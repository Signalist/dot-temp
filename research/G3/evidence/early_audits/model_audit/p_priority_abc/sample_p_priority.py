from reference_abc import *

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
    # Exact inverse plus P-priority projection in the measured voltage basis.
    # At vanishing voltage, no claim of P/Q deliverability is made.
    ep = v/max(V,floor)
    eq = -1j*ep
    a = self.case['P_req_W']/(1.5*max(V,floor))
    b = self.case['Q_req_var']/(1.5*max(V,floor))
    Imax = self.p['current_reference_limit_pu']*self.ibase
    alim = clip(a,-Imax,Imax)
    blim = clip(b,-math.sqrt(max(0.0,Imax**2-alim**2)),math.sqrt(max(0.0,Imax**2-alim**2)))
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
    return locals()
