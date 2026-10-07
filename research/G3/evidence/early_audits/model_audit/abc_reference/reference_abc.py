"""Independent three-phase Gate A average-model reference.

No import of the parent dq implementation, no model-state projection.
Only locked JSON parameters and standard NumPy/SciPy dependencies are used.
The plant is integrated in abc; dq is used only by the sampled controller.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import root

OFFSETS = np.array([0.0, -2.0*math.pi/3.0, 2.0*math.pi/3.0])
WEIGHTS = np.exp(-1j*OFFSETS)


def abc_from_complex(z: complex) -> np.ndarray:
    return np.real(z*np.exp(1j*OFFSETS))


def complex_from_abc(x: np.ndarray) -> complex:
    return complex((2.0/3.0)*np.dot(x, WEIGHTS))


def clip(x, a, b):
    return min(max(x, a), b)


class ABCReference:
    def __init__(self, p, case, h):
        self.p, self.case, self.h = p, case, h
        self.Ts = p['control_sample_s']
        self.w0 = p['omega_base_rad_s']
        self.vbase = p['V_phase_peak_base_V']
        self.ibase = p['I_phase_peak_base_A']
        self.Rf, self.Lf = p['filter_R_ohm'], p['filter_L_H']
        self.Rg, self.Lg = p['grid_R_ohm'], p['grid_L_H']
        self.R, self.L = self.Rf+self.Rg, self.Lf+self.Lg
        self.C = p['C_dc_F']
        self.Wref = 0.5*self.C*p['V_dc_initial_V']**2
        self.Ebase = p['battery_energy_MWh']*3.6e9
        self.eq = self.initialize()
        self.omega = self.w0
        self.theta = self.eq['theta']
        self.zpll = 0.0
        self.zi = self.Rf*self.eq['i_ab']*np.exp(-1j*self.theta)
        self.m_applied = self.eq['u_ab']/p['V_dc_initial_V']
        self.m_queued = self.eq['u_ab']/p['V_dc_initial_V']
        self.source_command = self.eq['Pbat']
        self.ref = self.eq['i_ab']
        self.ref_norm_max = 0.0
        self.mod_norm_max = 0.0
        self.rows = []
        self.first_continuous_crossing = None
        self.stop = None

    def initialize(self):
        E = self.vbase*self.case['source_voltage_pu']
        Zg = self.Rg+1j*self.w0*self.Lg
        target = self.case['P_req_W']+1j*self.case['Q_req_var']
        def eqn(x):
            i = complex(*x)
            S = 1.5*(E+Zg*i)*i.conjugate()
            return [(S.real-target.real)/self.p['S_base_VA'], (S.imag-target.imag)/self.p['S_base_VA']]
        iguess = target.conjugate()/(1.5*E)
        sol = root(eqn, [iguess.real, iguess.imag], tol=1e-12)
        if not sol.success or np.linalg.norm(eqn(sol.x)) > 1e-10:
            raise RuntimeError('Initial electrical root failed: '+str(sol.message))
        i = complex(*sol.x)
        v = E+Zg*i
        u = v+(self.Rf+1j*self.w0*self.Lf)*i
        Pinv = 1.5*(u*i.conjugate()).real
        Ploss = self.p['inverter_loss_constant_W'] + self.p['inverter_loss_current_squared_W_at_1pu']*(abs(i)/self.ibase)**2
        bus = Pinv+Ploss
        Pbat = bus/self.p['eta_dc_dc'] if bus >= 0 else bus*self.p['eta_dc_dc']
        return dict(i_ab=i, v_pcc_ab=v, u_ab=u, theta=float(np.angle(v)), Pbat=Pbat,
                    root_residual=float(np.linalg.norm(eqn(sol.x))))

    def source_level(self, t):
        ev = self.case['event']
        return ev['retained_voltage_pu'] if ev and ev['start_s'] <= t < ev['end_s'] else self.case['source_voltage_pu']

    def algebra(self, t, y, level):
        # Voltage is an actuator output, never an ideal current injection.
        Vdc = math.sqrt(2.0*y[3]/self.C)
        u = abc_from_complex(Vdc*self.m_applied)
        eg = self.vbase*level*np.cos(self.w0*t+OFFSETS)
        i = y[:3]
        v = (self.Lg*(u-self.Rf*i)+self.Lf*(eg+self.Rg*i))/self.L
        norm = math.sqrt(2.0/3.0*float(i@i))/self.ibase
        Pinv, Ps = float(u@i), float(eg@i)
        Pcopper = self.R*float(i@i)
        Ploss = self.p['inverter_loss_constant_W'] + self.p['inverter_loss_current_squared_W_at_1pu']*norm**2
        Pb = float(y[4]); eta = self.p['eta_dc_dc']
        Pbus = eta*Pb if Pb >= 0 else Pb/eta
        Pdeplete = Pb/self.p['eta_discharge_energy'] if Pb >= 0 else self.p['eta_charge_energy']*Pb
        return Vdc,u,eg,v,norm,Pinv,Ps,Pcopper,Ploss,Pbus,Pdeplete

    def rhs(self, t, y, level):
        Vdc,u,eg,v,norm,Pi,Ps,Pr,Pl,Pbus,Pdep = self.algebra(t,y,level)
        d = np.zeros(13)
        d[:3] = (u-eg-self.R*y[:3])/self.L
        d[3] = Pbus-Pi-Pl-self.p['auxiliary_power_W']
        d[4] = clip((self.source_command-y[4])/self.p['battery_source_tau_s'],
                    -self.p['battery_source_ramp_down_W_per_s'],self.p['battery_source_ramp_up_W_per_s'])
        d[5] = -Pdep
        d[6:] = [Pi,Ps,Pr,Pl,Pbus,y[4],Pdep]
        return d

    def sample(self,t,y):
        # Locked v1: measure OLD applied command, then release the queued command.
        Vdc,u,eg,vabc,norm,Pinv,Ps,Pr,Pl,Pbus,Pdep = self.algebra(t,y,self.source_level(t))
        rot = np.exp(-1j*self.theta)
        v = complex_from_abc(vabc)*rot
        i = complex_from_abc(y[:3])*rot
        V = abs(v); floor = self.p['pll_normalization_floor_pu']*self.vbase
        if V >= floor:
            err = v.imag/max(V,floor)
            wraw = self.w0+self.p['pll_Kp_per_s']*err+self.zpll
            wnew = clip(wraw,2*math.pi*self.p['pll_frequency_min_Hz'],2*math.pi*self.p['pll_frequency_max_Hz'])
            self.zpll += self.Ts*(self.p['pll_Ki_per_s2']*err+self.p['pll_Kaw_per_s']*(wnew-wraw))
            self.omega = wnew
        # Exact inverse plus Q-priority projection in the measured voltage basis.
        # At vanishing voltage, no claim of P/Q deliverability is made.
        ep = v/max(V,floor)
        eq = -1j*ep
        a = self.case['P_req_W']/(1.5*max(V,floor))
        b = self.case['Q_req_var']/(1.5*max(V,floor))
        Imax = self.p['current_reference_limit_pu']*self.ibase
        blim = clip(b,-Imax,Imax)
        alim = clip(a,-math.sqrt(max(0.0,Imax**2-blim**2)),math.sqrt(max(0.0,Imax**2-blim**2)))
        iref = alim*ep+blim*eq
        ei = iref-i
        uu = v+1j*self.omega*self.Lf*i+self.p['current_Kp_ohm']*ei+self.zi
        umax = self.p['svpwm_linear_voltage_derating']*Vdc/math.sqrt(3.0)
        us = uu*min(1.0,umax/max(abs(uu),1e-30))
        self.zi += self.Ts*(self.p['current_Ki_ohm_per_s']*ei+self.p['current_Kaw_per_s']*(us-uu))
        new_mod = us*np.exp(1j*self.theta)/Vdc
        eta = self.p['eta_dc_dc']; bus_demand = Pinv+Pl+self.p['auxiliary_power_W']
        ff = bus_demand/eta if bus_demand >= 0 else bus_demand*eta
        self.source_command = clip(ff+self.p['dc_energy_feedback_gain_per_s']*(self.Wref-y[3]),
                                   self.p['battery_terminal_power_min_W'],self.p['battery_terminal_power_max_W'])
        self.m_applied,self.m_queued = self.m_queued,new_mod
        self.ref = iref*np.exp(1j*self.theta)
        self.ref_norm_max = max(self.ref_norm_max,abs(iref)/self.ibase)
        self.mod_norm_max = max(self.mod_norm_max,abs(new_mod))

    def log(self,t,y):
        A = self.algebra(t,y,self.source_level(t))
        Vdc,u,eg,v,norm,Pi,Ps,Pr,Pl,Pbus,Pdep=A
        vi=complex_from_abc(v); ii=complex_from_abc(y[:3]); S=1.5*vi*ii.conjugate()
        self.rows.append([t,*y[:6],norm,abs(self.ref)/self.ibase,Vdc,S.real,S.imag,Pi,Ps,Pbus,
                          self.source_command,self.theta,self.omega,abs(self.m_applied),*y[6:]])
        if norm > self.p['current_continuous_limit_pu'] and self.first_continuous_crossing is None:
            self.first_continuous_crossing=t
        if norm >= self.p['current_emergency_stop_pu']: self.stop='actual_current_emergency'
        elif Vdc/self.p['V_dc_initial_V'] < self.p['V_dc_min_pu']: self.stop='dc_undervoltage'
        elif Vdc/self.p['V_dc_initial_V'] > self.p['V_dc_max_pu']: self.stop='dc_overvoltage'
        elif y[5]/self.Ebase < self.p['soc_min'] or y[5]/self.Ebase > self.p['soc_max']: self.stop='soc_boundary'

    def rk4(self, t, y, h, level):
        k1=self.rhs(t,y,level);k2=self.rhs(t+h/2,y+h*k1/2,level)
        k3=self.rhs(t+h/2,y+h*k2/2,level);k4=self.rhs(t+h,y+h*k3,level)
        return y+h*(k1+2*k2+2*k3+k4)/6

    def stop_margin(self,y):
        norm=math.sqrt(2.0/3.0*float(y[:3]@y[:3]))/self.ibase
        v=math.sqrt(2.0*y[3]/self.C)/self.p['V_dc_initial_V']
        soc=y[5]/self.Ebase
        return min(self.p['current_emergency_stop_pu']-norm,
                   v-self.p['V_dc_min_pu'],self.p['V_dc_max_pu']-v,
                   soc-self.p['soc_min'],self.p['soc_max']-soc)

    def run(self):
        y=np.zeros(13);y[:3]=abc_from_complex(self.eq['i_ab']);y[3]=self.Wref;y[4]=self.eq['Pbat'];y[5]=self.p['soc_initial']*self.Ebase
        y0=y.copy();t=0.0;end=self.case['duration_s'];n=0
        events=[]
        if self.case['event']: events=[self.case['event']['start_s'],self.case['event']['end_s']]
        while t < end-1e-12 and self.stop is None:
            self.sample(t,y)
            self.log(t,y)
            nextsample=min((n+1)*self.Ts,end)
            breaks=[t]+[e for e in events if t+1e-12 < e < nextsample-1e-12]+[nextsample]
            for left,right in zip(breaks[:-1],breaks[1:]):
                level=self.source_level((left+right)/2)
                steps=max(1,int(math.ceil((right-left)/self.h-1e-9)))
                h=(right-left)/steps
                for j in range(steps):
                    tj=left+j*h
                    candidate=self.rk4(tj,y,h,level)
                    used_h=h
                    reached=False
                    if self.stop_margin(candidate) <= 0:
                        # Locate the first hard boundary by integration/bisection.
                        # This is event localization, never projection of a state.
                        lo,hi=0.0,h
                        for _ in range(35):
                            mid=(lo+hi)/2
                            if self.stop_margin(self.rk4(tj,y,mid,level)) > 0: lo=mid
                            else: hi=mid
                        used_h=hi
                        candidate=self.rk4(tj,y,used_h,level)
                        reached=True
                    y=candidate
                    self.theta += used_h*self.omega
                    t=tj+used_h
                    self.log(t,y)
                    if reached and self.stop is None:
                        self.stop='hard_boundary_event'
                    if self.stop: break
                if self.stop:break
            n+=1
        a=np.asarray(self.rows)
        WL0=0.5*self.L*float(y0[:3]@y0[:3]);WL=0.5*self.L*float(y[:3]@y[:3])
        energy={'ac_residual_J':float(y[6]-y[7]-y[8]-(WL-WL0)),
                'dc_residual_J':float(y[10]-y[6]-y[9]-self.p['auxiliary_power_W']*t-(y[3]-y0[3])),
                'battery_residual_J':float(y[5]-y0[5]+y[12]),
                'dc_initial_J':self.Wref,'inductor_initial_J':WL0,'inductor_final_J':WL,
                'integral_Pinv_J':float(y[6]),'integral_Psource_J':float(y[7]),'integral_copper_J':float(y[8]),
                'integral_inverter_loss_J':float(y[9]),'integral_Pbus_J':float(y[10]),'integral_Pbat_J':float(y[11]),
                'delta_battery_energy_J':float(y[5]-y0[5]),'delta_dc_energy_J':float(y[3]-y0[3])}
        summary={'case':self.case['id'],'h_max_s':self.h,'status':self.stop or 'completed',
                 'last_time_s':float(t),'actual_current_max_pu':float(a[:,7].max()),
                 'reference_current_max_pu':self.ref_norm_max,'first_actual_current_gt_1_s':self.first_continuous_crossing,
                 'dc_voltage_min_pu':float(a[:,9].min()/self.p['V_dc_initial_V']),
                 'dc_voltage_max_pu':float(a[:,9].max()/self.p['V_dc_initial_V']),
                 'modulation_max':self.mod_norm_max,'initial_root_residual':self.eq['root_residual'],
                 'max_abc_current_sum_A':float(np.max(np.abs(a[:,1:4].sum(axis=1)))),
                 'energy':energy,'claims':'Fundamental switching-cycle-average abc model only; no protection after stop, no state projection'}
        return a,summary


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--protocol',required=True);ap.add_argument('--case',required=True);ap.add_argument('--h',type=float,default=1e-5);ap.add_argument('--out',required=True);args=ap.parse_args()
    raw=Path(args.protocol).read_bytes();p=json.loads(raw)
    case=next(x for x in p['case_registry'] if x['id']==args.case)
    sim=ABCReference(p,case,args.h);a,s=sim.run();s['protocol_sha256']=hashlib.sha256(raw).hexdigest();s['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    fields=['t','ia','ib','ic','Wdc','Pbat','Ebat','Iactual_pu','Iref_pu','Vdc','Ppcc','Qpcc','Pinv','Psource','Pbus','Pbat_cmd','theta_PLL','omega_PLL','modulation_norm','int_Pinv','int_Psource','int_copper','int_inverter_loss','int_Pbus','int_Pbat','int_depletion']
    np.savez_compressed(str(out)+'.npz',trace=a,columns=np.array(fields))
    Path(str(out)+'.json').write_text(json.dumps(s,indent=2)+'\n')
    print(json.dumps(s,indent=2))

if __name__=='__main__':main()
