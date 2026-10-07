#!/usr/bin/env python3
"""Verify public handoff bytes only; this is not scientific validation."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent

def verify_manifest():
    m=json.loads((ROOT/'MANIFEST.json').read_text());bad=[]
    for x in m['files']:
        p=ROOT/x['path']
        if not p.is_file() or p.stat().st_size!=x['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:bad.append(x['path'])
    if bad:raise AssertionError({'manifest_mismatches':bad})
    return {'status':'passed','files_checked':len(m['files']),'scope':'public handoff payload bytes only, not science or historical corpus'}
if __name__=='__main__':print(json.dumps(verify_manifest(),indent=2))
