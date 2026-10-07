from pathlib import Path
import numpy as np, json, csv, itertools, math
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'experiments'
rows=[]
for delta in [.001,.01,.1]:
 l,u=np.tan(np.pi/4-delta),np.tan(np.pi/4+delta); D=u-l
 kappa=1/(1+u*u)**1.5; K=1/(1+l*l)**1.5
 for eps in [1e-2,1e-4,1e-6,1e-8]:
  m=max(1,math.ceil(D*math.sqrt(K/(8*eps))))
  ts=np.linspace(l,u,m+1); ys=np.sqrt(1+ts*ts)
  # Dense diagnostic for safe chord interpolation, proof in THEOREMS T2a.
  check=np.linspace(l,u,max(1001,100*m+1)); err=np.interp(check,ts,ys)-np.sqrt(1+check*check)
  rows.append({'orientation_halfwidth_rad':delta,'gauge_tolerance':eps,'slope_l':l,'slope_u':u,'proven_piece_lower_real':D*math.sqrt(kappa)/(4*math.sqrt(eps)),'safe_constructed_pieces':m,'proven_chord_error_upper':K*(D/m)**2/8,'dense_max_error':float(err.max()),'dense_min_error':float(err.min())})
(OUT/'ORIENTATION_CROSSOVER.json').write_text(json.dumps({'scope':'normalized exact circle-sector theorem illustration, M=1; not a fit to grid eigenvalues','rows':rows},indent=2))
with (OUT/'orientation_crossover.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

# Complementary schedule plans execute identical labeled jobs under explicit DAGs.
jobs=['H1','H2','L1','L2']; powers={j:60 if j[0]=='H' else 40 for j in jobs}; work={j:3 if j[0]=='H' else 1 for j in jobs}
plans={'port1_plus':['H1','H2','L1','L2'],'port1_minus':['L1','L2','H1','H2'],'port2_plus':['H1','L1','L2','H2'],'port2_minus':['L1','H1','H2','L2']}
DAG1=[('H1','H2'),('L1','L2')]
DAG2=DAG1+[('H1','L2'),('L1','H2')]
def legal(plan,edges):return all(plan.index(u)<plan.index(v) for u,v in edges)
ledgers=[]
for name,plan in plans.items():
 dag=DAG1 if 'port1' in name else DAG2
 ledgers.append({'plan':name,'order':plan,'edges':dag,'legal':legal(plan,dag),'duration_s':2.0,'power_MW':[powers[j] for j in plan],'energy_MJ':sum(powers[j]*.5 for j in plan),'actual_completed_job_ids':sorted(plan),'completed_work_units':sum(work[j] for j in plan),'incremental_energy_MJ':sum((powers[j]-50)*.5 for j in plan),'task_service_model':'each labeled job requires one nonpreemptive .5s slot with fixed declared power; work attached to job identity, not inferred from power'})
# Structural DAG sweep: all subsets of forward edges compatible with each plus plan.
checks=[]
for port in ['port1','port2']:
 plus,minus=plans[port+'_plus'],plans[port+'_minus']
 possible=[(plus[i],plus[j]) for i in range(4) for j in range(i+1,4)]
 for mask in range(64):
  edges=[possible[j] for j in range(6) if mask>>j&1]
  both=legal(plus,edges) and legal(minus,edges)
  common_edges=[e for e in possible if legal(minus,[e])]
  pred=all(e in common_edges for e in edges)
  checks.append({'port':port,'mask':mask,'edges':edges,'both_plans_feasible':both,'intersection_test':pred,'same_result':both==pred})
# Strict cross precedence defeats a complementary plan; never call sign authority free.
counter={'port':'port1','added_edge':['H2','L1'],'plus_feasible':legal(plans['port1_plus'],DAG1+[('H2','L1')]),'minus_feasible':legal(plans['port1_minus'],DAG1+[('H2','L1')]),'interpretation':'same job energy and total work do not authorize an illegal task order'}
(OUT/'JOB_DAG_REALIZATION.json').write_text(json.dumps({'scope':'analytical conditional job catalog; no measured GPU/PCC trace or enforcement-cost evidence; extension added after primary protocol to remove reliance on affine work accounting','ledgers':ledgers,'DAG_checks':checks,'checks_count':len(checks),'all_checks_pass':all(x['same_result'] for x in checks),'both_feasible_counts':{p:sum(x['both_plans_feasible'] for x in checks if x['port']==p) for p in ['port1','port2']},'counterexample':counter},indent=2))
print(json.dumps({'orientation_rows':len(rows),'DAG_checks':len(checks),'both_feasible_counts':{p:sum(x['both_plans_feasible'] for x in checks if x['port']==p) for p in ['port1','port2']},'counterexample':counter},indent=2))
