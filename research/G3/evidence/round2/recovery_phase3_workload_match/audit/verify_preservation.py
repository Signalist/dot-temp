from pathlib import Path
import json,hashlib
A=Path(__file__).resolve().parent;R=A.parent;OLD=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((R/'BEFORE_PRESERVATION_SHA256.json').read_text())
z={'old_files_checked':len(a),'old_files_changed':[k for k,v in a.items() if sha(OLD/k)!=v]}
for name in ['EXECUTION_FREEZE_PHASE3.json','audit/INDEPENDENT_AUDIT_FREEZE.json']:
    x=json.loads((R/name).read_text())['files'];z[name]={'checked':len(x),'changed':[k for k,v in x.items() if sha(R/k)!=v]}
(A/'PRESERVATION_VERIFIED.json').write_text(json.dumps(z,indent=2)+'\n');print(z)
