"""Explicit opt-in acquisition; no model download, shell command, or credentials."""
import hashlib
from contextlib import contextmanager
import importlib.metadata
import json
import signal
import time
import urllib.parse
import urllib.request
from pathlib import Path
from .core import read_json, require, write_json


def identity(config):
    return {k: config[k] for k in ("acquisition_id", "run_id", "clock_id", "evidence")}


class EventSink:
    """One writer per file. Call at actual observation sites; never invent device EOS."""
    def __init__(self, path, config):
        self.file = Path(path).open("x", buffering=1)
        self.base = identity(config)

    def emit(self, event_type, **fields):
        row = {**self.base, "t_ns": time.monotonic_ns(), "type": event_type, **fields}
        self.file.write(json.dumps(row, allow_nan=False) + "\n")
        return row

    def close(self):
        self.file.close()


def nvml_open(index):
    try:
        import pynvml as n
    except ImportError as exc:
        raise RuntimeError("Install the pinned official nvidia-ml-py package in your own environment first") from exc
    n.nvmlInit()
    try:
        return n, n.nvmlDeviceGetHandleByIndex(index)
    except BaseException:
        n.nvmlShutdown()
        raise


def _string(value):
    return value.decode() if isinstance(value, bytes) else str(value)


def telemetry(config_path, output, execute=False):
    c = read_json(config_path)
    require(0.01 <= c["poll_s"] <= 10 and 0 < c["duration_s"] <= 3600, "bounded polling/duration required")
    if not execute:
        return {"mode": "DRY_RUN", "action": "read-only NVML", "GPU_calls": 0, "config": c}
    require(c["evidence"] == "MEASURED", "hardware requires MEASURED label")
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    n, handle = nvml_open(c["gpu_index"])
    stop = False
    old = {}
    def on_signal(_sig, _frame):
        nonlocal stop
        stop = True
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            old[sig] = signal.signal(sig, on_signal)
        uuid = _string(n.nvmlDeviceGetUUID(handle))
        inv = {"device_id_hash": hashlib.sha256(uuid.encode()).hexdigest(),
               "device_name": _string(n.nvmlDeviceGetName(handle)),
               "driver_version": _string(n.nvmlSystemGetDriverVersion()),
               "binding_version": importlib.metadata.version("nvidia-ml-py"),
               "clock_id": c["clock_id"], "wall_anchor_ns": time.time_ns(),
               "monotonic_anchor_ns": time.monotonic_ns(),
               "warning": "Host bracket is API timing, not physical sensor timestamp/filter accuracy."}
        write_json(out / "inventory.json", inv)
        start = time.monotonic()
        with (out / "telemetry.jsonl").open("x", buffering=1) as f:
            while not stop and time.monotonic()-start < c["duration_s"]:
                begin = time.monotonic_ns()
                row = {**identity(c), "channel": "nvml", "sensor_time_ns": None,
                       "baseline_W": None, "status": "ok", "errors": {}}
                getters = {"power_W": (n.nvmlDeviceGetPowerUsage, 0.001),
                           "energy_J": (n.nvmlDeviceGetTotalEnergyConsumption, 0.001),
                           "configured_cap_W": (n.nvmlDeviceGetPowerManagementLimit, 0.001),
                           "enforced_cap_W": (n.nvmlDeviceGetEnforcedPowerLimit, 0.001),
                           "temperature_C": (lambda h: n.nvmlDeviceGetTemperature(h, n.NVML_TEMPERATURE_GPU), 1),
                           "sm_clock_MHz": (lambda h: n.nvmlDeviceGetClockInfo(h, n.NVML_CLOCK_SM), 1)}
                for key, (fn, scale) in getters.items():
                    try:
                        row[key] = fn(handle) * scale
                    except n.NVMLError as exc:
                        row[key] = None
                        row["errors"][key] = type(exc).__name__
                end = time.monotonic_ns()
                row.update(t_ns=(begin+end)//2, query_begin_ns=begin, arrival_ns=end)
                if row["power_W"] is None:
                    row["status"] = "missing"
                f.write(json.dumps(row, allow_nan=False) + "\n")
                # Do not create a backlog of catch-up polls after delays.
                time.sleep(c["poll_s"])
        return {"mode": "MEASURED", "path": str(out), "aborted": stop,
                "admission": "RAW_ONLY; baseline, calibration, events and recovery still required"}
    finally:
        for sig, handler in old.items():
            signal.signal(sig, handler)
        n.nvmlShutdown()


@contextmanager
def absolute_deadline(seconds):
    """Linux main-thread wall deadline, including a stalled/slow-drip readline."""
    require(hasattr(signal, "setitimer"), "bounded request adapter requires Unix setitimer")
    require(signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0), "another alarm is active; refuse to replace it")
    previous = signal.getsignal(signal.SIGALRM)
    deadline = time.monotonic()+seconds
    def expired(_sig, _frame):
        raise TimeoutError("absolute request deadline exceeded")
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield deadline
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def completion_request(config_path, output, execute=False):
    c = read_json(config_path)
    parsed = urllib.parse.urlparse(c["url"])
    require(parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}, "adapter accepts local unauthenticated server only")
    require(not parsed.username and not parsed.password and not parsed.query and not parsed.fragment, "credentials/query rejected")
    require(parsed.path == "/v1/completions", "only /v1/completions adapter")
    require(isinstance(c["max_tokens"], int) and 1 <= c["max_tokens"] <= 4096, "bounded max_tokens")
    require(0 < c["timeout_s"] <= 600, "bounded timeout")
    if not execute:
        return {"mode": "DRY_RUN", "network_calls": 0, "server": c["url"], "model": c["model"], "prompt_path": c["prompt_file"]}
    require(c["evidence"] == "MEASURED", "request requires MEASURED label")
    prompt = Path(c["prompt_file"]).read_text()
    require(len(prompt.encode()) <= 1_000_000, "prompt file too large")
    payload = {"model": c["model"], "prompt": prompt, "max_tokens": c["max_tokens"],
               "temperature": c["temperature"], "stream": True, "n": 1,
               "stream_options": {"include_usage": True}}
    sink = EventSink(output, c)
    sink.emit("request_start", request_id=c["request_id"], max_tokens=c["max_tokens"],
              input_sha256=hashlib.sha256(prompt.encode()).hexdigest())
    final = False
    usage = None
    try:
        req = urllib.request.Request(c["url"], json.dumps(payload).encode(), {"Content-Type": "application/json"})
        # Disable proxies and redirects: prompts must stay at the explicitly named local server.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise RuntimeError("redirect refused")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        with absolute_deadline(c["timeout_s"]) as deadline:
            with opener.open(req, timeout=c["timeout_s"]) as response:
                while True:
                    require(time.monotonic() < deadline, "absolute request deadline exceeded")
                    raw = response.readline(8_000_001)
                    if not raw:
                        break
                    require(len(raw) <= 8_000_000, "SSE line too large")
                    if not raw.startswith(b"data:"):
                        continue
                    data = raw[5:].strip()
                    if data == b"[DONE]":
                        break
                    obj = json.loads(data)
                    if obj.get("usage"):
                        usage = obj["usage"].get("completion_tokens")
                    for choice in obj.get("choices", []):
                        require(choice.get("index", 0) == 0, "multi-sequence not supported")
                        text = choice.get("text", "")
                        if text:
                            sink.emit("chunk_received", request_id=c["request_id"], utf8_bytes=len(text.encode()),
                                      completed_tokens=None, work_source="client_text_chunk_NOT_tokens")
                        reason = choice.get("finish_reason")
                        if reason is not None:
                            require(not final, "duplicate terminal response")
                            final = True
                            known = reason if reason in {"stop", "length", "cancelled", "error"} else "unknown"
                            sink.emit("eos_visible", request_id=c["request_id"], finish_reason=known,
                                      stop_class="stop_rule" if known == "stop" else known,
                                      max_tokens=c["max_tokens"], censored=True,
                                      true_eos_ns=None, true_eos_source="unknown",
                                      availability_source="client_received_finish_reason")
        require(final, "stream ended without finish_reason; EOS right-censored")
        sink.emit("request_transport_end", completion_tokens=usage, token_count_source="server_usage" if usage is not None else "unknown")
        return {"status": "RAW_CLIENT_EVENTS_ONLY", "true_EOS": "UNKNOWN", "output": output}
    except Exception as exc:
        sink.emit("request_error", error_class=type(exc).__name__, censored=True)
        raise
    finally:
        sink.close()


def record_engine_progress(sink, request_id, cumulative_token_ids, phase, context_tokens, batch_size=1):
    """Invoke on audited engine output; timestamp is host observation, not GPU completion."""
    return sink.emit("progress", request_id=request_id, completed_tokens=len(cumulative_token_ids),
                     work_source="engine_token_ids", timestamp_source="host_engine_output_observation",
                     phase=phase, context_tokens=context_tokens, batch_size=batch_size)
