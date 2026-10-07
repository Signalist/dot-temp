"""Rational command plus exact two-block terminal correction, outward interval all-time proof."""
from pathlib import Path
import json,time
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];mp.iv.dps=40;mp.mp.dps=65
iv=mp.iv;I=lambda x:iv.mpf(str(x))
def enc(x):
 sc=mp.mpf(10)**45
 return [str(mp.floor(mp.mpf(x.a._mpi_[0])*sc)/sc),str(mp.ceil(mp.mpf(x.b._mpi_[1])*sc)/sc)]
def absmax(x):return max(abs(x.a),abs(x.b))
def pmin(a,b):return a if a.a<b.a else b
v=I('.690')*iv.sqrt(I(2)/3);Gp=1500*v;R=I('.005');L=I('.0003');Cdc=I('.03');tau=I('.005');om=100*iv.pi
cc=R/(1500*v*v);kk=L/(3000*v*v);p0=1300/(1+iv.sqrt(1-4*cc*650));Q0=I(808)
g2=I('.030')+2*I('.005')/3;s2=2*g2;ra=I('.045');r2=I('.040')+2*I('.005')/3
qq=cc*(10000*s2+Q0*Q0*g2);bb=ra*(1-2*cc*p0);gam=2*qq/(bb+iv.sqrt(bb*bb-4*cc*r2*qq))
def pulse(t,start=mp.mpf(0)):
 x=t-start
 if x<=0 or x>=mp.mpf('.040'):return I(0)
 if x<mp.mpf('.005'):return I(x)/I('.005')
 if x<=mp.mpf('.035'):return I(1)
 return (I('.040')-I(x))/I('.005')
def profile(t):
 g=pulse(t);gm=pulse(t,mp.mpf('.070'))
 if t<=mp.mpf('.125') or t>=mp.mpf('.175'):r=I(0)
 elif t<mp.mpf('.130'):r=(I(t)-I('.125'))/I('.005')
 elif t<=mp.mpf('.170'):r=I(1)
 else:r=(I('.175')-I(t))/I('.005')
 return p0+100*(gm-g)+gam*r,Q0*g,650+300*(g-gm)

def main():
 st=time.perf_counter();z=np.load(ROOT/'results'/'zoh_q808_h25.npz');ts=[mp.mpf(f'{t:.12f}') for t in z['t']];tt=[I(t) for t in ts];N=len(ts)-1
 # Decimal rational payload; scaling creates strict actuator margins before correction.
 us=[f'{u*(1-1e-6):.12f}' for u in z['u']];u0=list(map(I,us));T=I('.2')
 weights=[(1-iv.exp(-(tt[j+1]-tt[j])/tau))*iv.exp(-(T-tt[j+1])/tau) for j in range(N)]
 bT=sum((u*e for u,e in zip(u0,weights)),I(0));sumu=sum((u*(tt[j+1]-tt[j]) for j,u in enumerate(u0)),I(0));CT=sumu-tau*bT
 blocks=[(mp.mpf('.15'),mp.mpf('.16')),(mp.mpf('.18'),mp.mpf('.19'))]
 sel=[[j for j in range(N) if a<=ts[j] and ts[j+1]<=b] for a,b in blocks]
 bw=[sum((weights[j] for j in ix),I(0)) for ix in sel];cw=[sum((tt[j+1]-tt[j] for j in ix),I(0))-tau*b for ix,b in zip(sel,bw)]
 det=bw[0]*cw[1]-bw[1]*cw[0]
 delta=[(-bT*cw[1]+CT*bw[1])/det,(-CT*bw[0]+bT*cw[0])/det]
 uu=u0[:]
 for ix,dd in zip(sel,delta):
  for j in ix:uu[j]=uu[j]+dd
 b=I(0);charge=I(0);net=I(0);Z0=kk*p0*p0;W0=I('21.6');Wmin=I('17.496');Wmax=I('26.136')
 mins={key:I('1e9') for key in ['W_lower_kJ','W_upper_kJ','modulation_kJ','B_lower_kJ','B_upper_kJ','command_kW','power_kW','ramp_kW_per_s','current_kA2']};trace=[]
 for j in range(N):
  h=tt[j+1]-tt[j];hnum=ts[j+1]-ts[j];pe,qe,de=profile(ts[j+1]);ps,qs,ds=profile(ts[j]);pd=(pe-ps)/h;qd=(qe-qs)/h;dd=(de-ds)/h
  E=iv.exp(-h/tau);bn=E*b+(1-E)*uu[j];cn=charge+tau*(1-E)*b+(h-tau*(1-E))*uu[j]
  netn=net+h*((ps+pe-ds-de)/2-cc*(ps*ps+ps*pe+pe*pe+qs*qs+qs*qe+qe*qe)/3)
  A2=[pd-dd-2*cc*(pv*pd+qv*qd)-2*kk*(pd*pd+qd*qd) for pv,qv in [(ps,qs),(pe,qe)]]
  A2lo=min(x.a for x in A2);A2hi=max(x.b for x in A2)
  ip=pd/Gp;iq=qd/Gp;epd=-R*ip+om*L*iq;epq=-R*iq-om*L*ip;M2=3000*Cdc*(epd*epd+epq*epq)
  curves=[max(I(0),A2hi+30000),max(I(0),-A2lo+30000),max(I(0),A2hi-M2.a+30000)]
  for pv,qv,nv,cv,bv in [(ps,qs,net,charge,b),(pe,qe,netn,cn,bn)]:
   Z=kk*(pv*pv+qv*qv);W=W0+nv-Z+Z0+cv
   idd=pv/Gp;iiq=qv/Gp;ed=v-R*idd-L*ip+om*L*iiq;eq=-R*iiq-L*iq-om*L*idd;MF=1500*Cdc*(ed*ed+eq*eq)
   vals={'W_lower_kJ':W-Wmin-curves[0]*h*h/8,'W_upper_kJ':Wmax-W-curves[1]*h*h/8,'modulation_kJ':W-MF-curves[2]*h*h/8,'B_lower_kJ':50-cv-30000*h*h/8,'B_upper_kJ':50+cv-30000*h*h/8,'power_kW':450-absmax(bv),'current_kA2':I('2.25')-idd*idd-iiq*iiq}
   for key,val in vals.items():mins[key]=pmin(mins[key],val)
  mins['command_kW']=pmin(mins['command_kW'],450-absmax(uu[j]));mins['ramp_kW_per_s']=pmin(mins['ramp_kW_per_s'],30000-absmax((uu[j]-b)/tau))
  b,charge,net=bn,cn,netn
  trace.append([float(ts[j+1]),float(mp.mpf(b.mid._mpi_[0])),float(mp.mpf(charge.mid._mpi_[0])),float(mp.mpf((W0+net-kk*(pe*pe+qe*qe)+Z0+charge).mid._mpi_[0]))])
 record={'beta_kvar':808,'critical_hold_us':25,'later_hold_us':100,'intervals':N,'all_time_interval_lower_bounds':{k:enc(v) for k,v in mins.items()},'strict_all_constraints_pass':all(v.a>0 for v in mins.values()),'terminal_b_interval_kW':enc(b),'terminal_C_interval_kJ':enc(charge),'total_net_grid_minus_load_interval_kJ':enc(net),'terminal_repair_block_deltas_kW':[enc(d) for d in delta],'terminal_repair_determinant':enc(det),'exact_terminal_semantics':'u is rational base payload plus analytically defined two-block correction; the displayed interval is an enclosure of that exact command, not an independently rounded command table','gamma_interval_kW':enc(gam),'interval_decimal_precision':40,'runtime_s':time.perf_counter()-st}
 (ROOT/'results'/'zoh_q808_exact_payload.json').write_text(json.dumps({'times_decimal':[str(t) for t in ts],'base_commands_decimal_kW':us,'repair_blocks_s':[[str(a),str(b)] for a,b in blocks],'repair_definition':'weights_j=(1-exp(-h_j/tau))*exp(-(T-t_(j+1))/tau); bT=sum u_j weights_j; CT=sum h_j u_j-tau*bT; [B1 B2; C1 C2] delta=-[bT,CT], with Bm=sum weights on block and Cm=block_duration-tau*Bm; final u_j=base+delta_m on repair block','tau_s':'.005','T_s':'.2'},indent=2))
 np.savetxt(ROOT/'results'/'zoh_certified_trace.csv',np.array(trace),delimiter=',',header='t_s,b_kW,C_kJ,W_kJ',comments='')
 (ROOT/'results'/'outward_zoh_inner.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
if __name__=='__main__':main()
