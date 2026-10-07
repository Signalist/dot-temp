from pathlib import Path
import sys,json,hashlib,argparse,time,os,shutil
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
GRID=OUT.parents[1]/'round2_20261003/grid_transfer';sys.path.insert(0,str(GRID))
HOME=OUT/"andes_home"
if not HOME.exists():shutil.copytree(GRID/"home",HOME)
import replay_pwl_storage as rp
os.environ["HOME"]=str(HOME)
os.environ["MPLCONFIGDIR"]=str(HOME/"mpl")
from andes.utils.paths import get_pycode_path
assert Path(get_pycode_path()).is_relative_to(HOME)
rp.OUT=OUT/'nonlinear_replay';rp.OUT.mkdir(exist_ok=True)
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('--start',type=int,default=0);pa.add_argument('--stop',type=int,default=999);a=pa.parse_args()
 manifest=json.loads((OUT/'CONFIRMATION_FREEZE.json').read_text());results=[]
 for index,c in enumerate(manifest['cases']):
  if index<a.start or index>=a.stop:continue
  assert SHA(c['it_csv'])==c['it_sha256'] and SHA(c['bess_csv'])==c['bess_sha256']
  tic=time.time();print('START',index,c['label'],flush=True)
  try:r=rp.run(c['it_csv'],c['bess_csv'],c['label'],8,c['tf_s'],c['dt_s']);r['wall_seconds']=time.time()-tic
  except Exception as e:r={'label':c['label'],'exception':repr(e),'success':False,'wall_seconds':time.time()-tic}
  results.append(r);(OUT/f'confirmation_results_{a.start}_{a.stop}.json').write_text(json.dumps(results,indent=2));print('END',index,time.time()-tic,flush=True)
