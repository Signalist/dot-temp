"""Read-only independent numerical audit of the frozen primary experiment.

This does not import run_contracts.py, recompile its backend, run a nonlinear
simulator, or modify any existing experiment artifact. Its sole output is
INDEPENDENT_AUDIT.json. Run with the existing round2 ANDES Python environment.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import ctypes
import hashlib
import json
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parents[1] / "round2_g6_joint_admission_20261003"
SEED = 921047
QS = np.array([[1, 1], [1, -1], [-1, -1], [-1, 1]])


def read_json(name):
    return json.loads((ROOT / name).read_text())


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def legal(word, budget):
    padded = np.pad(word, (7, 7))
    return bool(np.lib.stride_tricks.sliding_window_view(padded, 8).sum(-1).max() <= budget)


def main():
    started = datetime.now(timezone.utc).isoformat()
    report = {"audit_started_utc": started, "seed": SEED, "status": "PASS"}
    original_names = [
        "FROZEN_CONTRACT_PROTOCOL.json", "run_contracts.py", "window_dp.cpp",
        "window_dp.so", "SUMMARY.json", "VALIDATION.json", "SOURCE_PROVENANCE.json",
        "all_phase_support_arrays.npz", "contract_amplitude_brackets.csv",
        "maximizing_words.json", "maximizing_word_schedules.csv",
        "per_block_energy_work_ledger.csv", "phase_convergence.csv", "comparisons.csv",
    ]
    original_hashes = {name: sha(ROOT / name) for name in original_names}

    # Unlike the primary validation, exhaust every short length and every
    # integer mismatch budget, including startup words shorter than L.
    lib = ctypes.CDLL(str(ROOT / "window_dp.so"))
    ptr = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
    lib.window_dp.argtypes = [ptr, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ptr]
    rng = np.random.default_rng(SEED)
    cases = 0
    maximum_gap = 0.0
    for n in range(1, 14):
        words = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(int)
        padded = np.pad(words, ((0, 0), (7, 7)))
        max_window = np.lib.stride_tricks.sliding_window_view(padded, 8, axis=1).sum(-1).max(1)
        for budget in range(9):
            rewards = np.ascontiguousarray(rng.normal(size=(3, n)))
            actual = np.empty(3)
            lib.window_dp(rewards, 3, n, 8, budget, actual)
            expected = (rewards @ words[max_window <= budget].T).max(axis=1)
            gap = float(abs(actual - expected).max())
            assert gap < 1e-11, (n, budget, gap)
            maximum_gap = max(maximum_gap, gap)
            cases += 3
    report["exhaustive_short_word_checks"] = {
        "lengths": list(range(1, 14)), "L": 8,
        "budgets": list(range(9)), "random_reward_rows_per_case": 3,
        "cases": cases, "max_gap": maximum_gap,
        "constraints": "All length-8 windows after seven zero mismatch bits of padding on each end",
    }

    sources = read_json("SOURCE_PROVENANCE.json")
    hashes_checked = 0
    for source in sources:
        for path, expected in source["hashes"].items():
            assert sha(path) == expected, path
            hashes_checked += 1
    report["inherited_source_hashes_checked"] = hashes_checked

    witnesses = read_json("maximizing_words.json")
    with (ROOT / "maximizing_word_schedules.csv").open() as stream:
        schedules = list(csv.DictReader(stream))
    with (ROOT / "per_block_energy_work_ledger.csv").open() as stream:
        ledgers = list(csv.DictReader(stream))
    with (ROOT / "phase_convergence.csv").open() as stream:
        convergence = list(csv.DictReader(stream))
    schedule_by_id = {word["id"]: [] for word in witnesses}
    ledger_by_id = {word["id"]: [] for word in witnesses}
    for row in schedules:
        schedule_by_id[row["witness_id"]].append(row)
    for row in ledgers:
        ledger_by_id[row["witness_id"]].append(row)

    arrays = np.load(ROOT / "all_phase_support_arrays.npz")
    summary = read_json("SUMMARY.json")
    validation = read_json("VALIDATION.json")
    replay_checks = []
    bound_checks = []
    maximum_energy_residue = 0.0
    minimum_positive_compute = float("inf")
    for source, folder in [("positive", "positive_workpoint"), ("wecc", "transfer")]:
        data = np.load(OLD / folder / f"{source}_kernel.npz")
        bounds = np.load(OLD / folder / f"{source}_bound_components.npz")
        weights = np.load(OLD / folder / f"{source}_coefficients.npy", mmap_mode="r")
        lam, residues = data["lam"], data["R"]
        assert float(lam.real.max()) < 0

        # Reconstruct complete-block modal integral, infinite geometric tail,
        # and both global derivative bounds without importing primary code.
        integral = np.zeros((len(lam), 2), complex)
        for segment, q in enumerate(QS):
            end = (segment + 1) / 2
            integral += (np.exp(lam * (2 - end)) * np.expm1(lam / 2) / lam)[:, None] * q
        rr = np.exp(2 * lam.real)
        block_residues = residues * integral[None, :, :]
        tail = np.einsum("omi,m->oi", abs(block_residues), rr ** 256 / (1 - rr))
        tail_gap = float(abs(tail - bounds["tail"]).max())
        assert tail_gap < 1e-25
        abs_integral = -np.expm1(2 * lam.real) / (-lam.real)
        item = {"source": source, "spectral_max_real": float(lam.real.max()), "tail_max_gap": tail_gap}
        for order in (1, 2):
            global_bound = (
                (abs(residues * lam[None, :, None] ** order) * abs_integral[None, :, None]).sum(1)
                + (abs(block_residues * lam[None, :, None] ** order) / (1 - rr)[None, :, None]).sum(1)
                + abs((residues * lam[None, :, None] ** (order - 1)).sum(1))
            )
            gap = float(abs(global_bound - bounds[f"global_L{order}"]).max())
            assert gap < 1e-14
            item[f"global_L{order}_max_gap"] = gap
        bound_checks.append(item)

        if source == "positive":
            A, Bmat, C = data["A"], data["B"], data["C"]
            augmented = np.block([[A, Bmat], [np.zeros((2, A.shape[0] + 2))]])
            propagators = {}

        for word in [word for word in witnesses if word["source"] == source]:
            name = word["id"]
            mismatch = np.array(word["mismatch_chronological"])
            signs = np.array(word["common_sign_chronological"])
            amplitudes = np.array(word["unit_total_amplitude_port_values_chronological"])
            ray = abs(amplitudes[0])
            rho = word["exported_schedule_total_amplitude_MW"]
            phase = word["probe_phase_seconds"]
            output_index = word["probe_output_index"]
            baseline = np.array(word["physical_P0_MW"])
            assert legal(mismatch, word["B"]) and legal(mismatch[::-1], word["B"])
            assert np.array_equal(amplitudes[:, 0], signs * ray[0])
            assert np.array_equal(amplitudes[:, 1], signs * (1 - 2 * mismatch) * ray[1])
            assert len(schedule_by_id[name]) == 257 * 4
            assert len(ledger_by_id[name]) == 257 * 2
            if source == "positive":
                state = np.zeros(A.shape[0])
                minimum_positive_compute = min(minimum_positive_compute, float(np.min(baseline - rho * ray)))
            else:
                state = np.zeros((len(lam), 2), complex)

            for block in range(257):
                energy = np.zeros(2)
                for segment in range(4):
                    row = schedule_by_id[name][block * 4 + segment]
                    delta = np.array([float(row["deltaP1_MW"]), float(row["deltaP2_MW"])])
                    energy += 0.5 * delta
                    assert np.max(abs(delta - rho * amplitudes[block] * QS[segment])) < 1e-13
                    actual = np.array([float(row["P1_MW"]), float(row["P2_MW"])])
                    assert np.max(abs(actual - baseline - delta)) < 1e-13
                    assert float(row["start_seconds"]) == block * 2 + segment * 0.5
                    assert float(row["end_seconds"]) == block * 2 + (segment + 1) * 0.5
                    duration = 0.5 if block < 256 else float(np.clip(phase - segment * 0.5, 0, 0.5))
                    if duration > 0:
                        if source == "positive":
                            if duration not in propagators:
                                propagators[duration] = expm(augmented * duration)
                            matrix = propagators[duration]
                            state = matrix[:A.shape[0], :A.shape[0]] @ state + matrix[:A.shape[0], A.shape[0]:] @ delta
                        else:
                            state = np.exp(lam * duration)[:, None] * state + (np.expm1(lam * duration) / lam)[:, None] * delta
                maximum_energy_residue = max(maximum_energy_residue, float(abs(energy).max()))
                assert np.all(energy == 0)
                for port in range(2):
                    row = ledger_by_id[name][block * 2 + port]
                    assert int(row["block"]) == block and int(row["port"]) == port + 1
                    assert float(row["delta_energy_MW_s"]) == energy[port]
                    assert float(row["total_energy_MW_s"]) == 2 * baseline[port]
                    assert float(row["affine_work_wbar_coefficient"]) == 2
                    assert float(row["affine_work_kappa_coefficient"]) == 0

            actual_output = float(C[output_index] @ state) if source == "positive" else float(np.sum(residues[output_index] * state).real)
            gap = abs(actual_output - word["finite_linear_probe_output_Hz"])
            assert gap < 1e-8, (name, actual_output, gap)
            phase_index = round(phase * 2048 / 2)
            coefficient_output = float(np.sum(weights[output_index, phase_index].T * amplitudes[::-1]))
            assert abs(coefficient_output - word["DP_support_Hz_per_MW"]) < 1e-15
            assert abs(arrays[f'{source}_ray{word["ray_index"]}_B{word["B"]}'].max() - coefficient_output) < 1e-15
            replay_checks.append({
                "id": name, "linear_replay_Hz": actual_output,
                "claimed_probe_Hz": word["finite_linear_probe_output_Hz"],
                "absolute_gap_Hz": gap,
                "method": "51-state A/B/C augmented matrix exponential" if source == "positive" else "modal-state recurrence across schedule segments",
                "chronological_and_reversed_languages_valid": True,
            })

    for source in ["positive", "wecc"]:
        for ray_index in range(3):
            for budget in [0, 1, 2, 4, 8]:
                group = [row for row in convergence if row["source"] == source and int(row["ray_index"]) == ray_index and int(row["B"]) == budget]
                assert [int(row["phase_intervals"]) for row in group] == [256, 512, 1024, 2048]
                lower = np.array([float(row["peak_lower_Hz_per_MW"]) for row in group])
                upper = np.array([float(row["peak_upper_Hz_per_MW"]) for row in group])
                assert np.all(np.diff(lower) >= -1e-14)
                assert np.all(np.diff(upper) <= 1e-14)

    report.update({
        "words_checked": len(witnesses), "schedule_rows_checked": len(schedules),
        "ledger_rows_checked": len(ledgers), "max_complete_block_energy_residue_MW_s": maximum_energy_residue,
        "positive_minimum_actual_compute_MW": minimum_positive_compute,
        "linear_replays": replay_checks,
        "max_linear_replay_gap_Hz": max(item["absolute_gap_Hz"] for item in replay_checks),
        "reconstructed_bound_components": bound_checks,
        "all_30_actual_four_resolution_brackets_nested": True,
        "recorded_primary_LP_cases": len(validation["LP"]),
        "recorded_primary_LP_max_gap": max(item["absolute_gap"] for item in validation["LP"]),
        "recorded_primary_LP_max_integrality_gap": max(item["integrality_gap"] for item in validation["LP"]),
        "recorded_primary_inherited_endpoint_max_gap": max(item["gap"] for item in validation["inherited_endpoint_checks"]),
        "mathematical_review": [
            "The C++ target-state predecessors are the two possible old length-7 histories; popcount(parent)+newbit enforces the length-8 window. The zero start and arbitrary terminal state implement extendible startup/end words.",
            "Reversal preserves every contiguous-window count. For nonnegative mismatch variables, every shorter subwindow is contained in a full window when n>=L. For n<L a single total-count constraint suffices.",
            "The consecutive-ones window LP matrix is totally unimodular; adding 0/1 variable bounds and integer B gives the same finite binary-language optimum. This establishes same-information equivalence, not an optimization-method novelty claim.",
            "All startup prefixes are bounded by the full finite support: append zero mismatch blocks on the older end and freely choose their common signs, adding nonnegative absolute rewards. Every legal finite word extends forever with zero mismatch bits.",
            "The omitted modal tail begins after lag255, so the rr**256 geometric tail is correctly indexed. It is port-independent and remains valid for every mismatch restriction.",
            "The inherited refined derivative bound uses sampled sum-absolute derivatives, both one-sided derivatives at template switches, analytic second derivatives, and the derivative tail. Its proof applies to every fixed signed-amplitude word and hence to their maximum. Phase nodes include all switches and both block endpoints.",
            "The 514-second energy/work ledger includes completion of the current block after its frequency probe; the probe occurs earlier at 512+phase seconds. Exactly equal affine work is conditional on the specified affine work law and its nonnegativity condition.",
        ],
        "claim_limits": [
            "Conditional floating-point LTI numerical bounds only: no directed-rounding guarantee, model-error enclosure, arbitrary initial-state guarantee, or new nonlinear validation.",
            "Retain previous voltage-qualification failures and WECC nonlinear frequency failure. Positive baseline nonnegativity alone does not establish operational hosting capability.",
            "WECC uses zero-baseline signed incremental ports, so its nonzero amplitudes are not physical nonnegative compute demand.",
            "Overlapping B=4 and independent-port brackets justify no resolved benefit, not exact continuous-time capacity equality or language equality.",
            "The asymptotic-average-only comparator equals unrestricted finite-prefix worst case only when arbitrary finite mismatch bursts are allowed, including before an eventual zero-mismatch tail; it is distinct from a bound enforced on every finite prefix.",
            "The C++ fixed array capacity supports at most 128 history states; L>8 can exceed it. Only L=8 was independently validated here. Other lengths require their own checks, and the target-state low-bit representation needs special handling at L=1.",
            "Refined derivative sampling was reviewed in the inherited source and its analytic global bounds reconstructed; this audit does not independently regenerate the full 2049-phase derivative sampling pass.",
        ],
        "new_nonlinear_integrations": 0,
        "scope": "Frozen primary 30 source/ray/B cases only; subsequent secondary ablations are not covered",
        "artifact_hashes_at_audit": original_hashes,
    })
    for name, expected in original_hashes.items():
        assert sha(ROOT / name) == expected, f"Original artifact changed during audit: {name}"
    report["existing_artifacts_unchanged_during_audit"] = True
    report["audit_completed_utc"] = datetime.now(timezone.utc).isoformat()
    (ROOT / "INDEPENDENT_AUDIT.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: report[key] for key in ["status", "words_checked", "schedule_rows_checked", "ledger_rows_checked", "max_linear_replay_gap_Hz", "existing_artifacts_unchanged_during_audit"]}))


if __name__ == "__main__":
    main()
