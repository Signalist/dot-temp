from freeze_confirmation import *
from datetime import datetime,timezone
import argparse
if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('--freeze',action='store_true');a=pa.parse_args();path=OUT/'AMPLITUDE_STRESS_ADDENDUM_FREEZE.json'
 if a.freeze:
  assert not path.exists()
  rows=[generate(True,True,4.927,1.10,0.,False),generate(True,True,4.927,1.10,0.,True)]
  m={'freeze_utc':datetime.now(timezone.utc).isoformat(),'reason':'Frozen v1 +5% high-start stress gave0.0987940 Hz; probe the next explicitly out-of-contract amplitude at +10%, with immediate timestep refinement. This follow-on is outcome-informed and not in v1 holdout counts. No controller redesign.','cases':rows,'source_sha256':SHA(__file__),'v1_manifest_sha256':SHA(OUT/'CONFIRMATION_FREEZE.json')};path.write_text(json.dumps(m,indent=2));print('FROZEN',SHA(path),flush=True)
 else:
  import run_confirmation as rc
  m=json.loads(path.read_text());rows=[]
  for c in m['cases']:
   assert SHA(c['it_csv'])==c['it_sha256'] and SHA(c['bess_csv'])==c['bess_sha256']
   rows.append(rc.rp.run(c['it_csv'],c['bess_csv'],c['label'],8,c['tf_s'],c['dt_s']))
   (OUT/'AMPLITUDE_STRESS_ADDENDUM_RESULTS.json').write_text(json.dumps(rows,indent=2))
