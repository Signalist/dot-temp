"""Outward mpmath interval rectangle certificate. No floating optimizer is trusted."""
from pathlib import Path
import json,time
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
mp.iv.dps=30
mp.mp.dps=60
iv=mp.iv;I=lambda x:iv.mpf(str(x))
v=I('0.690')*iv.sqrt(I(2)/3);R=I('.005');L=I('.0003');C=I('.03');tau=I('.005');omega=100*iv.pi
Gp=1500*v;cc=R/(1500*v*v);kk=L/(3000*v*v);Kap=iv.sqrt(1500*C)
p0=1300/(1+iv.sqrt(1-4*cc*650));P=p0-100;m=1-2*cc*P
nd=I(1);nq=I('-.102');norm=iv.sqrt(nd*nd+nq*nq)
left=I('.0113');right=I('.0239');w=right-left

def lo(x):return x.a

def hi(x):return x.b

def enc(x):
 scale=mp.mpf(10)**40
 return [str(mp.floor(mp.mpf(x.a._mpi_[0])*scale)/scale),str(mp.ceil(mp.mpf(x.b._mpi_[1])*scale)/scale)]

def point(x):return iv.mpf([x,x])

def positive(x):
 if x.b<=0:return I(0)
 return iv.mpf([max(I(0).a,x.a),x.b])

def certify(beta='813',N=4096,lam='0',eps='.1'):
 st=time.perf_counter();Q=I(beta);dt=w/N
 assert P.a>0 and m.a>0 and Q.a>=0 and I(lam).a>=0 and left.a>=I('.011').b
 ramp=I('.005')*(-I(400)/2+cc*p0*100-cc*(10000+Q*Q)/3)
 slope=-400+2*cc*p0*100-cc*10000-cc*Q*Q
 def H(t):return I('21.6')+ramp+(t-I('.005'))*slope-kk*(P*P+Q*Q-p0*p0)+450*t-I('4.2')+I('.75')*iv.exp(-(t-I('.011'))/tau)
 cells=[];rhsi=I(0)
 for j in range(N):
  a=left+j*dt;b=left+(j+1)*dt;t=iv.mpf([a.a,b.b]);x=(t-left)/w
  h=iv.sin(iv.pi*x)**2;hp=iv.pi/w*iv.sin(2*iv.pi*x);HH=H(t)
  if HH.a<=18:raise ValueError('Anchor interval not above18')
  # Exact integral of sine², eliminating first-order oscillation enclosure in the large baseline term.
  ih=dt/2-w/(4*iv.pi)*(iv.sin(2*iv.pi*(b-left)/w)-iv.sin(2*iv.pi*(a-left)/w))
  rhsi+=norm*ih*iv.sqrt(HH)/Kap
  z=norm*h/(2*Kap*iv.sqrt(HH))
  ad=L*nd*hp-(R*nd+omega*L*nq)*h
  aq=L*nq*hp-(R*nq-omega*L*nd)*h
  cells.append((z,ad,aq,j))
 # r(t)=int_t^right z; on each cell use interval from sum of later full cells to sum including current.
 future=I(0);E=I(0);last_zero=0
 # Rigorous analytic sign on final 1% avoids a 0/0 interval at the endpoint.
 # H>=18 follows from the interval range on the entire support (also checked).
 cot=iv.cos(iv.pi*I('.99'))/iv.sin(iv.pi*I('.99'));ratio=2*iv.pi/w*cot
 tail_ad=(-(R*nd+omega*L*nq)+L*nd*ratio)/Gp+kk*norm*P/(Kap*iv.sqrt(I(18)))
 tail_aq=((R*nq-omega*L*nd)-L*nq*ratio)/Gp
 assert tail_ad.b<0 and tail_aq.b<0
 for z,ad,aq,j in reversed(cells):
  ri=iv.mpf([future.a,(future+z*dt).b]);future+=z*dt
  if 100*j>=99*N:
   last_zero+=1;continue
  aa=ad/Gp+2*kk*z*P-ri*m
  bb=-aq/Gp-2*kk*z*Q-ri*2*cc*Q
  den=kk*z+ri*cc+I(lam)*cc
  pa=positive(aa-I(lam)*m);pb=positive(bb-I(lam)*2*cc*Q)
  if pa.b<=0 and pb.b<=0:last_zero+=1;continue
  if den.a<=0:raise ValueError('Zero denominator with positive numerator interval')
  E+=dt*(pa*pa+pb*pb)/(4*den)
 ed=v-R*P/Gp+omega*L*Q/Gp;eq=-R*Q/Gp-omega*L*P/Gp
 M=(nd*ed+nq*eq)*w/2
 dual=I(lam)*I(eps)+E;gap=M-rhsi-dual
 result={'beta_kvar':beta,'window_s':['.0113','.0239'],'direction':['1','-.102'],'lambda':lam,'epsilon_kJ':eps,'interval_precision_decimal':mp.iv.dps,'cells':N,'M_kV_s':enc(M),'RHS_interval_kV_s':enc(rhsi),'dual_interval_kV_s':enc(dual),'gap_interval_kV_s':enc(gap),'strict_exclusion':bool(gap.a>0),'prefix_only_without_recovery_budget':lam=='0','zero_positivepart_cells':last_zero,'tail_active_coefficient_upper':enc(tail_ad),'tail_reactive_coefficient_upper':enc(tail_aq),'runtime_s':time.perf_counter()-st,'arithmetic':'mpmath.iv directed intervals; interval Riemann enclosure, exact sine-squared cell weights'}
 return result
if __name__=='__main__':
 rows=[]
 for q,N in [('813',2048),('812.5',8192)]:
  r=certify(q,N);rows.append(r);print(json.dumps(r),flush=True)
 (ROOT/'results'/'outward_prefix_certificates.json').write_text(json.dumps(rows,indent=2))
