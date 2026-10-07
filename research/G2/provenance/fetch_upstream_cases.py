#!/usr/bin/env python3
"""Optional official pinned-workbook download, hash-check before write. Never runs content."""
from pathlib import Path
import argparse,hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True,type=Path);a=p.parse_args()
a.directory.mkdir(parents=True,exist_ok=True)
for c in json.loads((ROOT/'UPSTREAM.json').read_text())['cases']:
    dest=a.directory/(c['name']+'_full.xlsx')
    if dest.exists():raise SystemExit('Refusing overwrite: '+str(dest))
    url='https://raw.githubusercontent.com/CURENT/andes/v2.0.0/'+c['case_path']
    with urllib.request.urlopen(url,timeout=60) as f:data=f.read()
    actual=hashlib.sha256(data).hexdigest()
    if actual!=c['case_sha256']:raise SystemExit('Checksum mismatch for '+c['name']+'; no file written')
    dest.write_bytes(data);print(c['name'],actual,len(data))
