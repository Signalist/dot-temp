"""Repropagate stored held commands and rebuild port polynomials independently."""
from pathlib import Path
import json, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def check(path):
 dat=np.load(path)
 t=dat['t'];u=dat['u'];P=dat['p'];Q=dat['q'];D=dat['d'];h=np.diff(t)
 p=json.loads(str(dat['par_json']))
 v=p['v'];R=p['R'];L=p['L'];tau=p['tau'];omega=p['omega'];Cdc=p['Cdc']
 Gp=1500*v;c=R/(1500*v*v);k=L/(3000*v*v)
 W0=500*Cdc*p['vdc0']**2;Wmin=500*Cdc*p['vdcmin']**2;Wmax=500*Cdc*p['vdcmax']**2
 bs=[0.];cs=[0.];ints=0.;tube=np.full(5,np.inf);nodal=np.full(5,np.inf)
 derivmax=0.;poly_A_maxerr=0.;poly_M_maxerr=0.;mincmdstrip=math.inf
 for j,hj in enumerate(h):
  b0=bs[-1];C0=cs[-1];om=-math.expm1(-hj/tau)
  b1=b0+(u[j]-b0)*om
  C1=C0+u[j]*hj+(b0-u[j])*tau*om
  bs.append(b1);cs.append(C1)
  derivmax=max(derivmax,abs((u[j]-b0)/tau))
  pp=np.array([P[j],P[j+1]-P[j]]);qq=np.array([Q[j],Q[j+1]-Q[j]])
  sq=np.convolve(pp,pp)+np.convolve(qq,qq)
  net=np.r_[pp,0.]-c*sq-np.array([D[j],D[j+1]-D[j],0.])
  A=np.r_[ints,hj*net/np.arange(1,4)]
  A[:3]-=k*sq;A[0]+=k*(P[0]**2+Q[0]**2)
  ints+=hj*np.sum(net/np.arange(1,4))
  e0=np.array([v-R*pp[0]/Gp-L*pp[1]/(Gp*hj)+omega*L*qq[0]/Gp,
               -R*qq[0]/Gp-L*qq[1]/(Gp*hj)-omega*L*pp[0]/Gp])
  e1=np.array([-R*pp[1]/Gp+omega*L*qq[1]/Gp,
               -R*qq[1]/Gp-omega*L*pp[1]/Gp])
  M=1500*Cdc*np.array([e0@e0,2*(e0@e1),e1@e1,0.])
  poly_A_maxerr=max(poly_A_maxerr,np.max(np.abs(A-dat['A'][j])))
  poly_M_maxerr=max(poly_M_maxerr,np.max(np.abs(M-dat['M'][j])))
  A2=np.array([2*A[2],2*A[2]+6*A[3]])/hj**2
  M2=2*M[2]/hj**2
  curv=np.array([max(0,np.max(A2)+p['ramp']),max(0,-np.min(A2)+p['ramp']),
                 max(0,np.max(A2)-M2+p['ramp']),p['ramp'],p['ramp']])
  for x,Ct in [(0,C0),(1,C1)]:
   W=W0+np.polynomial.polynomial.polyval(x,A)+Ct
   B=p['B0']-Ct
   slacks=np.array([W-Wmin,Wmax-W,W-np.polynomial.polynomial.polyval(x,M),B-p['Bmin'],p['Bmax']-B])
   nodal=np.minimum(nodal,slacks)
   tube=np.minimum(tube,slacks-curv*hj*hj/8)
 bs=np.asarray(bs);cs=np.asarray(cs)
 return dict(file=path.name,terminal_b_kW=bs[-1],terminal_C_kJ=cs[-1],
             stored_node_b_error_kW=np.max(np.abs(bs-dat['b'])),stored_node_C_error_kJ=np.max(np.abs(cs-dat['charge'])),
             port_polynomial_A_max_difference=poly_A_maxerr,port_polynomial_M_max_difference=poly_M_maxerr,
             terminal_net_energy_kJ=ints,max_initial_cell_derivative_kW_s=derivmax,
             ramp_bound_excess_kW_s=derivmax-p['ramp'],maximum_command_kW=np.max(u),minimum_command_kW=np.min(u),
             b_magnitude_bound_margin_kW=p['bmax']-np.max(np.abs(bs)),
             queue_max_command_kW=np.max(np.abs(u[t[1:]<=p['delay']+1e-13])),
             current_sq_margin_kA2=p['imax']**2-np.max((P*P+Q*Q)/(Gp*Gp)),
             nodal_slack_min_kJ=nodal.tolist(),continuous_tube_slack_min_kJ=tube.tolist(),
             constraint_order=['W_lower','W_upper','modulation','B_lower','B_upper'],
             scope='Floating-point repropagation and independent energy/modulation polynomial construction, not interval proof')
if __name__=='__main__':
 rows=[check(f) for f in sorted((ROOT/'results').glob('zoh_q808_h*.npz'))]
 (ROOT/'review'/'zoh_independent_checks.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps(rows,indent=2))
