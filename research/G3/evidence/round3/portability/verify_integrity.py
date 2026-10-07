"""Verify the immutable extracted evidence bundle before any scientific replay."""
from pathlib import Path
import json, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
m=json.loads((ROOT/'PORTABLE_MANIFEST.json').read_text())
fail=[]
for name,rec in m['files'].items():
 p=ROOT/name
 if not p.is_file():fail.append('missing: '+name)
 elif p.stat().st_size!=rec['bytes'] or sha(p)!=rec['sha256']:fail.append('hash/size: '+name)
actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
expected=set(m['files'])|{'PORTABLE_MANIFEST.json','SHA256SUMS'}
for name in sorted(actual-expected):fail.append('unexpected: '+name)
for name in sorted(expected-actual):fail.append('missing: '+name)
sums={}
for line in (ROOT/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  ',1);sums[name]=digest
if set(sums)!=expected-{'SHA256SUMS'}:fail.append('SHA256SUMS file set mismatch')
for name,digest in sums.items():
 p=ROOT/name
 if not p.is_file() or sha(p)!=digest:fail.append('SHA256SUMS: '+name)
original=json.loads((ROOT/'MANIFEST.json').read_text())
for name,rec in original['files'].items():
 p=ROOT/name
 if not p.is_file() or sha(p)!=rec['sha256'] or p.stat().st_size!=rec['bytes']:fail.append('original source: '+name)
out={'all_pass':not fail,'portable_manifest_files_checked':len(m['files']),'sha256_records_checked':len(sums),'original_source_manifest_entries_checked':len(original['files']),'exact_file_count':len(actual),'failures':fail}
print(json.dumps(out,indent=2))
sys.exit(bool(fail))
