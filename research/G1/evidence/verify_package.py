"""Standard-library-only integrity verification. Does not execute scientific code."""
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parent

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 scope=json.loads((ROOT/'PACKAGE_SCOPE.json').read_text())
 for row in scope['included']:
  p=ROOT/row['path'];assert p.is_file(),row['path']
  assert p.stat().st_size==row['bytes'] and digest(p)==row['sha256'],row['path']
 for row in scope['exact_hash_duplicate_restore_map']:
  p=ROOT/row['restore_from'];assert p.stat().st_size==row['bytes'] and digest(p)==row['sha256'],row['path']
 content=ROOT/'PACKAGE_CONTENTS.json'
 if content.exists():
  for row in json.loads(content.read_text())['files']:
   p=ROOT/row['path'];assert p.is_file() and p.stat().st_size==row['bytes'] and digest(p)==row['sha256'],row['path']
 result={'passed':True,'included_source_files_verified':len(scope['included']),'audit_exact_hash_aliases_verified':len(scope['exact_hash_duplicate_restore_map']),'declared_omitted_raw_files':len(scope['omitted_scientific_raw']),'fully_self_contained':False}
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()
