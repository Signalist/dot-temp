"""Independent Gate1 audit oracle; algebraic static samples only, no plant integration.

This file deliberately does not import the guard or Gate0 solver implementation.
All test states are isolated algebraic fixtures, not physical trajectories.
"""
from pathlib import Path
import cmath
import hashlib
import json
import math
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXPECTED_PROTOCOL_SHA = 'be681761f993c6beaefaca0a54ece73dc2e3263d56b5b7f869ab476e87c96fa3'


def as_complex(v):
    return complex(float(v[0]), float(v[1]))


def as_real(z):
    return np.array([z.real, z.imag], dtype=float)


def state(i, q):
    return np.r_[as_real(i), as_real(q)]


class AlgebraOracle:
    def __init__(self, contract='structured_amplitude'):
        self.protocol_path = ROOT / 'protocol/GATE1_MPSC_SIX_MODELS_V1.json'
        assert hashlib.sha256(self.protocol_path.read_bytes()).hexdigest() == EXPECTED_PROTOCOL_SHA
        gate1 = json.loads(self.protocol_path.read_text())
        design_path = ROOT / 'protocol/GATE0_MPSC_DESIGN_V1.json'
        assert hashlib.sha256(design_path.read_bytes()).hexdigest() == gate1['base_Gate0_design_sha256']
        self.design = json.loads(design_path.read_text())
        assert hashlib.sha256((ROOT/self.design['base_protocol']).read_bytes()).hexdigest() == self.design['base_sha256']
        assert hashlib.sha256((ROOT/self.design['checkpoint']).read_bytes()).hexdigest() == self.design['checkpoint_sha256']
        self.d = json.loads((ROOT / self.design['base_protocol']).read_text())
        self.cp = json.loads((ROOT / self.design['checkpoint']).read_text())
        self.results = json.loads((ROOT / 'current_guard_gate0/GATE0_RESULTS.json').read_text())
        self.saved = next(r for r in self.results['contracts'] if r['contract'] == contract)
        self.Ts = self.design['sample_s']
        self.N = self.design['horizon_N']
        self.R = self.d['filter_R_ohm'] + self.d['grid_R_ohm']
        self.L = self.d['filter_L_H'] + self.d['grid_L_H']
        self.lam = self.R / self.L
        self.omega = self.d['omega_base_rad_s']
        self.Ibase = self.d['I_phase_peak_base_A']
        self.Ebase = self.d['V_phase_peak_base_V']
        self.Vbar = self.design['Vdc_center_V']
        self.Vlo, self.Vhi = self.design['Vdc_domain_V']
        self.mmax = self.d['svpwm_linear_voltage_derating'] / math.sqrt(3)
        self.reserve = self.design['first_hold_evaluation']['numerical_reserve_current_pu']
        co = self.design['contracts'][contract]
        self.Ec = co['source_center_pu'] * self.Ebase
        self.Er = co['source_uncertainty_radius_pu'] * self.Ebase
        self.a = math.exp(-self.lam * self.Ts)
        self.b = -math.expm1(-self.lam * self.Ts) / self.R
        self.c = self.Vbar * self.b / self.Ibase
        self.rot = cmath.exp(-1j * self.omega * self.Ts)
        self.Ki = -self.a ** 2 / self.c
        self.Kq = -self.a
        self.r = self.b * (max(abs(self.Vlo-self.Vbar), abs(self.Vhi-self.Vbar)) * self.mmax + self.Er) / self.Ibase
        self.current_radius = (1+self.a)*self.r
        self.input_radius = abs(self.Ki)*self.r
        self.utight = self.mmax-self.input_radius
        self.qbar = self.Ec*self.J(self.Ts)/(self.Vbar*self.b)
        self.mbar = self.qbar/self.rot
        self.sbar = state(0j, self.qbar)
        mu_domain = 1+(self.Vbar*max(self.utight, 0)+self.Ec)*self.b/self.Ibase
        d1 = (self.Vbar*max(self.utight, 0)+self.Ec+self.R*self.Ibase*mu_domain)/(self.L*self.Ibase)
        self.M2 = self.lam*d1+self.omega*self.Ec/(self.L*self.Ibase)
        self.chord = self.M2*(self.Ts/4)**2/8
        self.itight = 1-self.current_radius-self.chord-self.reserve

    def J(self, t):
        return (cmath.exp(1j*self.omega*t)-math.exp(-self.lam*t))/(self.R+1j*self.omega*self.L)

    def flow(self, z, t):
        zi, zq = as_complex(z[:2]), as_complex(z[2:])
        a = math.exp(-self.lam*t)
        b = -math.expm1(-self.lam*t)/self.R
        return a*zi+self.Vbar*b*zq/self.Ibase-self.Ec*self.J(t)/self.Ibase

    def advance(self, z, v):
        return state(self.rot*self.flow(z, self.Ts), self.rot*as_complex(v))

    def feedback(self, e):
        return self.Ki*as_complex(e[:2])+self.Kq*as_complex(e[2:])

    def omega_forward(self, w0, w1):
        return state(w0+self.a*self.rot*w1, self.Ki*self.rot*w1)

    def omega_inverse(self, e):
        ei, eq = as_complex(e[:2]), as_complex(e[2:])
        w1 = eq/(self.Ki*self.rot)
        w0 = ei-self.a*self.rot*w1
        reconstructed = self.omega_forward(w0, w1)
        finite = bool(np.isfinite(np.r_[e, as_real(w0), as_real(w1)]).all())
        norms = [abs(w0), abs(w1)]
        residual = float(np.max(np.abs(reconstructed-e))) if finite else math.inf
        return {'witnesses': [as_real(w0).tolist(), as_real(w1).tolist()],
                'disk_norms': norms, 'representation_residual_inf': residual,
                'inside': finite and max(norms) <= self.r+1e-8 and residual <= 1e-8}

    def source_reconstruct(self, i, vp, vdc, old_applied):
        lf, lg = self.d['filter_L_H'], self.d['grid_L_H']
        rf, rg = self.d['filter_R_ohm'], self.d['grid_R_ohm']
        return ((lf+lg)*vp-lg*(vdc*old_applied-rf*i))/lf-rg*i

    def validate_plan(self, s, z, v):
        z, v, s = np.asarray(z), np.asarray(v), np.asarray(s)
        if z.shape != (self.N+1,4) or v.shape != (self.N,2):
            return {'accepted': False, 'reason': 'shape'}
        if not np.isfinite(np.r_[s.ravel(), z.ravel(), v.ravel()]).all():
            return {'accepted': False, 'reason': 'nonfinite'}
        witness = self.omega_inverse(s-z[0])
        dyn = max(float(np.max(np.abs(self.advance(z[j],v[j])-z[j+1]))) for j in range(self.N))
        term = float(np.max(np.abs(z[-1]-self.sbar)))
        queue = max(abs(as_complex(row[2:]))-self.utight for row in z)
        inp = max(abs(as_complex(row))-self.utight for row in v)
        current = max(abs(self.flow(z[j], k*self.Ts/4))-self.itight for j in range(self.N) for k in range(5))
        omega = max(witness['disk_norms'])-self.r
        m = as_complex(v[0])+self.feedback(s-z[0])
        modulation = abs(m)-self.mmax
        res = max(0., dyn, term, queue, inp, current, omega, modulation, witness['representation_residual_inf'])
        return {'accepted': res <= 1e-8, 'max_primal_residual': res,
                'dynamics_residual_inf': dyn, 'terminal_residual_inf': term,
                'queue_norm_violation': queue, 'input_norm_violation': inp,
                'current_node_norm_violation': current, 'Omega_norm_violation': omega,
                'actual_modulation_norm_violation': modulation, 'membership': witness,
                'first_modulation': as_real(m).tolist()}


def static_algebra_checks():
    o = AlgebraOracle()
    saved = o.saved
    s0 = np.array(o.results['observation_interface']['aligned_initial_s0'])
    z, v = np.array(saved['nominal_states']), np.array(saved['nominal_inputs'])
    primal = o.validate_plan(s0,z,v)
    assert primal['accepted'], primal
    assert np.max(np.abs(o.sbar-saved['terminal_center_sbar'])) < 2e-15
    assert abs(o.mbar-as_complex(saved['terminal_nominal_input_mbar'])) < 2e-15
    assert np.max(np.abs(o.advance(o.sbar,as_real(o.mbar))-o.sbar)) < 2e-15
    assert abs(o.qbar-o.mbar) > 1e-3, 'Queue center and new command must differ by one sample rotation'
    cases = []
    for index in [1,o.N-1,o.N]:
        w0 = .21*o.r*cmath.exp(.43j)
        w1 = .39*o.r*cmath.exp(-.67j)
        e = o.omega_forward(w0,w1)
        center = z[index] if index < o.N else o.sbar
        nominal = as_complex(v[index]) if index < o.N else o.mbar
        algebraic_state = center+e
        inverse = o.omega_inverse(algebraic_state-center)
        assert inverse['inside'] and inverse['representation_residual_inf'] < 1e-14
        assert max(abs(as_complex(a)-b) for a,b in zip(inverse['witnesses'],[w0,w1])) < 1e-14
        new_m = nominal+o.feedback(e)
        assert abs(new_m) <= o.mmax+1e-8
        phase = .73+o.omega*o.Ts*index
        m_ab = new_m*cmath.exp(1j*phase)
        queued_ab = as_complex(algebraic_state[2:])*cmath.exp(1j*phase)
        assert abs(m_ab*cmath.exp(-1j*phase)-new_m) < 1e-14
        # A new command is expressed in the current sample's frame, then appears
        # as R(-omega Ts)*m in the NEXT sample's queue coordinate.
        assert abs(m_ab*cmath.exp(-1j*(phase+o.omega*o.Ts))-o.rot*new_m) < 1e-14
        cases.append({'j':index,'terminal':index>=o.N,'phase_rad':phase,
                      'membership':inverse,'new_modulation_ab':as_real(m_ab).tolist(),
                      'immutable_held_ab':as_real(queued_ab).tolist(),
                      'algebraic_state':algebraic_state.tolist()})
    # Separable current/queue projection circles are not an exact Omega test.
    ei = o.current_radius*.9
    eq = o.input_radius*.9
    false_box = state(ei+0j,eq+0j)
    assert abs(ei) < o.current_radius and abs(eq) < o.input_radius
    assert not o.omega_inverse(false_box)['inside']
    # Reconstruct only from static present electrical observations, with a
    # deliberately nonzero arbitrary global rotation unrelated to omega*t.
    meas = o.results['observation_interface']
    phase_errors = []
    for angle in [.73,-2.17,math.pi]:
        turn = cmath.exp(1j*angle)
        i = as_complex(meas['i_alpha_beta_A'])*turn
        vp = as_complex(meas['PCC_voltage_alpha_beta_V'])*turn
        applied = as_complex(o.cp['controller']['applied'])*turn
        source = o.source_reconstruct(i,vp,meas['Vdc_V'],applied)
        base = as_complex(meas['source_phasor_reconstructed_from_current_measurements_V'])*turn
        err = abs(source-base)
        phase_errors.append(err)
        assert err < 1e-10
    broad = AlgebraOracle('broad_circle')
    bp = broad.validate_plan(s0,broad.saved['nominal_states'],broad.saved['nominal_inputs'])
    assert not bp['accepted'] and bp['max_primal_residual'] > 1
    corruptions = {}
    for label, zs, vs in [('nonfinite',z.copy(),v.copy()),('terminal',z.copy(),v.copy()),('queue',z.copy(),v.copy())]:
        if label=='nonfinite': vs[3,0]=np.nan
        elif label=='terminal': zs[-1,0]+=.1
        elif label=='queue': zs[0,2]=2
        ans=o.validate_plan(s0,zs,vs)
        assert not ans['accepted']
        corruptions[label]=ans
    return {'status':'PASS_ALGEBRA_ONLY','no_physical_trajectory_executed':True,
            'protocol_sha256':EXPECTED_PROTOCOL_SHA,'structured_saved_plan':primal,
            'wide_failed_plan_rejected':bp,'backup_index_fixtures':cases,
            'box_projection_false_positive_rejected':o.omega_inverse(false_box),
            'source_reconstruction_complex_errors_V':phase_errors,
            'invalid_plan_rejection_checks':corruptions,
            'scope':'Independent numerical algebra and function-level fixtures only; no outward rounding, joint DC/SoC invariance, or realtime certification.'}


if __name__ == '__main__':
    result = static_algebra_checks()
    dest = HERE/'audit_algebra_results.json'
    dest.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'structured_residual':result['structured_saved_plan']['max_primal_residual'],
                      'wide_residual':result['wide_failed_plan_rejected']['max_primal_residual'],'output':str(dest)},indent=2))
