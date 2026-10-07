"""Reproduce the earlier d-axis bound; sharper vector family is in theory/."""
import sys,json
from pathlib import Path
from scipy.optimize import brentq
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'theory'))
from weak_modulation_certificate import certificate
rows=[]
for eps in [0,.001,.01,.1,1.]:
 b=brentq(lambda q:certificate(eps,beta=q)['margin_kV_s'],800,1000)
 rows.append(dict(epsilon_kJ=eps,beta_exclusion_threshold_fixed_test_kvar=b,examples=[certificate(eps,beta=q) for q in [800,825,850,875,900]]))
(root/'results'/'ALLOCATION_SLACK_FRONTIER.json').write_text(json.dumps(rows,indent=2))
