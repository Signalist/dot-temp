"""Compare interval profile evaluation to a narrower exact-rational-time construction."""
from pathlib import Path
from fractions import Fraction as F
import json,importlib.util
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('inner',ROOT/'src'/'certify_zoh_inner.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
payload=json.loads((ROOT/'results'/'zoh_q808_exact_payload.json').read_text())
strings=payload['times_decimal']
old=[s.profile(mp.mpf(t)) for t in strings]
mp.iv.dps=80
iv=mp.iv
I=lambda x:iv.mpf(str(x))
def IF(f):return iv.mpf(f.numerator)/f.denominator
cc=I('.005')/(1000*I('.690')**2)
p0=1300/(1+iv.sqrt(1-4*cc*650))
g2=IF(F('.030')+2*F('.005')/3);s2=2*g2;ra=I('.045');r2=IF(F('.040')+2*F('.005')/3)
qq=cc*(10000*s2+I(808)**2*g2);bb=ra*(1-2*cc*p0)
gamma=2*qq/(bb+iv.sqrt(bb**2-4*cc*r2*qq))
def pulse(t,start=F(0)):
 x=t-start
 if x<=0 or x>=F('.040'):return F(0)
 if x<F('.005'):return x/F('.005')
 if x<=F('.035'):return F(1)
 return (F('.040')-x)/F('.005')
def rawf(t):
 g=pulse(t);gm=pulse(t,F('.070'))
 if t<=F('.125') or t>=F('.175'):r=F(0)
 elif t<F('.130'):r=(t-F('.125'))/F('.005')
 elif t<=F('.170'):r=F(1)
 else:r=(F('.175')-t)/F('.005')
 return p0+100*IF(gm-g)+gamma*IF(r),IF(808*g),IF(650+300*(g-gm))
def fm(tup):
 sign,man,exp,_=tup
 return F((-1 if sign else 1)*man)*F(2)**exp
fails=[]
for st,oo in zip(strings,old):
 nn=rawf(F(st))
 for axis,(a,b) in enumerate(zip(oo,nn)):
  if not (fm(a._mpi_[0])<=fm(b._mpi_[0]) and fm(a._mpi_[1])>=fm(b._mpi_[1])):
   fails.append(dict(time=st,axis=axis,outer=str(a),reference=str(b)))
r=dict(nodes=len(strings),comparisons=3*len(strings),all_enclose_exact_rational_time_reference=not fails,failure_count=len(fails),failures=fails[:20],reference_interval_precision_digits=80)
(ROOT/'review'/'profile_rational_audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
