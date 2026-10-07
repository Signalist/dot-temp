from pathlib import Path
import numpy as np,json
from scipy.integrate import quad
from scipy.optimize import brentq
from independent_audit import witness_audit,replay_abc
ROOT=Path(__file__).resolve().parents[1]

def independent_custom(t,p,alpha,beta):
 c=p['R']/(1500*p['v']**2);P0=brentq(lambda z:z-c*z*z-p['D0'],p['D0'],2*p['D0'])
 def pulse(s):return np.maximum(0,np.minimum(1,np.minimum((np.asarray(s)-.005)/.05,(.31-np.asarray(s))/.05)))
 def tail(s):return np.maximum(0,np.minimum(1,np.minimum((np.asarray(s)-.32)/.01,(.38-np.asarray(s))/.01)))
 # Reproduce the DEFINED piecewise-linear scheduled workload, not a smooth sine substitute.
 nodes=.08+np.arange(65)*.0025;work=np.sin((nodes-.08)*2*np.pi/.04);work[np.abs(work)<1e-12]=0
 def load(s):return p['D0']+500*np.interp(s,nodes,work,left=0,right=0)
 events=np.r_[.005,.055,nodes,.26,.31,.32,.33,.37,.38]
 def balance(gam):
  def fn(s):
   P=P0+gam*tail(s);Q=beta*pulse(s)
   return P-c*(P*P+Q*Q)-load(s)
  return quad(fn,0,p['T'],points=sorted(set(events)),epsabs=1e-10,epsrel=1e-11,limit=300)[0]
 gamma=brentq(balance,0,200,xtol=1e-11)
 return P0+gamma*tail(t),beta*pulse(t),load(t),gamma,balance(gamma)
rows=[]
claims=json.loads((ROOT/'results/switch_corridor/RESULTS.json').read_text());claim={(r['ramp'],r['beta']):r for r in claims}
for f in sorted((ROOT/'results/switch_corridor').glob('spline_*.npz')):
 w,data=witness_audit(f,independent_custom,nominal_n=160);p=data[0];c=claim[(p['ramp'],w['beta_kvar'])];w['campaign_certified']=bool(c['inner']['certified_numeric_inner'])
 if w['campaign_certified']:w['independent_SI_abc_replay']=replay_abc(data)
 rows.append(w);print(f.name,w['independent_admitted_numeric'],w.get('independent_SI_abc_replay',{}).get('max_errors_and_clipping',{}),flush=True)
 out={'witnesses':rows,'summary':{'cases_checked':len(rows),'admitted':sum(r['campaign_certified'] for r in rows),'disagreements':[r['file'] for r in rows if r['campaign_certified']!=r['independent_admitted_numeric']]}}
 (ROOT/'audit/SWITCH_CORRIDOR_AUDIT.json').write_text(json.dumps(out,indent=2))
