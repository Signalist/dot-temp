"""Creates synthetic fixtures only. Never imports NVML or sends workload requests."""
from pathlib import Path
from .core import SCHEMA, analyze_run, freeze_split, validate_run, write_json, write_lines
from .analysis import fit_service, evaluate_service


def make_run(root, index, stage, level):
    run_id = f"run_{index:02d}"
    folder = Path(root) / run_id
    folder.mkdir()
    base = {"evidence": "SIMULATED", "acquisition_id": "sim_"+run_id,
            "run_id": run_id, "clock_id": "SIMULATED_CLOCK"}
    state = {"temperature_C": 40, "queue": 0, "clock_state": "SIMULATED_IDLE"}
    m = {**base, "schema_version": SCHEMA, "session_id": f"sim_session_{index:02d}",
         "stage": stage, "tier": "GPU_DC", "request_id": "req_"+run_id, "max_tokens": 4096, "device_id_hash": "SIMULATED_OTHER_GPU" if stage == "transfer" else "SIMULATED_GPU", "model_family": "SIMULATED_MODEL_FAMILY",
         "device_model_unit": "SIM_OTHER_DEVICE_MODEL" if stage == "transfer" else "SIM_DEVICE_MODEL",
         "model_revision": "SIMULATED_MODEL", "engine_revision": "SIMULATED_ENGINE",
         "stratum": "decode_context128_batch1" if stage != "transfer" else "decode_context256_batch1",
         "units": {"time": "ns", "power": "W", "energy": "J", "work": "tokens"},
         "concurrency": 1, "clock_error_ns": 1000, "max_gap_ns": 110_000_000,
         "baseline_method": "SIMULATED constant 40 W; not measured",
         "progress_timing_audit_id": "SIMULATED", "intervention_audit_id": "SIMULATED", "fullcycle_audit_id": "SIMULATED",
         "initial_state": state, "service_endpoint_rule": "first_progress_at_or_after_offset", "endpoint_lag_max_ns": 250_000_000, "service_window_offsets_ns": [[1_000_000_000, 3_000_000_000]], "stop_rules_id": "SIM_NO_STOP_RULES",
         "channels": {"gpu_dc": {"boundary": "SIMULATED all GPU DC rails", "source": "SIMULATED",
                       "rail_coverage": "SIMULATED", "all_required_rails": True,
                       "calibration_id": "SIMULATED", "filter_description": "SIMULATED exact",
                       "clock_transform_id": "SIMULATED identity", "calibration_error_W": 0,
                       "filter_error_W": 0, "baseline_error_W": 0, "bandwidth_Hz": 1000}}}
    events = []
    def e(t, kind, **kw):
        events.append({**base, "t_ns": round(t*1e9), "type": kind, **kw})
    e(0, "idle_before")
    e(1, "warmup_start")
    e(2, "warmup_end")
    e(3, "request_start", request_id="req_"+run_id)
    rate = 10*int(level**0.5)
    for tick in range(31, 71):
        e(tick/10, "progress", request_id="req_"+run_id,
          completed_tokens=(tick-30)*rate//10, work_source="SIMULATED", timestamp_source="SIMULATED", phase="decode",
          context_tokens=128, batch_size=1)
    e(7.02, "eos_visible", request_id="req_"+run_id, finish_reason="stop", stop_class="natural_eos", censored=False,
      max_tokens=4096, eos_token_verified=True, stop_rules_disabled=True, true_eos_ns=7_000_000_000, true_eos_source="SIMULATED")
    e(9, "power_return")
    e(11, "terminal_state", criterion_id="SIMULATED_IDLE_AND_THERMAL", restored=True,
      hold_ns=1_000_000_000, state=state)
    e(12, "capture_end")
    rows = []
    for tick in range(121):
        t = tick/10
        if 1 <= t <= 2:
            dynamic = 10
        elif 3 <= t <= 7:
            dynamic = level
        elif 7 < t < 9:
            dynamic = level*(9-t)/2
        else:
            dynamic = 0
        rows.append({**base, "t_ns": tick*100_000_000, "arrival_ns": tick*100_000_000+1000,
                     "channel": "gpu_dc", "power_W": 40+dynamic, "baseline_W": 40,
                     "status": "ok"})
    write_json(folder/"manifest.json", m)
    write_lines(folder/"events.jsonl", sorted(events, key=lambda r: r["t_ns"]))
    write_lines(folder/"power.jsonl", rows)
    write_lines(folder/"commands.jsonl", [{**base, "type": "cap_return", "issue_ns": 2_900_000_000,
        "return_ns": 2_900_100_000, "requested_cap_W": 40+level+20,
        "configured_cap_W": 40+level+20, "enforced_cap_W": 40+level+20,
        "physical_effect_ns": None, "status": "ok"}])
    return {"run_id": run_id, "session_id": m["session_id"], "stage": stage,
            "device_model_unit": m["device_model_unit"]}


def demo(output):
    root = Path(output)
    root.mkdir(parents=True, exist_ok=False)
    roles = [("identification", 25), ("identification", 36), ("identification", 49),
             ("calibration", 64), ("confirmation", 36), ("confirmation", 49),
             ("ablation", 25), ("transfer", 49)]
    # Synthetic split declaration is made before synthetic outcome generation.
    registry = {"schema_version": SCHEMA, "evidence": "SIMULATED", "declared_before_outcomes": True, "transfer_axis": "device",
                "runs": [{"run_id": f"run_{i:02d}", "session_id": f"sim_session_{i:02d}",
                          "stage": stage, "device_model_unit": "SIM_OTHER_DEVICE_MODEL" if stage == "transfer" else "SIM_DEVICE_MODEL",
                          "device_id_hash": "SIMULATED_OTHER_GPU" if stage == "transfer" else "SIMULATED_GPU",
                          "model_family": "SIMULATED_MODEL_FAMILY",
                          "analysis_protocol": {"max_tokens": 4096, "stratum": "decode_context256_batch1" if stage == "transfer" else "decode_context128_batch1",
                                                "model_revision": "SIMULATED_MODEL", "engine_revision": "SIMULATED_ENGINE",
                                                "stop_rules_id": "SIM_NO_STOP_RULES",
                                                "service_endpoint_rule": "first_progress_at_or_after_offset", "endpoint_lag_max_ns": 250_000_000, "service_window_offsets_ns": [[1_000_000_000, 3_000_000_000]]}}
                         for i, (stage, _) in enumerate(roles)]}
    write_json(root/"registry.json", registry)
    freeze_split(root/"registry.json", root/"frozen_split.json")
    results = []
    for i, (stage, level) in enumerate(roles):
        make_run(root, i, stage, level)
        folder = root/f"run_{i:02d}"
        validate_run(folder, "w6-dc")
        results.append(analyze_run(folder))
    write_json(root/"analysis.json", results)
    fit_service(root, root/"frozen_split.json", root/"frozen_service_model.json")
    evaluate_service(root, root/"frozen_split.json", root/"frozen_service_model.json", root/"evaluation.json")
    summary = {"evidence": "SIMULATED", "synthetic_runs": len(roles), "hardware_runs": 0,
               "validation": "schema, alignment, energy, split, service-fit and frozen-evaluation plumbing completed",
               "warning": "Fixture size is a software test, not the 30-episode physical pilot or a confirmation sample budget."}
    write_json(root/"SUMMARY.json", summary)
    return summary
