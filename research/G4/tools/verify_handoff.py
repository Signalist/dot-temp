#!/usr/bin/env python3
"""Verify sanitized published files. Historical manifests are provenance only."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def verify():
 m=json.loads((ROOT/'PUBLIC_MANIFEST.json').read_text());bad=[]
 for row in m['files']:
  p=ROOT/row['path']
  if Path(row['path']).is_absolute() or '..' in Path(row['path']).parts:bad.append(row['path']);continue
  if not p.is_file() or p.stat().st_size!=row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:bad.append(row['path'])
 if bad:raise RuntimeError('Missing or changed handoff files: '+repr(bad))
 return len(m['files'])
if __name__=='__main__':
 print(json.dumps({'files_verified':verify(),'all_passed':True}))
