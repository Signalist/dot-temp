from pathlib import Path
import json,csv,hashlib
import numpy as np
R=Path(__file__).resolve().parent
BASE=R.parent
OLD=BASE/'recovery_phase2'/'V2'
PBASE=654498.72485653043

def load(folder,tag,suff=''):
 z=np.load(folder/(tag+suff+'.npz'));return {k:z[k] for k in z.files}
def snapshot(z,t):
 k=int(np.argmin(abs(z['t']-t)));assert abs(z['t'][k]-t)<1e-9;return{k1:float(v[k]) for k1,v in z.items()}
def workload_definition():
 z=np.genfromtxt(R/'original_input.csv',delimiter=',',names=True);t=z['t'];d=z['d'];T=.2
 knots=np.unique(np.r_[0,t[(t>0)&(t<T)],T]);dk=np.interp(knots,t,d);area=np.r_[0,np.cumsum(np.diff(knots)*(dk[:-1]+dk[1:])/2)];delta=area-650000*knots
 def cum(tt):
  q=np.clip(np.asarray(tt),0,T);k=np.clip(np.searchsorted(knots,q,side='right')-1,0,len(knots)-2);h=q-knots[k];sl=(dk[k+1]-dk[k])/(knots[k+1]-knots[k]);return delta[k]+(dk[k]-650000)*h+.5*sl*h*h
 candidates=list(knots)
 for k in range(len(knots)-1):
  if (dk[k]-650000)*(dk[k+1]-650000)<0:candidates.append(knots[k]+(650000-dk[k])*(knots[k+1]-knots[k])/(dk[k+1]-dk[k]))
 info={'definition':'dS(t)=dL(t)=same original Signal.at(t-onset)[2] on[0,.2); otherwise650000W; dF(t)=650000W','file_end_s':float(t[-1]),'file_full_workload_energy_J':float(np.trapezoid(d,t)),'service_end_s':T,'service_workload_energy_J':float(area[-1]),'flat_service_workload_energy_J':650000*T,'S_minus_F_service_energy_J':float(delta[-1]),'max_abs_cumulative_S_minus_F_J':float(max(abs(cum(np.array(candidates))))),'d_service_min_W':float(min(dk)),'d_service_max_W':float(max(dk)),'function_equality_not_bitwise_quadrature':'All S and L input times map to same source row and interpolation expression; independently switched numerical subgrids need not yield bitwise equal cumulative integrals'}
 return cum,info

def periodic(a,end):
 t=a['t'];m=(t>end-.1-1e-10)&(t<=end+1e-10);tar=t[m]-.02;r={k:float(np.max(abs(a[k][m]-np.interp(tar,t,a[k])))) for k in ['W','B','ia','ib','ic']};r['qualified']=r['W']<=.1 and r['B']<=.1 and max(r[k] for k in ['ia','ib','ic'])<=.2;return r

def absolute_window(a,sp,start,end):
 x,y=snapshot(sp,start),snapshot(sp,end);out={}
 for k in ['grid_energy','loss_energy','load_energy','battery_energy','bridge_energy']:
  out[k+'_J']=y[k]-x[k]
 for k in ['W','B','filter_energy']:out['change_'+k+'_J']=y[k]-x[k]
 out['net_after_copper_J']=out['grid_energy_J']-out['loss_energy_J'];out['stored_change_J']=sum(out['change_'+k+'_J'] for k in ['W','B','filter_energy']);out['physical_identity_residual_J']=out['stored_change_J']-out['grid_energy_J']+out['loss_energy_J']+out['load_energy_J']
 return out

def pair_window(a,b,sa,sb,start,end):
 aa=absolute_window(a,sa,start,end);bb=absolute_window(b,sb,start,end);tt=a['t'];prev=np.r_[2,tt[:-1]];weight=np.maximum(0,np.minimum(tt,end)-np.maximum(prev,start));dp=a['Pmean']-b['Pmean'];d={k:aa[k]-bb[k] for k in aa};d['absolute_net_grid_energy_J']=abs(d['grid_energy_J']);d['positive_grid_energy_J']=float(weight@np.maximum(dp,0));d['absolute_integral_grid_energy_J']=float(weight@abs(dp));d['cycle_mean_signed_integral_J']=float(weight@dp);d['max_abs_incremental_cP_W']=float(max(abs((a['cp']-b['cp'])[weight>0]),default=0));return d

def bounds(x,ramp):
 e=x['all'];r={'Vmin':e['Vmin']>=1080,'Vmax':e['Vmax']<=1320,'Iphase':e['Iphase']<=1500,'Ispace':e['Ispace']<=1500,'Bmin':e['Bmin']>=0,'Bmax':e['Bmax']<=1e5,'b':e['bpeak']<=450000+1e-6,'u':e['u']<=450000+1e-6,'slew':e['bdot']<=ramp+1e-6,'PWM':e['mod']<=1+1e-9,'circular':e['circular']<=1+1e-9};r['pass']=all(r.values());return r

def assess(c,cum):
 tag=c['tag'];data={k:load(OLD if k!='L' else R,tag+({'F':'_s0','S':'_s1','L':'_L'}[k])) for k in ['F','L','S']};sp={k:load(OLD if k!='L' else R,tag+({'F':'_s0','S':'_s1','L':'_L'}[k]),'_snapshots') for k in data};dense={k:load(OLD if k!='L' else R,tag+({'F':'_s0','S':'_s1','L':'_L'}[k]),'_dense') for k in data};ext={k:json.loads(((OLD if k!='L' else R)/(tag+({'F':'_s0','S':'_s1','L':'_L'}[k])+'.json')).read_text()) for k in data};on=2+c['offset_s'];end=on+.2;deadline=on+.7;final=on+.9
 assert all(np.array_equal(data['S']['t'],data[k]['t']) for k in data);assert all(np.array_equal(dense['S']['t'],dense[k]['t']) for k in data)
 initial_equal=all(all(sp[k][f][0]==sp['S'][f][0] for f in sp['S']) for k in data)
 loaderr=float(np.max(abs(data['S']['load_energy']-data['L']['load_energy'])));expected=650000*(data['S']['t']-2)+cum(data['S']['t']-on);exacterr={k:float(np.max(abs(data[k]['load_energy']-expected))) for k in ['S','L']}
 allbounds={k:bounds(ext[k],c['ramp_W_per_s']) for k in data};track={}
 for k in data:
  bins=load(OLD if k!='L' else R,tag+({'F':'_s0','S':'_s1','L':'_L'}[k]),'_bins');p=float(max(abs(bins['Pmean']-bins['Pcmdmean'])));q=float(max(abs(bins['Qmean']-bins['Qcmdmean'])));track[k]={'max_P20ms_error_W':p,'max_Q20ms_error_var':q,'pass':p<=2000 and q<=10000}
 diffs={}
 for name,a,b in [('S-L','S','L'),('L-F','L','F'),('S-F','S','F')]:diffs[name]={k:float(max(abs(dense[a][k]-dense[b][k]))) for k in ['W','B','ia','ib','ic','b','jd','jq','zw','cp','ub','da','db','dc','filter_energy']}
 d=diffs['S-L'];ret=d['W']<=2 and d['B']<=2 and max(d[k] for k in ['ia','ib','ic'])<=2
 windows={'pre_onset':(2,on),'service':(on,end),'recovery':(end,deadline),'post_deadline':(deadline,final),'declared_onset_total':(on,final),'checkpoint_total':(2,final)};ledger={};triangle_max=0
 for name,(start,finish) in windows.items():
  ab={k:absolute_window(data[k],sp[k],start,finish) for k in data};pairs={p:pair_window(data[a],data[b],sp[a],sp[b],start,finish) for p,a,b in [('S-L','S','L'),('L-F','L','F'),('S-F','S','F')]};res={key:pairs['S-F'][key]-pairs['S-L'][key]-pairs['L-F'][key] for key in ab['S']};triangle_max=max(triangle_max,max(abs(v) for v in res.values()));ledger[name]={'start_absolute_s':start,'end_absolute_s':finish,'absolute_branches':ab,'paired_increments':pairs,'signed_triangle_residuals_J':res}
 cost=ledger['recovery']['paired_increments']['S-L'];budget=cost['absolute_net_grid_energy_J']<=100 and cost['positive_grid_energy_J']<=100 and cost['absolute_integral_grid_energy_J']<=100 and cost['max_abs_incremental_cP_W']<=5000
 ep={label:{k:snapshot(sp[k],t) for k in data} for label,t in [('checkpoint',2),('onset',on),('service_end',end),('deadline',deadline),('final',final)]}
 per={k:periodic(data[k],deadline) for k in data};numerics=all(ext[k]['all']['closure']<=.1 for k in data);passed=all(allbounds[k]['pass'] and track[k]['pass'] for k in data) and ret and budget and initial_equal and loaderr<=1e-5 and triangle_max<=1e-8 and numerics and per['L']['qualified']
 return {**c,'initial_checkpoint_equal_all_branches':initial_equal,'mathematically_identical_S_L_workload':True,'max_cumulative_S_L_load_energy_difference_J':loaderr,'max_numeric_load_error_vs_exact_function_J':exacterr,'physical_bounds':allbounds,'tracking':track,'dense_final100ms_differences':diffs,'physical_S_L_return_pass':ret,'S_L_recovery_budget_pass':budget,'L_final_periodicity':per['L'],'branch_final_periodicity':per,'numeric_energy_closure_pass':numerics,'signed_triangle_residual_max_J':triangle_max,'pass':bool(passed),'ledger':ledger,'endpoint_states':ep,'extrema':ext}

def main():
 p=json.loads((R/'PROTOCOL_PHASE3.json').read_text());cum,w=workload_definition();cases=[assess(c,cum) for c in p['configurations']];conv=[]
 for c in cases:
  if c['dt_s']!=1e-6:continue
  fine=c['tag'][:-2]+'h05';a=load(R,c['tag']+'_L');b=load(R,fine+'_L');conv.append({'coarse':c['tag'],'fine':fine,'max_abs_L_difference':{k:float(max(abs(a[k]-b[k]))) for k in ['W','B','ia','ib','ic','Pmean','Qmean','cp']}})
 before=json.loads((R/'BEFORE_PRESERVATION_SHA256.json').read_text());changed=[f for f,h in before.items() if hashlib.sha256((BASE/f).read_bytes()).hexdigest()!=h]
 out={'stage':'Phase3 retrospective workload-matched comparator','case_count':len(cases),'all_comparator_contracts_pass':all(c['pass'] for c in cases),'no_new_blind_confirmation':True,'workload_definition_audit':w,'prior_files_checked':len(before),'prior_files_changed':changed,'cases':cases,'L_convergence':conv};(R/'SUMMARY_PHASE3.json').write_text(json.dumps(out,indent=2)+'\n')
 rows=[]
 for c in cases:
  for window,lg in c['ledger'].items():
   for branch,a in lg['absolute_branches'].items():rows.append({'case':c['tag'],'window':window,'row_type':'absolute_branch','branch_or_pair':branch,**a})
   for pair,a in lg['paired_increments'].items():rows.append({'case':c['tag'],'window':window,'row_type':'paired_increment','branch_or_pair':pair,**a})
 fields=list(dict.fromkeys(k for row in rows for k in row))
 with (R/'ENERGY_ATTRIBUTION_PHASE3.csv').open('w') as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
 rows=[]
 for c in cases:
  d=c['dense_final100ms_differences']['S-L'];e=c['ledger']['recovery']['paired_increments']['S-L'];rows.append({'case':c['tag'],'pass':c['pass'],'L_bounds_pass':c['physical_bounds']['L']['pass'],'SL_return_pass':c['physical_S_L_return_pass'],'SL_budget_pass':c['S_L_recovery_budget_pass'],'load_energy_discrepancy_J':c['max_cumulative_S_L_load_energy_difference_J'],'max_dW_J':d['W'],'max_dB_J':d['B'],'max_di_A':max(d[k] for k in ['ia','ib','ic']),'signed_recovery_J':e['grid_energy_J'],'positive_recovery_J':e['positive_grid_energy_J'],'absolute_recovery_J':e['absolute_integral_grid_energy_J'],'max_incremental_cP_W':e['max_abs_incremental_cP_W']})
 with (R/'ACCEPTANCE_PHASE3.csv').open('w') as f:wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 print(json.dumps({'case_count':len(cases),'all_pass':out['all_comparator_contracts_pass'],'workload':w,'changed_prior_files':changed},indent=2));
 for c in cases:print(c['tag'],c['pass'],c['ledger']['recovery']['paired_increments']['S-L']['absolute_integral_grid_energy_J'])
if __name__=='__main__':main()
