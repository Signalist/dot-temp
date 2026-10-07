"""Bounded OPTIONAL cap writes; never a power trajectory or slew controller."""
import hashlib
import signal
import time
from .acquire import EventSink, _string, nvml_open
from .core import finite, read_json, require


def validate_plan(c):
    require(c.get("operator_reviewed") is True, "operator_reviewed must be true")
    require(c.get("exclusive_device") is True and c.get("no_other_workloads") is True, "exclusive device required")
    require(len(c.get("levels", [])) in range(1, 21), "1..20 levels")
    require(finite(c["operator_min_W"]) and finite(c["operator_max_W"]) and 0 < c["operator_min_W"] <= c["operator_max_W"], "operator bounds")
    require(finite(c["max_temperature_C"]) and 0 < c["max_temperature_C"] < 95, "operator temperature threshold")
    require(c.get("expected_device_sha256") and len(c["expected_device_sha256"]) == 64, "device hash required")
    total = 0
    for level in c["levels"]:
        require(finite(level["cap_W"]) and c["operator_min_W"] <= level["cap_W"] <= c["operator_max_W"], "cap outside operator envelope")
        require(finite(level["hold_s"]) and 0 < level["hold_s"] <= 60, "hold 0..60s")
        total += level["hold_s"]
    require(total <= 600, "session >600s")


def run_cap_session(c, log, nvml_pair=None):
    """Dependency injection is for CPU fake tests only; CLI supplies real NVML after opt-in."""
    validate_plan(c)
    n, h = nvml_pair or nvml_open(c["gpu_index"])
    sink = None
    original = None
    attempted = False
    old_handlers = {}
    def interrupted(_sig, _frame):
        raise KeyboardInterrupt("operator stop")
    try:
        require(hashlib.sha256(_string(n.nvmlDeviceGetUUID(h)).encode()).hexdigest() == c["expected_device_sha256"], "device identity mismatch")
        lower, upper = n.nvmlDeviceGetPowerManagementLimitConstraints(h)
        original = n.nvmlDeviceGetPowerManagementLimit(h)
        for level in c["levels"]:
            requested = round(level["cap_W"]*1000)
            require(lower <= requested <= upper, "outside device-supported cap range")
            # Never exceed the initial setting. Restoring that setting is the only increase exception.
            require(requested <= original, "cap increase above initial setting prohibited")
        sink = EventSink(log, c)
        sink.emit("cap_session_start", original_cap_W=original/1000,
                  supported_min_W=lower/1000, supported_max_W=upper/1000)
        for sig in (signal.SIGINT, signal.SIGTERM):
            old_handlers[sig] = signal.signal(sig, interrupted)
        for level in c["levels"]:
            require(n.nvmlDeviceGetTemperature(h, n.NVML_TEMPERATURE_GPU) < c["max_temperature_C"], "temperature stop")
            requested = round(level["cap_W"]*1000)
            attempted = True  # Restore even if an API raises after changing the setting.
            issue = time.monotonic_ns()
            sink.emit("cap_issue", requested_cap_W=requested/1000, issue_ns=issue)
            n.nvmlDeviceSetPowerManagementLimit(h, requested)
            returned = time.monotonic_ns()
            observed = n.nvmlDeviceGetPowerManagementLimit(h)
            enforced = n.nvmlDeviceGetEnforcedPowerLimit(h)
            sink.emit("cap_return", issue_ns=issue, return_ns=returned,
                      requested_cap_W=requested/1000, configured_cap_W=observed/1000,
                      enforced_cap_W=enforced/1000, physical_effect_ns=None,
                      status="ok" if observed == requested else "mismatch")
            require(observed == requested, "cap readback mismatch")
            deadline = time.monotonic()+level["hold_s"]
            while time.monotonic() < deadline:
                require(n.nvmlDeviceGetTemperature(h, n.NVML_TEMPERATURE_GPU) < c["max_temperature_C"], "temperature stop")
                time.sleep(min(0.2, max(0, deadline-time.monotonic())))
        return {"status": "cap schedule returned; physical effect NOT inferred"}
    except BaseException as exc:
        if sink:
            sink.emit("cap_session_error", error_class=type(exc).__name__)
        raise
    finally:
        try:
            # Defer repeated Ctrl-C/termination during the short restoration attempt.
            for sig in old_handlers:
                signal.signal(sig, signal.SIG_IGN)
            if attempted and original is not None:
                try:
                    n.nvmlDeviceSetPowerManagementLimit(h, original)
                    restored = n.nvmlDeviceGetPowerManagementLimit(h)
                    require(restored == original, "RESTORE FAILED: operator intervention required")
                    if sink:
                        sink.emit("cap_restore", original_cap_W=original/1000, status="verified_readback")
                except BaseException:
                    if sink:
                        sink.emit("cap_restore", original_cap_W=original/1000, status="FAILED_OPERATOR_ACTION_REQUIRED")
                    raise
        finally:
            for sig, handler in old_handlers.items():
                signal.signal(sig, handler)
            if sink:
                sink.close()
            n.nvmlShutdown()


def cap_session(config_path, output, execute=False):
    c = read_json(config_path)
    if not execute:
        return {"mode": "DRY_RUN", "GPU_calls": 0, "cap_writes": 0,
                "warning": "Template values are placeholders; review before explicit opt-in", "plan": c}
    require(c.get("evidence") == "MEASURED", "hardware label")
    return run_cap_session(c, output)
