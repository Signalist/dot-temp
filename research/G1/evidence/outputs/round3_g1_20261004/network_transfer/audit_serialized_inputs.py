"""Audit actual 12-significant-digit replay CSVs, preserving model-array metrics."""
from pathlib import Path
import numpy as np,json,hashlib
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent;ETA=.95;TAU=.05;CMD_TOL=1e-9;SOC_TOL=1e-8
rows=[]
for filename in ['CONFIRMATION_FREEZE.json','AMPLITUDE_STRESS_ADDENDUM_FREEZE.json']:
 for c in json.loads((OUT/filename).read_text())['cases']:
  path=Path(c['bess_csv']);assert hashlib.sha256(path.read_bytes()).hexdigest()==c['bess_sha256'];z=np.genfromtxt(path,delimiter=',',skip_header=1);t=z[:,0];p=z[:,1];h=np.diff(t);sl=np.diff(p)/h;v0=p[:-1]+TAU*sl;v1=p[1:]+TAU*sl;areas=h*(p[:-1]+p[1:])/2;debt=np.where(areas>=0,areas/ETA,areas*ETA);cum=np.r_[0,np.cumsum(debt)]
  maxcmd=float(max(np.max(abs(v0)),np.max(abs(v1))));terminal=float(cum[-1]);row={'label':c['label'],'manifest':filename,'bess_csv_sha256':c['bess_sha256'],'serialized_max_command_MW':maxcmd,'serialized_terminal_depletion_MWs':terminal,'serialized_pairwise_sum_terminal_depletion_MWs':float(np.sum(debt)),'serialized_energy_excursion_MWs':float(np.ptp(cum)),'command_within_numerical_tolerance':maxcmd<=50+CMD_TOL,'recovery_within_numerical_tolerance':abs(terminal)<=SOC_TOL,'original_model_array_max_command_MW':c['physics']['max_command_MW'],'original_model_array_return_error_MWs':c['physics']['return_error_MWs']};rows.append(row)
result={'audit_utc':datetime.now(timezone.utc).isoformat(),'scope':'Actual replay CSVs serialized to12 significant digits; model-array and analytic formula metrics are preserved separately. Exact formula recovery becomes a tiny rounding residual in serialized inputs.','n_case_records':len(rows),'command_numerical_tolerance_MW':CMD_TOL,'terminal_recovery_numerical_tolerance_MWs':SOC_TOL,'max_serialized_command_MW':max(r['serialized_max_command_MW'] for r in rows),'max_abs_serialized_terminal_depletion_MWs':max(abs(r['serialized_terminal_depletion_MWs']) for r in rows),'all_within_declared_numerical_tolerances':all(r['command_within_numerical_tolerance'] and r['recovery_within_numerical_tolerance'] for r in rows),'inputs_modified':False,'original_model_array_metrics_modified':False,'rows':rows}
assert result['all_within_declared_numerical_tolerances'];(OUT/'SERIALIZED_INPUT_NUMERICAL_AUDIT.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k!='rows'})
