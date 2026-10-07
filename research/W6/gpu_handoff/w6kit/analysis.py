"""Instrument CSV adapter, prospective split checks and deliberately modest service fit."""
import csv
import math
from decimal import Decimal
from pathlib import Path
from .core import (finite, read_json, require, sha, validate_run,
                   integrate, write_json, write_lines, validate_registry)


def import_meter(csv_path, spec_path, output):
    s = read_json(spec_path)
    require(s["channel"] in {"gpu_dc", "pcc_active"}, "unknown meter channel")
    require(s["clock_transform_id"] and s["calibration_id"], "audited clock/calibration IDs required")
    for k in ("sync_before_id", "sync_after_id", "source_clock_id", "clock_id", "boundary"):
        require(bool(s.get(k)), "missing " + k)
    require(finite(s["clock_error_ns"]) and s["clock_error_ns"] >= 0, "clock bound unknown")
    require(finite(s["slope"]) and s["slope"] > 0, "invalid clock slope")
    require(finite(s["power_scale_to_W"]) and s["power_scale_to_W"] > 0, "power gain")
    require(finite(s["baseline_W"]), "explicit baseline required")
    rows = []
    last = -1
    with Path(csv_path).open() as stream:
        for r in csv.DictReader(stream):
            source = Decimal(r["sensor_timestamp"])
            mapped = source * Decimal(str(s["time_scale_to_ns"])) * Decimal(str(s["slope"])) + Decimal(str(s["offset_ns"]))
            t = int(mapped.to_integral_value())
            require(t > last and t >= 0, "meter time duplicate/reset; split acquisition, do not sort")
            last = t
            power = float(r["power"]) * s["power_scale_to_W"]
            require(finite(power), "nonfinite power")
            rows.append({k: s[k] for k in ("acquisition_id", "run_id", "clock_id", "evidence")})
            rows[-1].update(t_ns=t, source_timestamp=r["sensor_timestamp"],
                            arrival_ns=int(r["arrival_monotonic_ns"]), channel=s["channel"],
                            power_W=power, baseline_W=s["baseline_W"], status=r["status"])
    require(bool(rows), "empty meter CSV")
    write_lines(output, rows)
    return {"rows": len(rows), "source_sha256": sha(csv_path), "spec_sha256": sha(spec_path),
            "warning": "No correlation-based alignment. Transform is supplied, not certified by this importer."}


def admitted_windows(folder, split):
    m, channels, events = validate_run(folder, "w6-dc")
    require(m["run_id"] == Path(folder).name, "manifest run identity differs from registered directory")
    validate_registry(split)
    require(m["evidence"] == split["evidence"], "split evidence mismatch")
    registry = {r["run_id"]: r for r in split["runs"]}
    require(m["run_id"] in registry, "run absent from frozen split")
    r = registry[m["run_id"]]
    require(r["session_id"] == m["session_id"] and r["stage"] == m["stage"], "split mismatch")
    require(r["device_model_unit"] == m["device_model_unit"], "device/model split mismatch")
    require(r["device_id_hash"] == m["device_id_hash"] and r["model_family"] == m["model_family"], "physical device/model family mismatch")
    for key, value in r["analysis_protocol"].items():
        require(m.get(key) == value, "manifest differs from frozen analysis protocol: " + key)
    points = []
    prog = {p["t_ns"]: p["completed_tokens"] for p in events["progress"]}
    eos = events["eos_visible"][0]["true_eos_ns"]
    for window in m.get("service_window_offsets_ns", []):
        selected = []
        for offset in window:
            target = offset+events["request_start"][0]["t_ns"]
            candidates = [t for t in prog if target <= t <= target+m["endpoint_lag_max_ns"]]
            require(bool(candidates), "no progress endpoint within frozen lag bound")
            selected.append(min(candidates))
        a, b = selected
        require(a < b, "bracketed service window collapsed")
        require(events["request_start"][0]["t_ns"] <= a < b <= eos, "service window outside useful work")
        dt = (b-a)/1e9
        require(b-a > 2*m["clock_error_ns"], "service window too short for timing error")
        delta = prog[b]-prog[a]
        require(delta >= 0, "decreasing count")
        mean_p = integrate(channels["gpu_dc"], a, b, True)/dt
        points.append({"run_id": m["run_id"], "session_id": m["session_id"],
                       "stage": m["stage"], "stratum": m["stratum"], "actual_dynamic_mean_W": mean_p,
                       "interval_rate_tokens_s": delta/dt,
                       "rate_clock_only_lower": delta/(dt+2*m["clock_error_ns"]/1e9),
                       "rate_clock_only_upper": delta/(dt-2*m["clock_error_ns"]/1e9)})
    require(bool(points), "no predeclared service windows")
    return m, points


def selected_folders(root, split, stages):
    validate_registry(split)
    expected = [r for r in split["runs"] if r["stage"] in stages]
    require(expected, "no preregistered runs for selected stages")
    known = {r["run_id"] for r in split["runs"]}
    require(all(p.name in known for p in Path(root).glob("run_*") if p.is_dir()), "unregistered run directory")
    for r in expected:
        folder = Path(root)/r["run_id"]
        require(folder.is_dir(), "missing preregistered run: " + r["run_id"])
        yield folder


def fit_service(root, split_path, output):
    split = read_json(split_path)
    points, inputs, strata, labels = [], {}, set(), set()
    for folder in selected_folders(root, split, {"identification", "calibration"}):
        # Confirmation outcomes are never opened by fitting.
        m, rows = admitted_windows(folder, split)
        points.extend(rows)
        strata.add(m["stratum"])
        labels.add(m["evidence"])
        inputs[str(folder.name)] = {name: sha(folder / name) for name in ("manifest.json", "power.jsonl", "events.jsonl")}
    require(len(strata) == 1 and len(labels) == 1, "do not pool strata or simulation with measurements")
    require(len(points) >= 3, "too few identification points")
    xs = [p["actual_dynamic_mean_W"] for p in points]
    ys = [p["interval_rate_tokens_s"] for p in points]
    require(len(set(xs)) >= 3, "fewer than 3 attained power levels")
    xbar, ybar = sum(xs)/len(xs), sum(ys)/len(ys)
    denom = sum((x-xbar)**2 for x in xs)
    b = sum((x-xbar)*(y-ybar) for x, y in zip(xs, ys))/denom
    a = ybar-b*xbar
    grouped = {}
    for x, y in zip(xs, ys):
        grouped.setdefault(x, []).append(y)
    ordered = sorted((x, sum(v)/len(v)) for x, v in grouped.items())
    slopes = [(y1-y0)/(x1-x0) for (x0, y0), (x1, y1) in zip(ordered, ordered[1:])]
    out = {"evidence": labels.pop(), "model": "diagnostic_OLS_rate=a+b*interval_actual_dynamic_power",
           "a": a, "b": b, "stratum": strata.pop(), "domain_W": [min(xs), max(xs)],
           "points": points, "source_sha256": inputs, "split_sha256": sha(split_path),
           "empirical_nondecreasing_means": all(x >= 0 for x in slopes),
           "empirical_concave_secants": all(a >= b for a, b in zip(slopes, slopes[1:])),
           "residual_max_abs_tokens_s": max(abs(y-(a+b*x)) for x, y in zip(xs, ys)),
           "claims": "Point estimate only; interval means do not identify pointwise causal s(p), hard envelopes, concavity, or independence."}
    require(not Path(output).exists(), "model output already exists: do not overwrite a frozen fit")
    write_json(output, out)
    return out


def evaluate_service(root, split_path, model_path, output):
    model, split = read_json(model_path), read_json(split_path)
    require(model["split_sha256"] == sha(split_path), "split changed after fit")
    rows = []
    for folder in selected_folders(root, split, {"confirmation", "ablation", "transfer"}):
        m, points = admitted_windows(folder, split)
        require(m["evidence"] == model["evidence"], "simulation/measurement mixing")
        for p in points:
            x = p["actual_dynamic_mean_W"]
            predicted = model["a"]+model["b"]*x
            rows.append({**p, "prediction": predicted,
                         "residual_tokens_s": p["interval_rate_tokens_s"]-predicted,
                         "in_calibration_stratum": m["stratum"] == model["stratum"],
                         "in_calibration_power_domain": model["domain_W"][0] <= x <= model["domain_W"][1]})
    require(rows, "no test runs")
    out = {"evidence": model["evidence"], "frozen_model_sha256": sha(model_path), "rows": rows,
           "warning": "No refitting; diagnostic residuals only. No safety or inferential pass threshold was specified."}
    require(not Path(output).exists(), "evaluation exists; preserve original")
    write_json(output, out)
    return out


def failure_budget(alpha, delta, endpoints=1):
    require(0 < alpha < 1 and 0 < delta < 1 and isinstance(endpoints, int) and endpoints >= 1, "probability args")
    return {"n_zero_failure_iid_units": math.ceil(math.log(delta/endpoints)/math.log(1-alpha)),
            "alpha": alpha, "delta_total": delta, "endpoints": endpoints,
            "premise": "Prespecified endpoints, iid independent acquisitions; rows/tokens are not independent units. No physical guarantee."}
