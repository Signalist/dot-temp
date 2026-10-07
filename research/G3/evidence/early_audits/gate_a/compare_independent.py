from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'protocol/GATE_A_LOCKED_V2_1.json').read_text());w=d['omega_base_rad_s'];Ts=d['control_sample_s']
def first_rows(a):
 r={}
 for row in a:r.setdefault(round(float(row[0]),12),row)
 return r
records=[]
for h,tag in [(1e-5,'10us'),(5e-6,'5us')]:
 dp=ROOT/f'gate_a/preconditioned_dq/h{h:g}.npz';ap=ROOT/f'model_audit/abc_reference/revalidation_results/preconditioned_v2_1_h{tag}.npz'
 if not ap.exists():raise FileNotFoundError(ap)
 da=np.load(dp)['trace'];aa=np.load(ap)['trace'];dr=first_rows(da);ar=first_rows(aa);end=min(da[-1,0],aa[-1,0]);errors=[]
 for k in range(int(end/Ts)+1):
  t=round(k*Ts,12)
  if t not in dr or t not in ar:raise ValueError(('clock mismatch',t))
  D,A=dr[t],ar[t];iab=(2/3)*(A[1]+A[2]*np.exp(2j*np.pi/3)+A[3]*np.exp(4j*np.pi/3));idq=iab*np.exp(-1j*w*t)
  errors.append([abs(complex(D[1],D[2])-idq),abs(D[3]-A[4]),abs(D[4]-A[5]),abs(D[10]-A[10]),abs(D[11]-A[11])])
 mx=np.max(errors,axis=0)
 dj=json.loads(dp.with_suffix('.json').read_text());aj=json.loads(ap.with_suffix('.json').read_text())
 records.append(dict(max_step_s=h,shared_control_clock_samples=len(errors),max_current_vector_error_A=float(mx[0]),max_DC_energy_error_J=float(mx[1]),max_battery_power_error_W=float(mx[2]),max_PCC_P_error_W=float(mx[3]),max_PCC_Q_error_var=float(mx[4]),dq_checkpoint_s=dj['checkpoint_time_s'],abc_checkpoint_s=aj['checkpoint']['time_s'],dq_DC_stop_s=dj['last_time_s'],abc_DC_stop_s=aj['final_time_s'],dc_stop_difference_s=abs(dj['last_time_s']-aj['final_time_s']),source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [dp,ap]},scope='Independent phase-state RK4 abc versus rotating-nominal-dq DOP853. Same frozen controller equations/resources; distinct plant implementations and solvers. Control-boundary physical states and pre-promotion powers compared.'))
out={'status':'reconstructed_then_rerun','original_npz_recovered':False,'records':records,'all_tests_pass':all(r['max_current_vector_error_A']<1e-4 and r['max_DC_energy_error_J']<1e-4 and r['max_PCC_P_error_W']<.01 and r['max_PCC_Q_error_var']<.01 and r['dc_stop_difference_s']<1e-7 and r['dq_checkpoint_s']==r['abc_checkpoint_s'] for r in records)}
(ROOT/'gate_a/INDEPENDENT_COMPARISON_REVALIDATED.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
