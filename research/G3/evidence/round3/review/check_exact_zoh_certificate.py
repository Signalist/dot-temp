"""Replay final held-command certificate, audit output rounding, and check payload events."""
from pathlib import Path
from fractions import Fraction
import importlib.util,json,shutil
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('certify_zoh_inner',ROOT/'src'/'certify_zoh_inner.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
REPLAY=ROOT/'review'/'inner_replay';(REPLAY/'results').mkdir(parents=True,exist_ok=True)
shutil.copyfile(ROOT/'results'/'zoh_q808_h25.npz',REPLAY/'results'/'zoh_q808_h25.npz')
mod.ROOT=REPLAY
original=mod.enc
checks=[]
def fmp(t):
 sign,man,exp,bc=t
 return Fraction((-1 if sign else 1)*man)*(Fraction(2)**exp)
def checked(x):
 out=original(x);lo=fmp(x.a._mpi_[0]);hi=fmp(x.b._mpi_[1])
 ok=Fraction(out[0])<=lo and Fraction(out[1])>=hi
 checks.append(dict(outward=ok,exported=out))
 return out
mod.enc=checked
mod.main()
payload=json.loads((REPLAY/'results'/'zoh_q808_exact_payload.json').read_text())
t=list(map(Fraction,payload['times_decimal']));u=list(map(Fraction,payload['base_commands_decimal_kW']))
required=list(map(Fraction,['0','.001','.005','.035','.040','.070','.075','.105','.110','.125','.130','.170','.175','.2']))
cert=json.loads((REPLAY/'results'/'outward_zoh_inner.json').read_text())
result=dict(all_decimal_exports_outward=all(v['outward'] for v in checks),interval_pairs_checked=len(checks),
            failed_exports=[v for v in checks if not v['outward']],
            event_alignment=all(q in t for q in required),strictly_increasing_grid=all(b>a for a,b in zip(t[:-1],t[1:])),
            queue_command_exactly_zero=all(uj==0 for a,b,uj in zip(t[:-1],t[1:],u) if b<=Fraction('.001')),
            grid_critical_holds_correct=all(b-a==Fraction('.000025') for a,b in zip(t[:-1],t[1:]) if b<=Fraction('.04')),
            grid_later_holds_correct=all(b-a==Fraction('.0001') for a,b in zip(t[:-1],t[1:]) if a>=Fraction('.04')),
            exact_payload_matches_parent=payload==json.loads((ROOT/'results'/'zoh_q808_exact_payload.json').read_text()),
            strict_all_constraints_pass=cert['strict_all_constraints_pass'],
            all_time_interval_lower_bounds=cert['all_time_interval_lower_bounds'])
(ROOT/'review'/'exact_zoh_certificate_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('AUDIT SUMMARY',json.dumps(result,indent=2))
