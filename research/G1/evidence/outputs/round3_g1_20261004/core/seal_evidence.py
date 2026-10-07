"""Hash final science outputs; package core and partitioned raw traces without caches."""
from pathlib import Path
import json,hashlib,zipfile,time
R=Path(__file__).resolve().parents[1];P=R/'packages';P.mkdir(exist_ok=True)
def eligible(p):
 rel=p.relative_to(R);return p.is_file() and not any(x in rel.parts for x in ['packages','__pycache__','andes_home','mplcache']) and p != R/'MANIFEST.json' and not p.name.endswith('.pyc')
files=sorted(p for p in R.rglob('*') if eligible(p));entries=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest=dict(date_utc='2026-10-04',scope='G1 round3 scientific dossier, proofs, code, raw certificates and24 original nonlinear observable traces; no environments/caches',files=entries,excluded=['runtime caches and __pycache__','packages themselves','self hash'],dependencies='README.md and network_transfer/REPRODUCE.md; qualified round2 model/adapter/ANDES environment remain external and unchanged')
(R/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));files.append(R/'MANIFEST.json')
raw=[p for p in files if 'network_transfer/nonlinear_replay' in str(p.relative_to(R)) and p.suffix=='.npz'];core=[p for p in files if p not in raw]
groups=[];cur=[];size=0
for p in raw:
 if cur and size+p.stat().st_size>29*1024**2:groups.append(cur);cur=[];size=0
 cur.append(p);size+=p.stat().st_size
if cur:groups.append(cur)
sets=[('G1_R3_core.zip',core)]+[(f'G1_R3_raw_{i+1}_of_{len(groups)}.zip',g) for i,g in enumerate(groups)];archives=[]
for name,ps in sets:
 path=P/name
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in ps:z.write(p,'G1_R3/'+str(p.relative_to(R)))
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for p in ps:assert hashlib.sha256(z.read('G1_R3/'+str(p.relative_to(R)))).hexdigest()==hashlib.sha256(p.read_bytes()).hexdigest()
 archives.append(dict(filename=name,files=len(ps),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
index=dict(scientific_files=len(entries),scientific_bytes=sum(e['bytes'] for e in entries),archives=archives,raw_archive_count=len(groups),restore='Extract core plus all raw parts to the same folder. No copied simulator environment; see explicit external dependencies.',verified='ZIP CRC and every archived SHA checked against current file bytes',manifest_sha256=hashlib.sha256((R/'MANIFEST.json').read_bytes()).hexdigest())
(P/'PACKAGE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2));print(json.dumps(index,indent=2))
