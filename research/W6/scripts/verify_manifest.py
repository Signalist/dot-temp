"""Verify current publication bytes; no network, hardware or mutation."""
from pathlib import Path
import hashlib, json
ROOT = Path(__file__).resolve().parents[1]

def main():
    expected = {}
    for line in (ROOT/'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split('  ', 1)
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts: raise ValueError('Unsafe manifest path')
        if name in expected: raise ValueError('Duplicate manifest path')
        expected[name] = digest
    missing = []; changed = []
    for name, digest in expected.items():
        p = ROOT/name
        if not p.is_file(): missing.append(name)
        elif hashlib.sha256(p.read_bytes()).hexdigest() != digest: changed.append(name)
    # Recheck reports/caches are allowed; frozen manifest members are immutable.
    result = {'passed':not missing and not changed,'files_verified':len(expected),'missing':missing,'changed':changed,'scope':'Current publication payload hashes only'}
    print(json.dumps(result, indent=2))
    if not result['passed']: raise SystemExit(1)

if __name__ == '__main__': main()
