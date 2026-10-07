"""Portable original-source transfer replay using byte-identical included inputs.
Writes a new local replay-validation directory; does not overwrite frozen evidence.
"""
from pathlib import Path
import importlib.util,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'transfer/run_transfer.py'
spec=importlib.util.spec_from_file_location('g6_original_transfer_replay',source)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
for x in json.loads((ROOT/'inputs/SOURCE_COPIES.json').read_text())['files']:
 p=ROOT/x['copy'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'],p
out=ROOT/'replay_validation'/'local_transfer';out.mkdir(parents=True,exist_ok=True)
mod.ROOT=out;mod.SOURCE=ROOT/'inputs'
which=sys.argv[1:] or ['kundur','wecc']
for name,fn in [('kundur',mod.qualify_kundur),('wecc',mod.qualify_wecc)]:
 if name in which:
  lam,R,qualification=fn();mod.run(name,lam,R,qualification)
print(out)
