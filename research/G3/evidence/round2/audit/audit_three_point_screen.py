from pathlib import Path
import numpy as np,json
ROOT=Path(__file__).resolve().parents[1];rows=[]
for f in sorted((ROOT/'results/switch_corridor').glob('spline*.npz')):
 z=np.load(f);p=json.loads(str(z['par_json']));t=z['t'];n=len(t);h=np.diff(t);i=np.column_stack([z['p'],z['q']])/(1500*p['v']);di=np.diff(i,axis=0)
 W0=500*p['Cdc']*p['vdc0']**2;Wmin=500*p['Cdc']*p['vdcmin']**2;Wmax=500*p['Cdc']*p['vdcmax']**2
 Wnode=np.r_[z['Wpoly'][:,0],sum(z['Wpoly'][-1])];A=Wnode-W0-z['charge'];floor=np.zeros(n)
 for k in range(n-1):
  for j in [k,k+1]:
   e=np.array([p['v'],0])-p['R']*i[j]-p['L']*di[k]/h[k]-p['omega']*p['L']*np.array([-i[j,1],i[j,0]])
   floor[j]=max(floor[j],1500*p['Cdc']*(e@e))
 low=np.maximum.reduce([np.full(n,Wmin)-W0-A,floor-W0-A,np.full(n,p['B0']-p['Bmax'])]);high=np.minimum(Wmax-W0-A,p['B0']-p['Bmin'])
 for j in np.where(t<=p['delay']+1e-12)[0]:low[j]=max(low[j],0);high[j]=min(high[j],0)
 low[-1]=max(low[-1],0);high[-1]=min(high[-1],0)
 best={'violation_kJ':-np.inf}
 for j in range(1,n-1):
  aa=t[j]-t[:j,None];bb=t[None,j+1:]-t[j];wa=bb/(aa+bb);wb=aa/(aa+bb);tol=p['ramp']*aa*bb/2
  margins=[low[j]-(wa*high[:j,None]+wb*high[None,j+1:]+tol),(wa*low[:j,None]+wb*low[None,j+1:]-tol)-high[j]]
  for side,m in enumerate(margins):
   ix=np.unravel_index(np.argmax(m),m.shape);val=float(m[ix])
   if val>best['violation_kJ']:best={'violation_kJ':val,'times_s':[float(t[ix[0]]),float(t[j]),float(t[j+1+ix[1]])],'direction':'middle_lower_vs_outer_upper' if side==0 else 'middle_upper_vs_outer_lower'}
 rows.append({'file':f.name,'ramp_kW_s':p['ramp'],'beta_kvar':float(z['beta']),**best,'excluded':best['violation_kJ']>1e-6})
out={'scope':'All ordered triples of recorded grid nodes, not merely symmetric triples. Necessary |C second derivative|<=r plus two-sided DC/modulation/inventory corridor and fixed endpoint C=0. No lag-strip, b bounds, or full multi-cell constraints.','rows':rows}
(ROOT/'audit/THREE_POINT_SCREEN.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
