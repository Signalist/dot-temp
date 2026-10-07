"""Strict data admission and deterministic, descriptive analysis. Stdlib only."""
import hashlib
import json
import math
import re
from pathlib import Path

SCHEMA = "w6-1"
ROLES = {"identification", "calibration", "confirmation", "ablation", "transfer"}


def read_json(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def read_lines(path):
    with Path(path).open() as stream:
        return [json.loads(line, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
                for line in stream if line.strip()]


def write_lines(path, values):
    with Path(path).open("x") as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def require(test, message):
    if not test:
        raise ValueError(message)


def timestamp(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_run(folder, purpose="descriptive"):
    """Fails closed; declarations are checked, not independently certified."""
    folder = Path(folder)
    m = read_json(folder / "manifest.json")
    p = read_lines(folder / "power.jsonl")
    events = read_lines(folder / "events.jsonl")
    for field in ("acquisition_id", "session_id", "run_id", "clock_id", "device_id_hash",
                  "model_revision", "engine_revision", "stratum", "baseline_method", "request_id", "model_family"):
        require(isinstance(m.get(field), str) and bool(m[field]), "missing " + field)
    require(m.get("schema_version") == SCHEMA, "schema_version")
    require(m.get("evidence") in {"SIMULATED", "MEASURED"}, "evidence label")
    require(m.get("stage") in ROLES, "stage")
    require(m.get("tier") in {"GPU_ONLY", "GPU_DC", "PCC"}, "tier")
    require(m.get("units") == {"time": "ns", "power": "W", "energy": "J", "work": "tokens"}, "units")
    require(isinstance(m.get("max_tokens"), int) and m["max_tokens"] > 0, "manifest max_tokens")
    require(m.get("concurrency") == 1, "isolated single request required")
    require(finite(m.get("max_gap_ns")) and m["max_gap_ns"] > 0, "max_gap_ns")
    require(finite(m.get("clock_error_ns")) and m["clock_error_ns"] >= 0, "clock_error_ns unknown")
    require(isinstance(m.get("channels"), dict) and m["channels"], "channels metadata")
    require(bool(p) and bool(events), "empty capture")
    channels = {}
    for row in p:
        for key in ("acquisition_id", "run_id", "clock_id", "evidence"):
            require(row.get(key) == m[key], "mixed provenance " + key)
        require(timestamp(row.get("t_ns")) and timestamp(row.get("arrival_ns")), "power time type")
        require(row["arrival_ns"] >= row["t_ns"] - m["clock_error_ns"], "arrival precedes sample beyond bound")
        require(row.get("status") == "ok", "bad/missing/saturated power record")
        require(finite(row.get("power_W")) and finite(row.get("baseline_W")), "power/baseline invalid")
        require(row["power_W"] >= 0 and row["baseline_W"] >= 0, "negative absolute electrical power")
        channel = row.get("channel")
        require(channel in m["channels"], "undeclared channel")
        channels.setdefault(channel, []).append(row)
    for channel, rows in channels.items():
        meta = m["channels"][channel]
        require(meta.get("boundary") and meta.get("source"), "missing channel boundary/source")
        require(all(b["t_ns"] > a["t_ns"] for a, b in zip(rows, rows[1:])), "duplicate/decreasing power time")
        require(all(b["t_ns"] - a["t_ns"] <= m["max_gap_ns"] for a, b in zip(rows, rows[1:])), "power gap")
        require(len(rows) >= 2, "insufficient samples")
    require(set(channels) == set(m["channels"]), "declared channel absent")
    by_type = {}
    last = -1
    progress = -1
    progress_time = -1
    for e in events:
        for key in ("acquisition_id", "run_id", "clock_id", "evidence"):
            require(e.get(key) == m[key], "mixed event provenance " + key)
        require(timestamp(e.get("t_ns")) and e["t_ns"] >= last, "decreasing event time")
        last = e["t_ns"]
        by_type.setdefault(e.get("type"), []).append(e)
        if e.get("type") in {"request_start", "progress", "eos_visible"}:
            require(e.get("request_id") == m["request_id"], "event request identity mismatch")
        if e.get("type") == "progress":
            require(e["t_ns"] > progress_time, "duplicate progress timestamp")
            progress_time = e["t_ns"]
            require(e.get("work_source") in {"engine_token_ids", "SIMULATED"}, "chunks are not tokens")
            require(isinstance(e.get("completed_tokens"), int) and not isinstance(e["completed_tokens"], bool)
                    and progress < e["completed_tokens"] <= m["max_tokens"], "nonincreasing/invalid useful progress")
            progress = e["completed_tokens"]
    mandatory = ("idle_before", "warmup_start", "warmup_end", "request_start", "eos_visible",
                 "power_return", "terminal_state", "capture_end")
    for kind in mandatory:
        require(len(by_type.get(kind, [])) == 1, "missing/duplicate " + kind)
    times = {kind: by_type[kind][0]["t_ns"] for kind in mandatory}
    require(all(times[b] > times[a] for a, b in zip(mandatory, mandatory[1:])), "phase ordering")
    for rows in channels.values():
        require(rows[0]["t_ns"] <= times["idle_before"] and rows[-1]["t_ns"] >= times["capture_end"], "incomplete capture window")
    eos = by_type["eos_visible"][0]
    require(eos.get("finish_reason") in {"stop", "length", "cancelled", "error", "timeout", "unknown"}, "finish_reason absent")
    require(eos.get("stop_class") in {"natural_eos", "stop_rule", "length", "cancelled", "error", "timeout", "unknown"}, "stop_class absent")
    require(eos.get("max_tokens") == m["max_tokens"], "EOS max_tokens differs from manifest")
    require(isinstance(eos.get("censored"), bool), "censoring absent")
    require(eos["censored"] or eos["stop_class"] == "natural_eos", "non-natural completion must remain censored")
    if eos["stop_class"] == "natural_eos":
        require(eos["finish_reason"] == "stop" and eos.get("eos_token_verified") is True
                and eos.get("stop_rules_disabled") is True, "natural EOS needs audited token and stop-rule evidence")
    for e in by_type.get("progress", []):
        require(times["request_start"] <= e["t_ns"] <= eos["t_ns"], "progress outside request")
    commands_path = folder / "commands.jsonl"
    completed_commands = []
    if commands_path.exists():
        for command in read_lines(commands_path):
            for key in ("acquisition_id", "run_id", "clock_id", "evidence"):
                require(command.get(key) == m[key], "mixed command provenance " + key)
            if command.get("type") == "cap_return":
                require(timestamp(command.get("issue_ns")) and timestamp(command.get("return_ns"))
                        and command["return_ns"] >= command["issue_ns"], "command time ordering")
                for field in ("requested_cap_W", "configured_cap_W", "enforced_cap_W"):
                    require(finite(command.get(field)) and command[field] > 0, "invalid cap channel " + field)
                require(command.get("status") == "ok", "command did not acknowledge")
                completed_commands.append(command)
    true_eos = eos.get("true_eos_ns")
    if true_eos is not None:
        require(timestamp(true_eos) and times["request_start"] < true_eos <= eos["t_ns"], "true EOS order")
        require(eos.get("true_eos_source") in {"device_completion_instrumented", "SIMULATED"}, "unsupported true EOS source")
        require(all(e["t_ns"] <= true_eos for e in by_type.get("progress", [])), "progress after true EOS; use acquisition-time events or retain as output availability")
    if m["evidence"] == "MEASURED":
        require(eos.get("true_eos_source") != "SIMULATED", "simulated EOS in measured run")
        require(all(e.get("work_source") != "SIMULATED" for e in events), "simulated progress in measured run")
    terminal = by_type["terminal_state"][0]
    require(terminal.get("criterion_id") and terminal.get("restored") is True, "terminal state unverified")
    require(finite(terminal.get("hold_ns")) and terminal["hold_ns"] > 0, "terminal hold absent")
    require(m.get("initial_state") == terminal.get("state") and bool(m.get("initial_state")), "state not restored")
    if purpose in {"w6-dc", "pcc"}:
        require(m["tier"] in {"GPU_DC", "PCC"} and "gpu_dc" in channels, "external GPU DC reference required")
        ref = m["channels"]["gpu_dc"]
        for key in ("rail_coverage", "calibration_id", "filter_description", "clock_transform_id"):
            require(bool(ref.get(key)), "DC metadata missing " + key)
        require(ref.get("all_required_rails") is True, "incomplete DC rails")
        for key in ("calibration_error_W", "filter_error_W", "baseline_error_W", "bandwidth_Hz"):
            require(finite(ref.get(key)) and ref[key] >= 0, "unknown DC uncertainty " + key)
        require(ref["bandwidth_Hz"] > 0, "zero bandwidth")
        require(true_eos is not None, "true EOS missing; client receipt is not device EOS")
        require(bool(by_type.get("progress")), "useful-progress events absent")
        require(m.get("progress_timing_audit_id"), "progress timing audit missing")
        allowed_timestamps = {"device_completion_aligned"} if m["evidence"] == "MEASURED" else {"device_completion_aligned", "SIMULATED"}
        require(all(e.get("timestamp_source") in allowed_timestamps
                    for e in by_type["progress"]), "host output observation or simulated timestamp is not measured device progress")
        require(m.get("intervention_audit_id") and m.get("fullcycle_audit_id"), "actuation/fullcycle audit absent")
        require(bool(completed_commands), "command acknowledgment log absent")
    if purpose == "pcc":
        require(m["tier"] == "PCC" and "pcc_active" in channels, "PCC channel required")
        pcc = m["channels"]["pcc_active"]
        for key in ("calibration_id", "filter_description", "clock_transform_id", "measurement_contract_id"):
            require(bool(pcc.get(key)), "PCC metadata missing " + key)
        for key in ("calibration_error_W", "filter_error_W", "baseline_error_W", "bandwidth_Hz"):
            require(finite(pcc.get(key)) and pcc[key] >= 0, "unknown PCC uncertainty " + key)
        require(pcc["bandwidth_Hz"] > 0, "PCC zero bandwidth")
        require(m.get("electrical_topology_id") and m.get("pcc_nuisance_audit_id"), "PCC topology/nuisance missing")
        require(m.get("grid_tail_certificate_id"), "full grid tail not bounded")
    require(purpose in {"descriptive", "w6-dc", "pcc"}, "unknown purpose")
    return m, channels, by_type


def integrate(rows, start, end, dynamic=False):
    require(end > start and rows[0]["t_ns"] <= start and rows[-1]["t_ns"] >= end, "energy window not bracketed")
    total = 0.0
    for a, b in zip(rows, rows[1:]):
        left, right = max(start, a["t_ns"]), min(end, b["t_ns"])
        if right <= left:
            continue
        pa = a["power_W"] - (a["baseline_W"] if dynamic else 0)
        pb = b["power_W"] - (b["baseline_W"] if dynamic else 0)
        span = b["t_ns"] - a["t_ns"]
        vl = pa + (pb-pa) * ((left-a["t_ns"])/span)
        vr = pa + (pb-pa) * ((right-a["t_ns"])/span)
        total += (right-left) * 1e-9 * (vl+vr)/2
    return total


def analyze_run(folder):
    m, channels, ev = validate_run(folder)
    start = ev["request_start"][0]["t_ns"]
    eos = ev["eos_visible"][0]
    stop = eos.get("true_eos_ns")
    end = ev["power_return"][0]["t_ns"]
    thermal = ev["terminal_state"][0]["t_ns"]
    out = {"evidence": m["evidence"], "run_id": m["run_id"], "tier": m["tier"],
           "status": "DESCRIPTIVE_ONLY_NO_PHYSICAL_CERTIFICATE", "energy": {},
           "power_cycle_s": (end-start)/1e9, "matched_state_cycle_s": (thermal-start)/1e9,
           "EOS_delay_s": None if stop is None else (eos["t_ns"]-stop)/1e9,
           "service_s": None if stop is None else (stop-start)/1e9,
           "recovery_s": None if stop is None else (end-stop)/1e9,
           "censored": eos["censored"], "stop_class": eos["stop_class"],
           "clock_error_ns": m["clock_error_ns"], "continuous_slew_bound": "NOT_IDENTIFIED"}
    for channel, rows in channels.items():
        slope = max(abs((b["power_W"]-a["power_W"])/((b["t_ns"]-a["t_ns"])/1e9)) for a, b in zip(rows, rows[1:]))
        out["energy"][channel] = {
            "gross_cycle_J": integrate(rows, start, end),
            "dynamic_cycle_J": integrate(rows, start, end, True),
            "dynamic_service_J": None if stop is None else integrate(rows, start, stop, True),
            "dynamic_recovery_J": None if stop is None else integrate(rows, stop, end, True),
            "gross_capture_J": integrate(rows, rows[0]["t_ns"], rows[-1]["t_ns"]),
            "gross_cooldown_J": integrate(rows, end, thermal),
            "max_sampled_slope_W_per_s_NOT_bound": slope,
            "negative_dynamic_samples_retained": sum(r["power_W"] < r["baseline_W"] for r in rows),
        }
    return out


def validate_registry(registry):
    require(registry.get("schema_version") == SCHEMA, "registry schema")
    require(registry.get("evidence") in {"MEASURED", "SIMULATED"}, "registry evidence")
    require(registry.get("declared_before_outcomes") is True, "prospective declaration required")
    require(isinstance(registry.get("runs"), list) and registry["runs"], "empty registry")
    require(registry.get("transfer_axis") in {"device", "model_family"}, "explicit transfer axis required")
    groups, runs = {}, set()
    for r in registry["runs"]:
        require(isinstance(r.get("run_id"), str) and re.fullmatch(r"run_[A-Za-z0-9_-]+", r["run_id"]), "unsafe run ID")
        require(r["stage"] in ROLES and r["run_id"] not in runs, "duplicate run/invalid stage")
        runs.add(r["run_id"])
        group = r["session_id"]
        require(groups.get(group, r["stage"]) == r["stage"], "session leakage across split")
        groups[group] = r["stage"]
        require(r.get("device_id_hash") and r.get("model_family"), "missing split device/family identity")
        protocol = r.get("analysis_protocol", {})
        require(isinstance(protocol.get("max_tokens"), int) and protocol["max_tokens"] > 0, "unfrozen max_tokens")
        for key in ("stratum", "model_revision", "engine_revision", "stop_rules_id"):
            require(bool(protocol.get(key)), "unfrozen protocol " + key)
        require(protocol.get("service_endpoint_rule") == "first_progress_at_or_after_offset", "unfrozen endpoint rule")
        require(timestamp(protocol.get("endpoint_lag_max_ns")), "unfrozen endpoint lag bound")
        windows = protocol.get("service_window_offsets_ns")
        require(isinstance(windows, list) and windows, "unfrozen service windows")
        previous = -1
        for window in windows:
            require(len(window) == 2 and all(timestamp(t) for t in window)
                    and previous <= window[0] < window[1], "invalid/overlapping frozen service window")
            previous = window[1]
    transfer = {r["device_model_unit"] for r in registry["runs"] if r["stage"] == "transfer"}
    training = {r["device_model_unit"] for r in registry["runs"] if r["stage"] != "transfer"}
    require(not transfer.intersection(training), "transfer unit leaked")
    axis = "device_id_hash" if registry["transfer_axis"] == "device" else "model_family"
    transfer_axis = {r[axis] for r in registry["runs"] if r["stage"] == "transfer"}
    train_axis = {r[axis] for r in registry["runs"] if r["stage"] != "transfer"}
    require(not transfer_axis.intersection(train_axis), "transfer axis leaked: " + axis)
    return groups


def freeze_split(registry_path, destination):
    registry = read_json(registry_path)
    groups = validate_registry(registry)
    out = {**registry, "registry_sha256": sha(registry_path), "groups": groups,
           "warning": "Hash records a declaration; cannot prove data were unseen. Archive the hash externally before acquisition."}
    with Path(destination).open("x") as f:
        json.dump(out, f, indent=2)
    return out
