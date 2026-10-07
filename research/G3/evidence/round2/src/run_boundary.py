"""Reproduce the declared five near-boundary contracts, including rejected q810."""
from pathlib import Path
import json
from admission import solve_inner
from envelope import prefix_outer
root=Path(__file__).resolve().parents[1];rows=[]
for q in [790,800,805,808,810]:
 rows.append({'beta':q,'inner':solve_inner(100,q,320,save=root/'results'/f'boundary_a100_q{q}_n320.npz'),'prefix_outer':prefix_outer(100,q)})
(root/'results'/'BOUNDARY_RESULTS.json').write_text(json.dumps(rows,indent=2))
