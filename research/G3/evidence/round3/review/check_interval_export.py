"""Verify all exported decimal endpoints against exact binary interval endpoints."""
from pathlib import Path
from fractions import Fraction
import importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('certify_prefix_interval',ROOT/'src'/'certify_prefix_interval.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def mpf_fraction(tup):
    sign,man,exp,bc=tup
    return Fraction((-1 if sign else 1)*man)*(Fraction(2)**exp)
original=mod.enc
checks=[]
def checked(x):
    out=original(x)
    low=mpf_fraction(x.a._mpi_[0]);high=mpf_fraction(x.b._mpi_[1])
    ok=Fraction(out[0])<=low and Fraction(out[1])>=high
    checks.append(dict(outward=ok,exported=out))
    assert ok, (out,x)
    return out
mod.enc=checked
rows=[mod.certify('813',2048),mod.certify('812.5',8192)]
result=dict(all_decimal_exports_outward=all(c['outward'] for c in checks),interval_pairs_checked=len(checks),certificates=rows)
(ROOT/'review'/'interval_export_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
