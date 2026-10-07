"""Verify only documented new and prior dependency bytes; never run simulations."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'INCREMENT_GATE0_MANIFEST.json').read_text())
fail=[];counts={}
for key in ('new_files','prior_dependencies'):
 counts[key]=0
 for entry in m[key]:
  p=R/entry['path']
  if not p.is_file():fail.append({'path':entry['path'],'reason':'missing'});continue
  actual=hashlib.sha256(p.read_bytes()).hexdigest()
  if actual!=entry['sha256']:fail.append({'path':entry['path'],'reason':'hash mismatch'})
  counts[key]+=1
print(json.dumps({'success':not fail,'checked':counts,'failures':fail},indent=2))
sys.exit(bool(fail))
