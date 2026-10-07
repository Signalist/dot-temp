from pathlib import Path
import json,csv
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def load(f):return json.load(open(ROOT/'results'/f))
def run():
 p=[r for r in load('PRIMARY_MESHES.json') if r['N']==128];du=load('CONTINUOUS_DUAL.json');bas=load('BASELINES.json');atoms=load('ATOMIC_GLOBAL_BOUNDS.json');tr=load('DISTRIBUTION_TRANSFER.json');ac=load('ACCOUNTING_ABLATION.json');ref=load('REFINEMENTS_256.json')
 sg=[]
 for i,r in enumerate(p):
  c=r['case'];b=bas[i];d=du[i];dimensionless=c['c']/c['R']**(1/(1+c['beta']))
  sg.append({'beta':c['beta'],'R':c['R'],'c':c['c'],'normalized_c':dimensionless,'objective':r['parts']['objective'],'dynamic_energy':r['parts']['dynamic_energy'],'cycle_time':r['parts']['cycle_time'],'continuous_dual_relative_gap':d['relative_gap'],'constant_target_objective_reduction':1-r['parts']['objective']/b['constant_target_with_recovery']['parts']['objective'],'bellman_relative_excess':b['bellman_sub4']['objective']/r['parts']['objective']-1,'mesh_128_vs256_relative_difference':abs(r['parts']['objective']-ref[i]['precise_parts']['objective'])/r['parts']['objective']})
 with open(ROOT/'results/PRIMARY_SUMMARY.csv','w') as f:
  wr=csv.DictWriter(f,fieldnames=list(sg[0]));wr.writeheader();wr.writerows(sg)
 summary={'primary_configurations':len(p),'primary_scaling_equivalence_classes':len(set((r['beta'],round(r['normalized_c'],8)) for r in sg)),'continuous_relative_gap_range':[min(d['relative_gap'] for d in du),max(d['relative_gap'] for d in du)],'constant_target_objective_reduction_range':[min(r['constant_target_objective_reduction'] for r in sg),max(r['constant_target_objective_reduction'] for r in sg)],'same_information_bellman_relative_excess_max':max(r['bellman_relative_excess'] for r in sg),'mesh128_to256_relative_difference_max':max(r['mesh_128_vs256_relative_difference'] for r in sg),'old_task_only_objective_excess_range':[min(r['old_objective_excess_fraction'] for r in ac),max(r['old_objective_excess_fraction'] for r in ac)],'transfer_source_policy_excess_range':[min(r['source_excess_fraction'] for r in tr),max(r['source_excess_fraction'] for r in tr)],'atomic_global_relative_gap_range':[min(r['refinements'][-1]['relative_gap'] for r in atoms),max(r['refinements'][-1]['relative_gap'] for r in atoms)],'hardware_measurements':False,'outward_rounding':False,'all_numeric_counts_are_configurations_or_replays_not_statistical_independent_N':True}
 if (ROOT/'results/SAFE_PRIMARY_PATHS.json').exists():
  safe=load('SAFE_PRIMARY_PATHS.json')
  summary['safe_primary_relative_dual_gap_range']=[min(r['relative_gap'] for r in safe),max(r['relative_gap'] for r in safe)]
  summary['safe_primary_all_exact_rational_constraints_pass']=all(all(r['exact_rational_checks'].values()) for r in safe)
  summary['safe_primary_minimum_slew_margin']=min(r['minimum_slew_margin'] for r in safe)
  summary['safe_target_objective_reduction_range']=[min(1-r['parts']['objective']/b['constant_target_with_recovery']['parts']['objective'] for r,b in zip(safe,bas)),max(1-r['parts']['objective']/b['constant_target_with_recovery']['parts']['objective'] for r,b in zip(safe,bas))]
 if (ROOT/'results/MATCHED_CYCLE_FRONTIER.json').exists():
  matches=load('MATCHED_CYCLE_FRONTIER.json');good=[r for r in matches if r['target_feasible_at_requested_cycle_time']]
  summary['matched_cycle_feasible_count']=len(good);summary['matched_cycle_infeasible_target_count']=len(matches)-len(good)
  summary['matched_cycle_dynamic_saving_range']=[min(r['relative_dynamic_energy_saving'] for r in good),max(r['relative_dynamic_energy_saving'] for r in good)]
  summary['matched_cycle_allocated_facility_saving_range']=[min(r['relative_allocated_facility_energy_saving'] for r in good),max(r['relative_allocated_facility_energy_saving'] for r in good)]
 if (ROOT/'results/TRACE_DRIVEN_GLOBAL.json').exists():
  summary['trace_cases']=[{'beta':r['case']['beta'],'R':r['case']['R'],'c':r['case']['c'],'n_requests':r['requests'],'n_atoms':r['support_atoms'],'lower':r['refinements'][-1]['lower'],'upper':r['refinements'][-1]['upper'],'relative_gap':r['refinements'][-1]['relative_gap'],'weighted_objective_reduction_vs_global_target':1-r['refinements'][-1]['upper']/r['constant_target']['objective']} for r in load('TRACE_DRIVEN_GLOBAL.json')]
 (ROOT/'results/SCIENTIFIC_SUMMARY.json').write_text(json.dumps(summary,indent=2))
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
 fig,ax=plt.subplots(2,2,figsize=(12,8),layout='constrained')
 x=np.linspace(0,1,129)
 for idx in [3,4,5]:
  r=p[idx];z=np.array(r['z']);b=r['case']['beta'];power=((1+b)*z)**(1/(1+b));ax[0,0].plot(x,power,label=f"c={r['case']['c']}")
 ax[0,0].set(xlabel='Completed work x',ylabel='Actual dynamic power p',title='Full recovery-cycle profiles (beta=.5, R=4)');ax[0,0].legend()
 xx=np.arange(12);ax[0,1].bar(xx,[100*r['constant_target_objective_reduction'] for r in sg],color='#266c93');ax[0,1].set(xticks=xx,xticklabels=[str(i+1) for i in xx],xlabel='Configuration (table rows)',ylabel='Weighted objective reduction (%)',title='Against optimized target + recovery (same information)')
 for row in atoms:
  vals=row['refinements'];ax[1,0].loglog([v['intervals_per_node'] for v in vals],[100*v['relative_gap'] for v in vals],marker='o',alpha=.7)
 ax[1,0].set(xlabel='Intervals per EOS-state node',ylabel='Global upper/lower gap (%)',title='Eight atomic models: analytic global bound construction')
 ax[1,0].text(.03,.03,'Floating evaluation; not outward-rounded',transform=ax[1,0].transAxes,fontsize=8)
 labels=[f"b={r['case']['beta']}, c={r['case']['c']}" for r in ac];ax[1,1].barh(labels,[100*r['old_objective_excess_fraction'] for r in ac],color='#b86b35');ax[1,1].set(xlabel='Excess full-cycle objective (%)',title='Omitting recovery time changes the policy')
 fig.suptitle('W6 round3: exact model evidence, no GPU measurements',fontsize=15);fig.savefig(ROOT/'figures/FULL_CYCLE_EVIDENCE.png',dpi=170);plt.close(fig)
 print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
