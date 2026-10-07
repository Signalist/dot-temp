"""Import authorized local raw inputs only after verifying all frozen hashes."""
import argparse,hashlib,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args()
source=pathlib.Path(a.source).resolve();out=pathlib.Path(a.out)
if out.exists():raise SystemExit('Choose a new output directory')
files=json.loads((ROOT/'continuation/quality/LEGACY_INPUT_FREEZE.json').read_text())['files']
for rel,digest in files.items():
    path=(source/rel).resolve()
    if not path.is_relative_to(source):raise SystemExit('Input escapes source directory')
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise SystemExit('Missing or changed input: '+rel)
for rel in files:
    target=out/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/rel,target)
print(json.dumps({'verified_files':len(files),'network_used':False,'programs_executed':False}))
