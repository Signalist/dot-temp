"""Check the included qualified reduced model before optional network replay."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'research/grid_memory/inputs/kundur_reduced51.npz'
passed=p.is_file() and p.stat().st_size==15314 and hashlib.sha256(p.read_bytes()).hexdigest()=='31e798abc23bdcb6c3b46aeb488caf96636127390935eac4d9f0e2fdd5601828'
print(json.dumps({'passed':passed,'input':'research/grid_memory/inputs/kundur_reduced51.npz','scope':'Historical qualified reduced-model bytes; not fresh ANDES/nonlinear requalification'}))
if not passed:raise SystemExit(1)
