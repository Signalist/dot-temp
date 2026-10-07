"""Frozen Gate 1 physical-model driver. Importing this file runs no trajectory.

Run exactly one declared condition at a time, only after the separate interface
review. C0-slow and C0-fast must be reported before the fault conditions. Existing
runs are never overwritten. A same-condition 5 us numerical refinement requires
its completed primary record to show a hard contact or near-boundary interval.

The controller gets scalar physical parameters and the current source level for
measurement formation only. Event schedules, references, future observations,
and scoring states remain in this driver. No optimizer restart or tuning lives
here. The seven original physical/passive states plus six new quadratures form
the unchanged 13-dimensional augmented plant.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback

# Set before importing NumPy/SciPy, rather than merely documenting the setting.
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'gate_a'))
from dq_bench import battery_draw, controller, rhs, signals
from dq_preconditioned import normstate, serial_ctl

PROTOCOL = ROOT / 'protocol/GATE1_MPSC_SIX_MODELS_V1.json'
EXPECTED_PROTOCOL_SHA256 = 'be681761f993c6beaefaca0a54ece73dc2e3263d56b5b7f869ab476e87c96fa3'
OUTPUT = HERE / 'results'
STATE_NAMES = ['id', 'iq', 'Wdc', 'Pb', 'deltaEb', 'intPsource', 'intLoss',
               'intPpcc', 'intQpcc', 'intPb', 'intBatteryDraw',
               'int_abs_P_error', 'int_abs_Q_error']
COLS = ['t', *STATE_NAMES, 'Ipu', 'Vdcpu', 'Ppcc', 'Qpcc', 'Vpccpu',
        'Pinv', 'Psource', 'WL', 'energy_residual', 'soc', 'Vs', 'PLL_Hz']
CI = {s: k for k, s in enumerate(COLS)}
CONTROL_COLS = ['t', 'Irefpu', 'voltage_sat_factor', 'PLL_Hz', 'Pb_cmd',
                'ip_ref', 'iq_ref', 'mnorm', 'current_ref_clipped',
                'voltage_clipped', 'source_cmd_clipped', 'PLL_clipped',
                'guard_intervened', 'guard_modification_norm']
INTERVAL_COLS = ['start', 'end', 'Imax', 'Vdcmin', 'Vdcmax', 'Smax',
                 'P_absmax', 'Pb_absmax', 'socmin', 'socmax',
                 'frequency_error_max', 'energy_residual_max',
                 'current_ref_clip', 'voltage_clip', 'source_cmd_clip',
                 'PLL_clip', 'guard_intervened', 'modulation_max']
NORMALIZED_NAMES = ['t', 'id_over_Ibase', 'iq_over_Ibase', 'Wdc_over_Wnom',
                    'Pb_over_1MW', 'PLL_phase_minus_nominal_phase',
                    'zpll_over_omega0', 'zi_d_over_Vbase', 'zi_q_over_Vbase',
                    'applied_d', 'applied_q', 'queued_d', 'queued_q',
                    'omega_over_omega0', 'pb_command_over_1MW']
HARD_NAMES = ['actual_current', 'actual_current_emergency', 'dc_low', 'dc_high',
              'soc_low', 'soc_high', 'AC_P_positive', 'AC_P_negative', 'AC_S',
              'Pb_positive', 'Pb_negative']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def jsonable(value):
    """Lossless complex serialization; nonfinite diagnostics are explicit strings."""
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, (complex, np.complexfloating)):
        return [jsonable(value.real), jsonable(value.imag)]
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return 'NaN' if math.isnan(value) else ('+Infinity' if value > 0 else '-Infinity')
    if isinstance(value, Path):
        return str(value)
    return value


def dump(path, data):
    Path(path).write_text(json.dumps(jsonable(data), ensure_ascii=False,
                                    indent=2, allow_nan=False) + '\n')


def load_design(case_id):
    if sha(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError('Frozen six-model protocol changed; no trajectory was started')
    f = json.loads(PROTOCOL.read_text())
    gpath = ROOT / f['base_Gate0_design']
    if sha(gpath) != f['base_Gate0_design_sha256']:
        raise RuntimeError('Frozen Gate 0 design hash mismatch')
    g = json.loads(gpath.read_text())
    ppath, cppath = ROOT / g['base_protocol'], ROOT / f['initial_checkpoint']
    if sha(ppath) != g['base_sha256'] or sha(cppath) != g['checkpoint_sha256']:
        raise RuntimeError('Frozen physical protocol/checkpoint hash mismatch')
    case = next((c for c in f['execution_order'] if c['id'] == case_id), None)
    if case is None:
        raise ValueError('Only the six frozen case IDs are permitted')
    full_d = json.loads(ppath.read_text())
    # A numeric whitelist strips case/event metadata before the guard sees D.
    d = {k: v for k, v in full_d.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    port = f['ports'][case['port']]
    d.update(battery_source_tau_s=port['tau_s'],
             battery_source_ramp_up_W_per_s=port['ramp_W_per_s'],
             battery_source_ramp_down_W_per_s=port['ramp_W_per_s'])
    cp = json.loads(cppath.read_text())
    if cp['time_s'] != .6 or len(cp['plant_state']) != 7 or d['control_sample_s'] != 1e-4:
        raise RuntimeError('Frozen state or sample-clock contract does not match')
    return f, g, case, d, full_d, cp


def tag_for(case_id, h):
    return f'{case_id}_h{h:g}'


def check_run_admission(f, case, h):
    """No implicit suite, no silent repeated physical condition, no failed-port fault."""
    if h not in (1e-5, 5e-6):
        raise ValueError('Only frozen 10 us primary and conditional 5 us refinement allowed')
    tag = tag_for(case['id'], h)
    if any(OUTPUT.glob(tag + '.*')):
        raise RuntimeError(f'{tag} already has evidence; refusing to overwrite or retry')
    ids = [c['id'] for c in f['execution_order']]
    if case['id'] == 'C0-fast' and not (OUTPUT / (tag_for('C0-slow', 1e-5) + '.json')).exists():
        raise RuntimeError('C0-slow must be run and recorded first')
    if case['event'] is not None:
        # Both no-fault cases are reviewed before any fault. The explicit one-case
        # invocation remains the caller\'s stage choice; no fault is auto-launched.
        for cid in ids[:2]:
            p = OUTPUT / (tag_for(cid, 1e-5) + '.json')
            if not p.exists():
                raise RuntimeError('Both C0 records are required before fault execution')
        ref = json.loads((OUTPUT / (tag_for('C0-' + case['port'], 1e-5) + '.json')).read_text())
        if ref.get('no_fault_physical_admission') is not True:
            raise RuntimeError('NOT_RUN_PENDING_REVIEW: this port failed C0 physical/guard admission')
        # Enforce declared ordering for earlier cases whose ports are admitted.
        for previous in f['execution_order'][2:ids.index(case['id'])]:
            rp = OUTPUT / (tag_for('C0-' + previous['port'], 1e-5) + '.json')
            admitted = json.loads(rp.read_text()).get('no_fault_physical_admission') is True
            if admitted and not (OUTPUT / (tag_for(previous['id'], 1e-5) + '.json')).exists():
                raise RuntimeError(f"Frozen execution order requires {previous['id']} first")
    if h == 5e-6:
        primary = OUTPUT / (tag_for(case['id'], 1e-5) + '.json')
        if not primary.exists():
            raise RuntimeError('Refinement requires the same-condition primary result')
        result = json.loads(primary.read_text())
        if not result.get('numerical_refinement_indicated', False):
            raise RuntimeError('No hard-contact/near-boundary reason for a 5 us refinement')


def service(y0, y1, duration):
    d = np.asarray(y1) - np.asarray(y0)
    if duration <= 0:
        means = {'mean_P_W': None, 'mean_Q_var': None,
                 'mean_absolute_P_error_W': None, 'mean_absolute_Q_error_var': None}
    else:
        means = dict(mean_P_W=float(d[7] / duration), mean_Q_var=float(d[8] / duration),
                     mean_absolute_P_error_W=float(d[11] / duration),
                     mean_absolute_Q_error_var=float(d[12] / duration))
    return dict(duration_s=float(duration), P_actual_integral_J=float(d[7]),
                Q_actual_integral_var_s=float(d[8]),
                P_signed_request_error_integral_J=float(d[7] - 800000 * duration),
                Q_signed_request_error_integral_var_s=float(d[8] - 700000 * duration),
                P_absolute_request_error_integral_J=float(d[11]),
                Q_absolute_request_error_integral_var_s=float(d[12]), **means)


def inventory(y0, y1, d):
    ebase = d['battery_energy_MWh'] * 3.6e9
    wl = lambda y: .75 * (d['filter_L_H'] + d['grid_L_H']) * (y[0]**2 + y[1]**2)
    return dict(initial_soc=d['soc_initial'] + y0[4] / ebase,
                final_soc=d['soc_initial'] + y1[4] / ebase,
                battery_stored_energy_change_J=y1[4] - y0[4],
                DC_energy_change_J=y1[2] - y0[2],
                RL_energy_change_J=wl(y1) - wl(y0),
                remote_source_active_integral_J=y1[5] - y0[5],
                total_loss_integral_J=y1[6] - y0[6],
                battery_terminal_power_integral_J=y1[9] - y0[9],
                battery_draw_integral_J=y1[10] - y0[10],
                initial_Pb_W=y0[3], final_Pb_W=y1[3],
                battery_energy_restoration_claimed=False)


def energy_necessary_condition(onset, event, d):
    """Same short-time necessary inequality, recalculated from this actual onset.

    This relaxed linear slew envelope grants arbitrary source control; it is an
    outer obstruction, not a prediction. Its positive-source branch is used
    only up to Pb0/Rdown, exactly as in the historical 17.088 ms calculation.
    """
    if onset is None:
        return {'status': 'UNOBSERVED', 'first_headroom_equality_after_fault_s': None}
    y = np.asarray(onset['plant_state'], dtype=float)
    ib, vb = d['I_phase_peak_base_A'], d['V_phase_peak_base_V']
    lt, rt = d['filter_L_H'] + d['grid_L_H'], d['filter_R_ohm'] + d['grid_R_ohm']
    wl = .75 * lt * (y[0]**2 + y[1]**2)
    wlmax = .75 * lt * ib**2
    wmax = .5 * d['C_dc_F'] * (d['V_dc_max_pu'] * d['V_dc_initial_V'])**2
    pexit = 1.5 * vb * event['retained_source_pu'] * ib + d['inverter_loss_constant_W'] \
        + d['inverter_loss_current_squared_W_at_1pu'] + 1.5 * rt * ib**2
    headroom = wmax + wlmax - y[2] - wl
    a = d['eta_dc_dc'] * y[3] - pexit
    b = d['eta_dc_dc'] * d['battery_source_ramp_down_W_per_s']
    horizon = min(event['end_s'] - event['start_s'], max(0., y[3] / d['battery_source_ramp_down_W_per_s']))
    peak = min(horizon, max(0., a / b))
    gain = lambda t: a*t - .5*b*t*t
    crossing = None
    if headroom <= 0:
        crossing = 0.
    elif peak > 0 and gain(peak) >= headroom:
        crossing = brentq(lambda t: gain(t) - headroom, 0., peak, xtol=1e-14)
    return dict(status='RECOMPUTED_FROM_ACTUAL_ONSET', onset_time_s=event['start_s'],
                onset_full_plant_state=y.tolist(), onset_controller=onset['controller'],
                source_Pb0_W=float(y[3]), source_ramp_down_W_per_s=d['battery_source_ramp_down_W_per_s'],
                source_tau_s=d['battery_source_tau_s'], source_voltage_pu=event['retained_source_pu'],
                WL0_J=float(wl), aggregate_headroom_J=float(headroom), exit_upper_W=float(pexit),
                initial_excess_power_lower_W=float(a), excess_power_down_slope_W_per_s=float(b),
                valid_positive_source_horizon_s=float(horizon), peak_prefix_s=float(peak),
                maximum_prefix_gain_J=float(gain(peak)), maximum_headroom_excess_J=float(gain(peak)-headroom),
                first_headroom_equality_after_fault_s=crossing,
                first_headroom_equality_absolute_s=event['start_s']+crossing if crossing is not None else None,
                excludes_all_actual_I_DC_safe_control=bool(gain(peak)>headroom),
                scope='Outer slew-only necessary condition; lag/control constraints relaxed; no copied historical onset time')


def flattened_scalars(value, prefix=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from flattened_scalars(item, prefix + '.' + str(key) if prefix else str(key))
    elif isinstance(value, (int, float, np.number)) and not isinstance(value, (bool, np.bool_)):
        yield prefix, float(value)


class TimingSummary:
    def __init__(self):
        self.series = {}
        self.counts = {'calls': 0, 'guard_failures': 0, 'solver_success_false': 0,
                       'backup_calls': 0, 'accepted_nonoptimal_calls': 0}
        self.backup_types = {}

    def add(self, log, outer_s, failure=False):
        self.counts['calls'] += 1
        self.counts['guard_failures'] += int(failure)
        self.series.setdefault('controller_total_wall_s_including_PI_guard_AW', []).append(float(outer_s))
        for key, value in flattened_scalars(log):
            lower = key.lower()
            if math.isfinite(value) and ('.timing.' in lower or lower.endswith(('wall_s', 'duration_s'))):
                self.series.setdefault(key, []).append(value)
        def walk(obj):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    yield key.lower(), val
                    if isinstance(val, dict):
                        yield from walk(val)
        fields = list(walk(log))
        failed = any(k in ('solver_success', 'optimizer_success', 'success', 'success_flag') and v is False for k, v in fields)
        self.counts['solver_success_false'] += int(failed)
        modes = [str(v) for k, v in fields if k in ('mode', 'type', 'backup_type', 'command_source', 'selected_mode', 'chosen_mode') and isinstance(v, str)]
        backup = next((s for s in modes if any(x in s.lower() for x in ('backup', 'shifted', 'terminal'))), None)
        if backup:
            self.counts['backup_calls'] += 1
            self.backup_types[backup] = self.backup_types.get(backup, 0) + 1
        self.counts['accepted_nonoptimal_calls'] += int(any(k in ('accepted_nonoptimal', 'accepted_non_optimal', 'feasible_nonoptimal', 'accepted_suboptimal') and v is True for k,v in fields))

    def result(self):
        return dict(counts=self.counts, backup_types=self.backup_types,
                    seconds={k: dict(n=len(v), minimum_s=min(v), median_s=float(np.median(v)),
                                     p95_s=float(np.percentile(v,95)), maximum_s=max(v),
                                     sum_s=float(sum(v)), over_100us_count=sum(x>1e-4 for x in v))
                             for k,v in self.series.items()},
                    note='All raw timing/solver/backup fields are retained per call; offline virtual time only')


def reference_comparison(case, endpoints, normalized, d):
    """Report existing-reference coverage; never fabricate the unobserved tail."""
    if case['event']:
        path = OUTPUT / (tag_for('C0-' + case['port'], 1e-5) + '.npz')
        label = 'same_port_guarded_no_fault'
    elif case['port'] == 'fast':
        path = ROOT / 'source_speed_ablation/results/fast_reference_h1e-05.npz'
        label = 'existing_same_full_state_unguarded_fast_Q_priority'
    else:
        path = ROOT / 'gate_a_extension/results/matched_no_fault_reference_v2.npz'
        label = 'existing_same_full_state_unguarded_slow_Q_priority'
    if not path.exists():
        return {'status': 'REFERENCE_UNAVAILABLE', 'reference': str(path.relative_to(ROOT))}, None
    with np.load(path, allow_pickle=False) as z:
        ra = z['endpoint_trace'].copy()
        rn = z['normalized_state'].copy() if 'normalized_state' in z else None
    if not np.allclose(ra[0, 1:8], endpoints[0, 1:8], rtol=0, atol=1e-8) or abs(ra[0,0]-.6)>1e-12:
        raise RuntimeError('Reference initial physical/passive state is not identical')
    end = min(float(endpoints[-1,0]), float(ra[-1,0]))
    own = np.array([np.interp(end, endpoints[:,0], endpoints[:,j]) for j in range(endpoints.shape[1])])
    ref = np.array([np.interp(end, ra[:,0], ra[:,j]) for j in range(ra.shape[1])])
    # Both existing references place cumulative PCC P/Q immediately after the
    # original seven physical/passive states, even though their tails differ.
    result = dict(status='OBSERVED_COMMON_WINDOW_ONLY', reference=label,
                  reference_file=str(path.relative_to(ROOT)), reference_sha256=sha(path),
                  same_initial_7_state_exact=bool(np.array_equal(ra[0,1:8],endpoints[0,1:8])),
                  common_start_s=.6, common_end_s=end,
                  full_observed_case_covered=bool(ra[-1,0]>=endpoints[-1,0]-1e-12),
                  comparison_interpolation='Linear on stored100us endpoints if terminal time is off clock; not a new physical replay',
                  P_integral_difference_J=float(own[8]-ref[8]),
                  Q_integral_difference_var_s=float(own[9]-ref[9]),
                  battery_stored_energy_difference_J=float(own[5]-ref[5]),
                  DC_energy_difference_J=float(own[3]-ref[3]),
                  RL_energy_difference_J=float(.75*(d['filter_L_H']+d['grid_L_H'])*(own[1]**2+own[2]**2-ref[1]**2-ref[2]**2)),
                  remote_source_integral_difference_J=float(own[6]-ref[6]),
                  total_loss_integral_difference_J=float(own[7]-ref[7]),
                  no_past_service_restoration_claim=True)
    if ra.shape[1] == len(COLS):
        result.update(P_absolute_error_integral_difference_J=float(own[12]-ref[12]),
                      Q_absolute_error_integral_difference_var_s=float(own[13]-ref[13]))
    if rn is not None:
        nmax = 0.; count = 0
        for row in normalized:
            j = np.searchsorted(rn[:,0], row[0]-1e-11)
            if j<len(rn) and abs(rn[j,0]-row[0])<1e-10:
                nmax=max(nmax,float(np.max(abs(row[1:]-rn[j,1:])))); count+=1
        result.update(matched_sample_count=count, max_normalized_state_difference=nmax if count else None)
    else:
        result['normalized_state_comparison'] = 'NOT_AVAILABLE_IN_EXISTING_SLOW_REFERENCE'
    return result, rn


def recovery_score(case, completed, globally_safe, states, intervals, reference_states, d):
    if not case['event']:
        return {'status':'NOT_APPLICABLE_NO_FAULT','joint_recovery_time_s':None,'checks':[]}
    if not completed:
        return {'status':'NOT_SCORED_INCOMPLETE_TRAJECTORY','joint_recovery_time_s':None,
                'checks':[], 'clearance_observed':bool(states[-1,0]>=case['event']['end_s'])}
    if reference_states is None:
        return {'status':'NOT_SCORED_REFERENCE_UNAVAILABLE','joint_recovery_time_s':None,'checks':[]}
    Ts=d['control_sample_s']; nperiod=round(.05/Ts); count=0; recovered=None; checks=[]
    start=math.ceil((case['event']['end_s']+.15-1e-12)/.05)*.05
    for end in np.arange(start,states[-1,0]+1e-11,.05):
        ids=np.flatnonzero((states[:,0]>end-.05+1e-11)&(states[:,0]<=end+1e-11))
        if len(ids)!=nperiod or ids[0]<nperiod:
            continue
        times=states[ids,0]; prior=ids-nperiod
        rids=np.searchsorted(reference_states[:,0],times-1e-11)
        if np.any(rids>=len(reference_states)) or np.max(abs(reference_states[rids,0]-times))>1e-10:
            continue
        selfdiff=float(np.max(abs(states[ids,1:]-states[prior,1:])))
        targetdiff=float(np.max(abs(states[ids,1:]-reference_states[rids,1:])))
        window=intervals[(intervals[:,1]>end-.15+1e-11)&(intervals[:,1]<=end+1e-11)]
        covered=len(window)>=round(.15/Ts) and window[0,0]<=end-.15+1e-10
        safe=bool(covered and max(window[:,2])<=1+1e-8 and min(window[:,3])>=.8-1e-8
                  and max(window[:,4])<=1.1+1e-8 and max(window[:,5])<=1.2e6*(1+1e-8)
                  and max(window[:,6])<=.95e6*(1+1e-8) and max(window[:,7])<=1e6*(1+1e-8)
                  and min(window[:,8])>=.2-1e-8 and max(window[:,9])<=.8+1e-8
                  and max(window[:,17])<=d['svpwm_linear_voltage_derating']/np.sqrt(3)*(1+1e-8))
        # Include common-guard intervention in the conservative unclipped window.
        free=bool(covered and not np.any(window[:,12:17]>.5))
        freq=float(max(window[:,10])) if len(window) else None
        good=bool(safe and free and selfdiff<=1e-5 and targetdiff<=1e-5 and freq is not None and freq<=.001)
        count=count+1 if good else 0
        checks.append(dict(time_s=float(end),self_50ms_difference=selfdiff,
                           same_time_guarded_no_fault_difference=targetdiff,safe_150ms=safe,
                           unclipped_including_guard_150ms=free,PLL_max_error_Hz=freq,
                           qualifying=good,successive=count))
        if count>=3 and recovered is None: recovered=float(end)
    return dict(status='SCORED_COMPLETED_TRAJECTORY',joint_recovery_time_s=recovered,checks=checks,
                global_safe_recovery=bool(globally_safe and recovered is not None),
                earlier_violation_cannot_be_erased=True,battery_inventory_excluded_from_orbit=True)


def update_roster(f):
    rows=[]
    for case in f['execution_order']:
        p=OUTPUT/(tag_for(case['id'],1e-5)+'.json')
        if p.exists():
            s=json.loads(p.read_text())
            row=dict(case=case['id'],status='EXECUTED',stop_reason=s['stop_reason'],
                     no_fault_physical_admission=s.get('no_fault_physical_admission'),result_file=p.name)
        else:
            ref=OUTPUT/(tag_for('C0-'+case['port'],1e-5)+'.json')
            blocked=case['event'] is not None and ref.exists() and json.loads(ref.read_text()).get('no_fault_physical_admission') is not True
            row=dict(case=case['id'],status='NOT_RUN_PENDING_REVIEW',
                     reason='same_port_C0_not_admitted' if blocked else 'staged_execution_not_yet_requested',
                     fault_onset_state='UNOBSERVED' if case['event'] else None,
                     recovery='UNOBSERVED')
        rows.append(row)
    dump(OUTPUT/'MODEL_ROSTER.json',dict(current_guard_qualified=False,paper_ready=False,
                                      safety_scope='conditional_current_only',no_100us_real_time_claim=True,cases=rows))


def run(case_id, h=1e-5):
    f,g,case,d,full_d,cp=load_design(case_id)
    check_run_admission(f,case,h)
    # Lazy imports let reviewers inspect pure scoring without invoking a guard.
    from guarded_controller import guarded_controller, GuardFailure
    from common_guard import CommonGuard
    OUTPUT.mkdir(exist_ok=True)
    tag=tag_for(case_id,h)
    # Exclusive reservation is durable even if a process crashes before summary.
    claim=OUTPUT/(tag+'.started.json')
    with claim.open('x') as stream:
        json.dump(dict(case=case_id,started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                       pid=os.getpid(),source_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL)),stream,indent=2)
    wall0=time.perf_counter()
    y=np.r_[np.array(cp['plant_state'],dtype=float),np.zeros(6)]
    ys=y.copy()
    ctl={k:(complex(*v) if k in ('zi','applied','queued') else v) for k,v in cp['controller'].items()}
    init_ctl=copy.deepcopy(ctl); initial_norm=normstate(.6,y,ctl,d)
    if not np.allclose(initial_norm,cp['normalized_state'],rtol=0,atol=1e-12):
        raise RuntimeError('The complete frozen .6s state was not reconstructed exactly')
    guard=CommonGuard(d)
    req={'P_req_W':800000.,'Q_req_var':700000.}
    Ts=d['control_sample_s'];t0=.6;end=case['end_time_s'];event=case['event']
    mmax=d['svpwm_linear_voltage_derating']/np.sqrt(3)
    wl0=.75*(d['filter_L_H']+d['grid_L_H'])*(y[0]**2+y[1]**2)
    def level(tt):
        return event['retained_source_pu'] if event and event['start_s']<=tt<event['end_s'] else 1.
    def measure(tt,yy,vv,cc=None):
        c=ctl if cc is None else cc
        i,vdc,u,v,pi,s,ps=signals(tt,yy,c,d,vv)
        wl=.75*(d['filter_L_H']+d['grid_L_H'])*abs(i)**2
        er=yy[4]-ys[4]+yy[2]-ys[2]+wl-wl0+yy[5]-ys[5]+yy[6]-ys[6]
        return np.array([tt,*yy,abs(i)/d['I_phase_peak_base_A'],vdc/d['V_dc_initial_V'],
                         s.real,s.imag,abs(v)/d['V_phase_peak_base_V'],pi,ps,wl,er,
                         d['soc_initial']+yy[4]/(d['battery_energy_MWh']*3.6e9),vv,c['omega']/(2*np.pi)])
    def fun(tt,yy,vv):
        s=signals(tt,yy,ctl,d,vv)[5]
        return np.r_[rhs(tt,yy,ctl,d,vv),s.real,s.imag,yy[3],battery_draw(yy[3],d),
                     abs(s.real-800000.),abs(s.imag-700000.)]
    def row_margins(a):
        return np.array([1-a[14],1.1-a[14],a[15]-.8,1.1-a[15],a[23]-.2,.8-a[23],
                         1-a[16]/950000.,1+a[16]/950000.,1-np.hypot(a[16],a[17])/1.2e6,
                         1-a[4]/1e6,1+a[4]/1e6])
    def margins(tt,yy,vv):
        return row_margins(measure(tt,yy,vv))
    ep=[measure(t0,y,1.)];states=[[t0,*initial_norm]];dense=[];controls=[];intervals=[]
    contacts=[];first_contacts={};first_beyond={};event_states={};timing=TimingSummary()
    reason='completed';exception_info=None;final_time=t0;near_count=0;sample_count=0
    phase_records={};max_mod=max(abs(ctl['applied']),abs(ctl['queued']))
    with gzip.open(OUTPUT/(tag+'.jsonl.gz'),'wt',encoding='utf-8') as raw:
        def emit(record):
            raw.write(json.dumps(jsonable(record),ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
            raw.flush()
        def phase_ctl(tt,sample_t):
            c=copy.deepcopy(ctl);c['theta']+=c['omega']*(tt-sample_t);return c
        def contact(name,tt,yy,vv,kind,sample_t,margin=None):
            if any(c['name']==name and abs(c['time_s']-tt)<1e-12 and c['kind']==kind for c in contacts[-16:]):
                return
            c=dict(name=name,time_s=float(tt),kind=kind,normalized_margin=margin,
                   plant_state=np.asarray(yy).tolist(),controller=serial_ctl(phase_ctl(tt,sample_t)),
                   source_level_pu=vv)
            contacts.append(c);first_contacts.setdefault(name,c);emit({'record':'hard_contact',**c})
        def screen(tt,yy,vv,kind,sample_t):
            mm=margins(tt,yy,vv);bad=[]
            for j,name in enumerate(HARD_NAMES):
                if mm[j]<=0:
                    contact(name,tt,yy,vv,kind,sample_t,float(mm[j]));bad.append(name)
                if mm[j]<-1e-8 and name not in first_beyond:
                    first_beyond[name]=float(tt)
            return bad
        def terminal_contact(names):
            for name in names:
                if name!='actual_current' or event is None:
                    return name
            return None
        emit(dict(record='run_header',case=case,protocol_sha256=sha(PROTOCOL),
                  same_full_checkpoint=cp,initial_augmented_plant_state=y,
                  physical_parameters=d,controller_parameter_whitelist=sorted(d),
                  control_sample_s=Ts,max_step_s=h,rtol=1e-10,atol=1e-8,
                  current_guard_qualified=False,safety_scope='conditional_current_only',
                  no_100us_real_time_claim=True,
                  fixed_current_certificate_bounds={key:getattr(guard,key,None) for key in
                                                    ('r','epsI','itight','utight','chord','mmax','Vlo','Vhi','N','Ts')},
                  storage_note='Every accepted sample emits update and end records; each rejected sample emits full prestate; physical states are never projected'))
        try:
            for k in range(round(t0/Ts),int(np.ceil(end/Ts))):
                tt=k*Ts;te=min((k+1)*Ts,end);sample_count+=1
                pre_y=y.copy();pre_ctl=copy.deepcopy(ctl);vs=level(tt)
                pre_measure=measure(tt,y,vs)
                bad=screen(tt,y,vs,'pre_sample',tt)
                stopping=terminal_contact(bad)
                if stopping:
                    reason=stopping;emit(dict(record='pre_sample_physical_stop',k=k,time_s=tt,
                                             plant_state=y,controller=serial_ctl(ctl),contacts=bad));break
                nominal_ctl=copy.deepcopy(ctl)
                nominal_cc=controller(tt,y.copy(),nominal_ctl,d,req,vs)
                m_nom=nominal_ctl['queued']
                call_start=time.perf_counter()
                try:
                    cc,log=guarded_controller(tt,y,ctl,d,req,vs,guard)
                except GuardFailure as exc:
                    elapsed=time.perf_counter()-call_start
                    log=getattr(exc,'record',{})
                    timing.add(log,elapsed,True)
                    failure_kind=str(log.get('failure_reason',log.get('reason',log.get('status',str(exc))))) if isinstance(log,dict) else str(exc)
                    reason='unadmitted' if k==round(t0/Ts) or 'unadmitted' in failure_kind.lower() else 'lost_certificate'
                    invariant=bool(np.array_equal(y,pre_y) and serial_ctl(ctl)==serial_ctl(pre_ctl))
                    if not invariant: reason='guard_failure_mutated_prestate'
                    emit(dict(record='guard_failure',k=k,time_s=tt,stop_reason=reason,
                              plant_pre=pre_y,plant_after_exception=y,controller_pre=serial_ctl(pre_ctl),
                              controller_after_exception=serial_ctl(ctl),prestate_preserved=invariant,
                              m_nom=m_nom,nominal_control=nominal_cc,guard=log,
                              certified_backup_plan=getattr(guard,'last_plan',None),
                              controller_total_wall_s_including_PI_guard_AW=elapsed,
                              driver_guard_call_wall_s=elapsed,driver_total_over_100us=elapsed>Ts,
                              exception_type=type(exc).__name__,exception_message=str(exc)))
                    exception_info={'type':type(exc).__name__,'message':str(exc),'record':log}
                    break
                elapsed=time.perf_counter()-call_start
                timing.add(log,elapsed)
                m_safe=ctl['queued'];delta=abs(m_safe-m_nom)
                expected_zi=nominal_ctl['zi']+Ts*d['current_Kaw_per_s']*pre_measure[15]*d['V_dc_initial_V']*(m_safe-m_nom)*np.exp(-1j*pre_ctl['theta'])
                invariants=dict(plant_unchanged=bool(np.array_equal(y,pre_y)),
                                old_queue_promoted=bool(ctl['applied']==pre_ctl['queued']),
                                field_whitelist_unchanged=set(ctl)==set(pre_ctl),
                                source_PLL_equal_nominal=all(ctl[key]==nominal_ctl[key] for key in ('theta','zpll','omega','pb_command')),
                                antiwindup_absolute_error=float(abs(ctl['zi']-expected_zi)),
                                all_values_finite=all(np.isfinite(v) for v in ctl.values()),
                                cc_eight_columns=len(cc)==8,
                                m_safe_norm=float(abs(m_safe)),mmax=float(mmax))
                vmax=max(pre_measure[18]*d['V_phase_peak_base_V'],.1*d['V_phase_peak_base_V'])
                requested_a,requested_b=800000/(1.5*vmax),700000/(1.5*vmax)
                flags=[abs(cc[5]-requested_a)>1e-7 or abs(cc[6]-requested_b)>1e-7,
                       cc[2]<1-1e-10,abs(cc[4])>=1e6*(1-1e-12),
                       abs(cc[3]-45)<1e-9 or abs(cc[3]-75)<1e-9,delta>1e-10]
                controls.append([*cc,*map(float,flags),delta]);max_mod=max(max_mod,abs(ctl['applied']),abs(m_safe))
                emit(dict(record='sample_update',k=k,time_s=tt,source_level_pu=vs,
                          plant_pre=pre_y,plant_post_update=y,controller_pre=serial_ctl(pre_ctl),
                          controller_post_update=serial_ctl(ctl),normalized_pre=normstate(tt,pre_y,pre_ctl,d),
                          normalized_post_update=normstate(tt,y,ctl,d),original_control=nominal_cc,
                          control=cc,m_nom=m_nom,m_safe=m_safe,guard_modification_norm=delta,
                          antiwindup_correction_vs_nominal=ctl['zi']-nominal_ctl['zi'],
                          guard=log,certified_backup_plan=getattr(guard,'last_plan',None),
                          controller_total_wall_s_including_PI_guard_AW=elapsed,
                          driver_guard_call_wall_s=elapsed,
                          driver_total_over_100us=elapsed>Ts,interface_checks=invariants))
                interface_ok=(invariants['plant_unchanged'] and invariants['old_queue_promoted'] and
                              invariants['field_whitelist_unchanged'] and invariants['source_PLL_equal_nominal'] and
                              invariants['antiwindup_absolute_error']<=1e-8 and invariants['all_values_finite'] and
                              invariants['cc_eight_columns'])
                if not interface_ok:
                    reason='controller_interface_violation';break
                if abs(m_safe)>mmax*(1+1e-8) or abs(ctl['applied'])>mmax*(1+1e-8):
                    contact('modulation',tt,y,vs,'sample_queue',tt,1-max(abs(m_safe),abs(ctl['applied']))/mmax)
                    reason='modulation_hard_violation';break
                cuts=sorted(set([tt,te]+([v for v in (event['start_s'],event['end_s']) if tt+1e-14<v<te-1e-14] if event else [])))
                local=[pre_measure];actual=tt;stopped=False;solver_records=[]
                for aa,bb in zip(cuts[:-1],cuts[1:]):
                    vv=level((aa+bb)/2);local.append(measure(aa,y,vv))
                    bad=screen(aa,y,vv,'hold_start_or_event_right',tt)
                    stopping=terminal_contact(bad)
                    if stopping:
                        actual=aa;reason=stopping;stopped=True;break
                    evf=[]
                    for j,name in enumerate(HARD_NAMES):
                        def ef(at,ay,index=j): return margins(at,ay,vv)[index]
                        ef.terminal=bool(name!='actual_current' or event is None);ef.direction=-1
                        evf.append(ef)
                    sol=solve_ivp(lambda at,ay:fun(at,ay,vv),(aa,bb),y,method='DOP853',
                                  rtol=1e-10,atol=1e-8,max_step=h,events=evf)
                    solver_records.append(dict(start_s=aa,requested_end_s=bb,actual_end_s=float(sol.t[-1]),
                                               success=bool(sol.success),status=int(sol.status),message=sol.message,
                                               nfev=int(sol.nfev),internal_nodes=len(sol.t)))
                    local.extend(measure(at,ay,vv) for at,ay in zip(sol.t[1:],sol.y.T[1:]))
                    y=sol.y[:,-1].copy();actual=float(sol.t[-1]);final_time=actual
                    for j,times in enumerate(sol.t_events):
                        for at,ay in zip(times,sol.y_events[j]):
                            contact(HARD_NAMES[j],float(at),ay,vv,'continuous_event_root',tt,0.)
                    if event and any(abs(actual-boundary)<1e-12 for boundary in (event['start_s'],event['end_s'])):
                        ec=phase_ctl(actual,tt)
                        key=format(actual,'.12f')
                        event_states[key]=dict(time_s=actual,plant_state=y.tolist(),controller=serial_ctl(ec),
                                               controller_theta_storage_before_advance=ctl['theta'],
                                               WL_J=float(.75*(d['filter_L_H']+d['grid_L_H'])*(y[0]**2+y[1]**2)),
                                               source_left_pu=level(np.nextafter(actual,-np.inf)),source_right_pu=level(actual))
                        emit(dict(record='external_event_boundary',**event_states[key]))
                    if sol.status==1:
                        reason=next(HARD_NAMES[j] for j,times in enumerate(sol.t_events) if evf[j].terminal and len(times))
                        stopped=True;break
                    if not sol.success:
                        reason='physical_solver_failure';stopped=True;break
                a=np.array(local)
                # Original internal-node extrema, including all left/right jumps.
                # Root contacts are stored separately; these are numerical observations.
                for row in a:
                    for name,margin in zip(HARD_NAMES,row_margins(row)):
                        if margin<-1e-8: first_beyond.setdefault(name,float(row[0]))
                        if margin<=0 and name not in first_contacts:
                            contact(name,float(row[0]),row[1:14],row[24],'first_observed_internal_node',tt,float(margin))
                mxS=float(np.max(np.hypot(a[:,16],a[:,17])));mxP=float(np.max(abs(a[:,16])))
                iv=[tt,actual,float(max(a[:,14])),float(min(a[:,15])),float(max(a[:,15])),mxS,mxP,
                    float(max(abs(a[:,4]))),float(min(a[:,23])),float(max(a[:,23])),
                    float(max(abs(a[:,25]-60))),float(max(abs(a[:,22]))),*map(float,flags),
                    max(abs(ctl['applied']),abs(ctl['queued']))]
                intervals.append(iv)
                near=(iv[2]>=.999 or iv[3]<=.801 or iv[4]>=1.099 or mxS>=.999*1.2e6
                      or mxP>=.999*950000 or iv[7]>=.999*1e6 or iv[8]<=.201 or iv[9]>=.799)
                near_count+=int(near)
                retain=bool(tt<t0+.005-1e-14 or near or (event and tt<=event['end_s']+.05))
                if retain:dense.extend(local)
                ctl['theta']+=ctl['omega']*(actual-tt)
                final_time=actual
                endpoint=measure(actual,y,level(np.nextafter(actual,-np.inf)))
                ep.append(endpoint);states.append([actual,*normstate(actual,y,ctl,d)])
                emit(dict(record='sample_interval',k=k,start_s=tt,end_s=actual,plant_post=y,
                          controller_post=serial_ctl(ctl),normalized_post=normstate(actual,y,ctl,d),
                          endpoint=endpoint,interval_extrema=iv,physical_solver_segments=solver_records,
                          dense_retained=retain,near_boundary=near,stop_reason=reason if stopped else None))
                if stopped:break
        except Exception as exc:
            reason='unhandled_runner_or_guard_failure'
            exception_info=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
            emit(dict(record='unhandled_failure',time_s=final_time,plant_state=y,controller=serial_ctl(ctl),exception=exception_info))
        emit(dict(record='run_terminal',time_s=final_time,stop_reason=reason,
                  plant_state=y,controller=serial_ctl(ctl),exception=exception_info))
    ep=np.asarray(ep);states=np.asarray(states)
    controls=np.asarray(controls).reshape(-1,len(CONTROL_COLS))
    intervals=np.asarray(intervals).reshape(-1,len(INTERVAL_COLS))
    dense=np.asarray(dense).reshape(-1,len(COLS))
    trace_path=OUTPUT/(tag+'.npz')
    np.savez_compressed(trace_path,endpoint_trace=ep,normalized_state=states,control=controls,
                        interval_extrema=intervals,dense_trace=dense,endpoint_columns=np.array(COLS),
                        normalized_columns=np.array(NORMALIZED_NAMES),control_columns=np.array(CONTROL_COLS),
                        interval_columns=np.array(INTERVAL_COLS),initial_plant_state=ys,
                        final_plant_state=y,full_controller_json=np.array(json.dumps(jsonable(serial_ctl(ctl)))))
    metrics=dict(I_peak_pu=float(max(ep[:,14])),Vdc_min_pu=float(min(ep[:,15])),
                 Vdc_max_pu=float(max(ep[:,15])),S_peak_VA=float(max(np.hypot(ep[:,16],ep[:,17]))),
                 P_abs_peak_W=float(max(abs(ep[:,16]))),Pb_abs_peak_W=float(max(abs(ep[:,4]))),
                 soc_min=float(min(ep[:,23])),soc_max=float(max(ep[:,23])),
                 energy_residual_max_J=float(max(abs(ep[:,22]))),modulation_max=float(max_mod))
    if len(intervals):
        for key,j,op in [('I_peak_pu',2,max),('Vdc_min_pu',3,min),('Vdc_max_pu',4,max),
                         ('S_peak_VA',5,max),('P_abs_peak_W',6,max),('Pb_abs_peak_W',7,max),
                         ('soc_min',8,min),('soc_max',9,max),('energy_residual_max_J',11,max)]:
            metrics[key]=float(op(metrics[key],op(intervals[:,j])))
    completed=bool(reason=='completed' and abs(final_time-end)<1e-10)
    physical_safe=bool(not contacts and not first_beyond and max_mod<=mmax*(1+1e-8))
    admitted=bool(completed and physical_safe and timing.counts['guard_failures']==0)
    onset=next((v for v in event_states.values() if event and abs(v['time_s']-event['start_s'])<1e-12),None)
    cleared=next((v for v in event_states.values() if event and abs(v['time_s']-event['end_s'])<1e-12),None)
    comparison,refstates=reference_comparison(case,ep,states,d)
    recovery=recovery_score(case,completed,physical_safe,states,intervals,refstates,d)
    q=dict(case=case_id,evidence='new_frozen_gate1_offline_model_diagnostic',
           status='EXECUTED',current_guard_qualified=False,paper_ready=False,
           safety_scope='conditional_current_only',no_100us_real_time_claim=True,
           topology_scope='Synthetic controlled DC port only; no validated DC/DC or directly connected battery claim',
           same_full_state=True,initial_checkpoint=f['initial_checkpoint'],checkpoint_sha256=g['checkpoint_sha256'],
           protocol_sha256=sha(PROTOCOL),physical_protocol_sha256=g['base_sha256'],
           runner_source_sha256=sha(__file__),controller_source_sha256=sha(HERE/'guarded_controller.py'),
           guard_source_sha256=sha(HERE/'common_guard.py'),physical_rhs_source_sha256=sha(ROOT/'gate_a/dq_bench.py'),
           source_port=case['port'],source_tau_s=d['battery_source_tau_s'],
           source_ramp_W_per_s=d['battery_source_ramp_up_W_per_s'],
           h_s=h,control_sample_s=Ts,initial_time_s=t0,planned_end_s=end,final_time_s=final_time,
           stop_reason=reason,simulation_completed=completed,metrics=metrics,
           no_physical_hard_contact_up_to_stop=physical_safe,complete_hard_safe=admitted,
           no_fault_physical_admission=admitted if not event else None,
           first_contacts=first_contacts,all_hard_contacts=contacts,first_observed_beyond_roundoff=first_beyond,
           terminal_contact={reason:final_time} if reason in HARD_NAMES else {},
           current_continuous_crossings_s=[c['time_s'] for c in contacts if c['name']=='actual_current'],
           event=event,event_boundary_states=event_states,
           phases=dict(checkpoint_observed=True,fault_onset_observed=bool(onset) if event else None,
                       clearance_observed=bool(cleared) if event else None,
                       full_recovery_observation_completed=completed if event else None,
                       unobserved_remainder_s=max(0.,end-final_time)),
           service=service(ys,y,final_time-t0),inventory=inventory(ys,y,d),
           matched_reference=comparison,recovery=recovery,
           actual_onset_energy_necessary_condition=energy_necessary_condition(onset,event,d) if event else {'status':'NOT_APPLICABLE_NO_FAULT'},
           timing=timing.result(),guard_exception=exception_info,
           health_gate=dict(physical_admitted=admitted if not event else None,
                            service_transparency_pass=None,
                            reason='No service-transparency tolerance was predeclared; retain request errors and matched-reference differences',
                            initial_guard_modification_norm=float(controls[0,-1]) if len(controls) else None,
                            max_guard_modification_norm=float(max(controls[:,-1])) if len(controls) else None,
                            intervention_count=int(sum(controls[:,12]>.5)) if len(controls) else 0),
           samples_attempted=sample_count,accepted_control_count=len(controls),
           near_boundary_interval_count=near_count,
           numerical_refinement_indicated=bool(contacts or near_count),
           initial_plant_state=ys,initial_controller=serial_ctl(init_ctl),
           final_plant_state=y,final_controller=serial_ctl(ctl),
           wall_time_s=time.perf_counter()-wall0,
           trace_file=trace_path.name,trace_sha256=sha(trace_path),
           full_sample_log_file=tag+'.jsonl.gz',full_sample_log_sha256=sha(OUTPUT/(tag+'.jsonl.gz')),
           storage='Every100us full pre/post plant/PLL/PI/source/queue and full guard plan in gzip; endpoints/normalized state/extrema in NPZ; dense first5ms, fault through50ms after clearance, and near-boundary intervals',
           numerical_event_scope='DOP853 root-located downward crossings plus explicit left/right jump screens; sampled extrema are not interval-certified bounds')
    if onset:
        yf=np.asarray(cleared['plant_state']) if cleared else y
        stop=event['end_s'] if cleared else final_time
        q['observed_fault_service']=service(onset['plant_state'],yf,max(0.,stop-event['start_s']))
    dump(OUTPUT/(tag+'.json'),q)
    update_roster(f)
    print(json.dumps(jsonable(q),ensure_ascii=False,indent=2,allow_nan=False),flush=True)
    return q


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',required=True,choices=('C0-slow','C0-fast','C50-slow','C50-fast','C1-slow','C1-fast'))
    parser.add_argument('--h',type=float,default=1e-5,choices=(1e-5,5e-6))
    args=parser.parse_args()
    run(args.case,args.h)
