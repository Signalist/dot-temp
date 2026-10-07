"""Exact polynomial command construction; decimals are approximations, not exact coefficients."""
from pathlib import Path
import json
import mpmath as mp
mp.mp.dps=65;ROOT=Path(__file__).resolve().parents[1]
h=mp.mpf('.005');aa=mp.exp(-h/mp.mpf('.004'));bb=mp.exp(-h/mp.mpf('.006'));A=-100/(1+aa+bb)
u=[A,-A*(1+aa+bb),A*(aa+bb+aa*bb),-A*aa*bb]
def end(tau):
 z=mp.exp(-h/tau);bT=(1-z)*A*(z-1)*(z-aa)*(z-bb)
 return {'tau_s':str(tau),'bT_kW_approx':str(bT),'CT_kJ_approx':str(-tau*bT)}
out={'scope':'Classical pure-lag exact illustration; finite parameter checks do not prove continuum exact reset','exact_definition':'h=.005; a=exp(-h/.004); b=exp(-h/.006); A=-100/(1+a+b); (u0,u1,u2,u3)=A*(1,-(1+a+b),a+b+a*b,-a*b); p(z)=A*(z-1)*(z-a)*(z-b). Then b(T;tau)=(1-exp(-h/tau))*p(exp(-h/tau)) and integral u=h*p(1)=0 exactly.','times_s':['0','.005','.01','.015','.02'],'commands_kW_approximations':[str(x) for x in u],'exact_reset_parameters_s':['.004','.006'],'interior_parameter_failure_s':'.005','endpoints':[end(mp.mpf(q)) for q in ['.004','.005','.006']],'precision_digits':65,'previous_floating_nullspace_attempt_retained':'finite_parameter_reset_float_attempt.json'}
(ROOT/'results'/'finite_parameter_reset_counterexample.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
