#!/usr/bin/env python3
"""Additional direct-physics audit of primary half-SOC and fixed hardware schedules."""
from pathlib import Path
import json,hashlib
import numpy as np
from independent_theory_checks import audit_schedule
HERE=Path(__file__).resolve().parent
src=HERE.parent/'experiments/FIXED_INITIAL_RESULTS.json'
def main():
    data=json.loads(src.read_text());rows=[];failed=[]
    for category in ['fixed_half','fixed_hardware_horizon','positive_tolerance','exact']:
        for i,r in enumerate(data[category]):
            if not r['success']:
                failed.append({'category':category,'row':i,'K':r['K'],'scope':'No feasible witness supplied; infeasibility not established by this physical-simulation audit'})
                continue
            a=audit_schedule(r['p'],r['e0'],r['capacity'],r['ec'],r['ed'],r['tau'],N=r['N'],L=6,H=18,enumerate_histories=r['K']<=5)
            p=np.asarray(r['p']);peak=float(max(np.max(np.abs(p-6)),np.max(np.abs(p-18))))
            a.update(category=category,row=i,ec=r['ec'],ed=r['ed'],tau=r['tau'],capacity=r['capacity'],initial_energy=r['e0'],half_initial_error=abs(r['e0']-.5*r['capacity']),max_power=peak,rate_violation=max(0,peak-r['rate']),power_range_violation=max(0,float(6-p.min()),float(p.max()-18)))
            rows.append(a)
    tests=dict(all_supplied_witnesses_physically_feasible=all(r['capacity_violation']<1e-7 and r['recovery_violation']<1e-7 for r in rows),half_SOC=all(r['half_initial_error']<1e-8 for r in rows),rate_and_range=all(r['rate_violation']<1e-8 and r['power_range_violation']<1e-8 for r in rows),extremal_histories_realized=all(r['max_witness_error']<1e-8 for r in rows),short_horizons_exhaustive=all(r.get('enumeration_error',0)<1e-8 for r in rows),one_high_width_identity=all(r['width_vs_spread_error']<1e-8 for r in rows))
    out={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'successful_witness_count':len(rows),'unsolved_or_infeasible_rows_not_certified_by_this_audit':failed,'tests':tests,'rows':rows}
    (HERE/'FIXED_INITIAL_INDEPENDENT_AUDIT.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item()))
    print(json.dumps({'count':len(rows),'excluded_count':len(failed),'tests':tests,'max_state_violation':max(r['capacity_violation'] for r in rows),'max_recovery_violation':max(r['recovery_violation'] for r in rows)},indent=2));assert all(tests.values())
if __name__=='__main__':main()
