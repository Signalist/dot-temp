from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'INCREMENT_PORT_CURRENT_MANIFEST.json').read_text())
for group in ['new_files','base_v2_dependencies']:
 for f in m[group]:
  p=R/f['path']
  assert p.exists(), f"Missing {group}: {p}; restore the base G3 v2 before using this increment"
  assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],f"Hash mismatch: {p}"
print('All new files and base-v2 dependencies verified; no simulation executed')
