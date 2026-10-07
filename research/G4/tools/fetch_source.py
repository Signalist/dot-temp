#!/usr/bin/env python3
"""Optional public-source acquisition, one explicit ledger record at a time."""
from pathlib import Path
import argparse,hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--id',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-unpinned',action='store_true');a=p.parse_args()
rows=json.loads((ROOT/'provenance/PUBLIC_SOURCES.json').read_text())['sources'];rows=[x for x in rows if x['id']==a.id]
if len(rows)!=1:p.error('Choose an exact unique id from PUBLIC_SOURCES.json')
r=rows[0];dest=a.output.resolve()
if dest.exists() or dest==ROOT or ROOT in dest.parents:p.error('Destination must be new and outside the handoff')
if not r.get('sha256') and not a.allow_unpinned:p.error('No frozen source hash; --allow-unpinned is required')
if not r['url'].startswith('https://'):p.error('Only HTTPS source URLs accepted')
with urllib.request.urlopen(r['url'],timeout=60) as response:data=response.read()
h=hashlib.sha256(data).hexdigest()
if r.get('sha256') and h!=r['sha256']:raise SystemExit('Source SHA-256 mismatch; nothing saved. Investigate version/content before continuing.')
dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
print(json.dumps({'source_id':a.id,'bytes':len(data),'sha256':h,'historical_hash_verified':bool(r.get('sha256'))},indent=2))
