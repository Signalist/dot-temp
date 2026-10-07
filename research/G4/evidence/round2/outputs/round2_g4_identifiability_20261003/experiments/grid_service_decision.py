#!/usr/bin/env python3
"""Grid-relevant safe accept/abstain decision with exact rational energy certificate.
The primary smooth witness has finite PCS, equal converter state at decision,
identical past PCC and identical future tasks. No real actuation occurs.
"""
from fractions import Fraction as F
import numpy as np,pathlib,json
R=pathlib.Path(__file__).resolve().parent
eta=F(19,20);E0=F(9);B=F(18);a2=F(4);a3=F(19,2);D=F(12);r=.2;tau=.01
elow=E0-(D-a2)/eta+eta*a3
ehigh=E0+eta*a2-(D-a3)/eta
need=F(247,25);remaining=ehigh-need;recharge=(E0-remaining)/eta
service_duration=F(2);amp=eta*need/service_duration

def shape(s):
 s=np.asarray(s);h=np.zeros_like(s);dh=np.zeros_like(s);J=np.zeros_like(s)
 valid=(s>=0)&(s<=1);a=valid&(s<r);b=valid&(s>=r)&(s<=1-r);c=valid&(s>1-r)
 x=s[a];h[a]=np.sin(np.pi*x/(2*r))**2/(1-r);dh[a]=np.pi*np.sin(np.pi*x/r)/(2*r*(1-r));J[a]=(x/2-r*np.sin(np.pi*x/r)/(2*np.pi))/(1-r)
 h[b]=1/(1-r);J[b]=(s[b]-r/2)/(1-r)
 x=1-s[c];h[c]=np.sin(np.pi*x/(2*r))**2/(1-r);dh[c]=-np.pi*np.sin(np.pi*x/r)/(2*r*(1-r));J[c]=1-(x/2-r*np.sin(np.pi*x/r)/(2*np.pi))/(1-r)
 J[s>1]=1
 return h,dh,J

def command_bound(A,T=1):return float(A)*(1+np.sqrt(1+(np.pi*tau/(r*T))**2))/(2*(1-r))
def slew_bound(A,T=1):return float(A)*np.pi/(2*r*(1-r)*T)

def main():
 tt=np.linspace(0,6,60001);p_pre=np.full_like(tt,6.);h2,dh2,J2=shape(tt-1);h3,dh3,J3=shape(tt-2)
 p_pre+=float(a2)*h2+float(a3)*h3
 # Both worlds implement this same prehistory; each PCS ends at0 bydecision3.
 pre=[]
 for j in[2,3]:
  d=6+12*(h2 if j==2 else h3);b=d-p_pre;bdot=12*(dh2 if j==2 else dh3)-float(a2)*dh2-float(a3)*dh3
  E=9+((-float(D-a2)/float(eta))*J2+float(eta*a3)*J3 if j==2 else float(eta*a2)*J2-float((D-a3)/eta)*J3)
  mask=tt<=3;pre.append({'high_task_slot':j,'decision_SOC':float(E[30000]),'min_SOC_beforedecision':float(E[mask].min()),'max_SOC_beforedecision':float(E[mask].max()),'buffer_at_decision':float(b[30000]),'max_realized_buffer':float(max(abs(b[mask]))),'max_command_sampled':float(max(abs((b+tau*bdot)[mask])))})
 hs,dhs,Js=shape((tt-3)/2);hr,dhr,Jr=shape(tt-5)
 bsvc=float(amp)*hs-float(recharge)*hr
 cmdsvc=bsvc+tau*(float(amp)*dhs/2-float(recharge)*dhr)
 Pafter=6-bsvc;Eafter=float(ehigh)-float(need)*Js+float(eta*recharge)*Jr
 mask=tt>=3;allbounds={'pre_command_bound':max(command_bound(v) for v in [D-a2,a3,a2,D-a3]),'service_command_bound':command_bound(amp,2),'recovery_command_bound':command_bound(recharge),'pre_slew_bound':max(slew_bound(v) for v in [D-a2,a3,a2,D-a3]),'service_slew_bound':slew_bound(amp,2),'recovery_slew_bound':slew_bound(recharge),'service_PCC_min':6-float(amp)/(1-r),'recovery_PCC_max':6+float(recharge)/(1-r),'generic_accepted_state_worst_recovery_command':command_bound(E0/eta),'generic_accepted_state_worst_recovery_PCC':6+float(E0/eta)/(1-r)}
 epsE=.02;epsT=.006;edotbound=max(float(D-a2)/float(eta),float(eta*a3),float(eta*a2),float((D-a3)/eta))/(1-r);err=epsE+epsT*edotbound
 out={'scope':'fixed-site short-duration grid import-curtailment decision from identicalpastPCC; samefuturetasks and exact recovery, syntheticdeclaredphysicalmodel','parameters':{'eta':str(eta),'capacity':str(B),'initial_energy':str(E0),'task_work_total':48,'jobs_completed':6,'high_task_peak':21,'PCS_tau':tau,'rate_and_command_limit':12,'slew_limit':100,'recovery_deadline':6,'recovery_PCC_cap':18},'exact_energy_certificate':{'SOC_low':str(elow),'SOC_high':str(ehigh),'service_required_energy':str(need),'low_allcontrol_deficit':str(need-elow),'high_energy_margin':str(ehigh-need),'remaining_high':str(remaining),'recovery_AC_energy':str(recharge),'final_energy_exact':str(remaining+eta*recharge),'allcontrol_exclusion':'For3<=t<=5, identicalcontinuingd=6 and P<=P_req imply b=d-P>=b_req>=0; e_dot<=-b_req/eta. Integratedneed=247/25 exceedselow. No allowedcontrolor charging split canavoid this withoutviolatingcap/work/energyphysics.'},'prehistory':pre,'service':{'start':3,'end':5,'AC_import_reduction_energy':float(amp*2),'stored_energy_required':float(need),'PCC_target':'6-4.693h((t-3)/2)','samefuture_compute_power':6,'highworld_implementation':'first-orderPCS feedforward u=b_req+tau*bdot; thennegativebuffer recoverypulse; currentknownfuturetasks afterDAGjoin only','energy_afterservice':float(remaining),'recovery_charge_average':float(recharge),'finalSOC':float(Eafter[-1]),'finalbuffer':float(bsvc[-1]),'minSOC_service_and_recovery':float(Eafter[mask].min())},'analytic_bounds':allbounds,'matched_measurement':{'known_site':'A','time':3,'one_bit_both_methods':True,'SOC_threshold':float(need)+err,'query_time':2.995,'timestamp_error':.001,'delivery_guaranteed_by':2.999,'commitment_start':3,'generic_safe_accept_rule':'bit1 when measuredE>=requiredEnergy+totalStateError; bit0 meansabstain unlessotherwise resolved','SOC_error':epsE,'maximum_state_age_at_commitment':epsT,'state_slope_bound':edotbound,'total_state_error':err,'low_true_energy_exclusion_margin':float(need-elow),'low_noaccept_bit_margin':float(need-elow),'high_accept_bit_worst_error_margin':float(ehigh-need)-2*err,'continuous_SOC_safe_accept_for_all_states_above_requirement':True,'PCC_prefix_same_entirely':True,'PCC_even_zero_error_and_unlimited_bandwidth_adds_nothing':True,'decision_without_extra_info':'abstain from guaranteeing specifiedsite service; exactsameinfo robustbaseline alsoabstains','with_SOCbit':'accepthighworld/rejectlowworld underdeclaredcontract; sameinformationbaseline obtains sameanswer','sensor_cost_advantage_claim':False},'same_information_conservative_service':{'maximum_uniform_scaled_service_from_energy_bound':float(elow/need),'guaranteed_AC_energy':float(eta*elow),'requested_AC_energy':float(eta*need),'relative_uplift_for_high_state_full_accept':float(need/elow-1),'meaning':'PCC-only robustbaselinecanofferashrunkenservice; forfixedfullcommitmentitmustabstain. Recoveryatenergyboundaryisstillfeasible under samebounds.'},'no_service_baseline':{'low_excess_energy_to_discharge':float(elow-E0),'high_excess_energy_to_discharge':float(ehigh-E0),'causal_continuation':'over3..6 releaseexcessvia smoothpositivebattery pulse, allremainingtasks6, endenergy9andpower0; amplitudes eta*(E3-9)/3, wellbelowlimits'},'tests':{}}
 tests={'prefix_both_feasible':all(x['min_SOC_beforedecision']>=0 and x['max_SOC_beforedecision']<=18 for x in pre),'exact_low_impossible':need>elow,'exact_high_available':remaining>0,'exact_recovery':remaining+eta*recharge==E0,'all_commands_under12':max(v for k,v in allbounds.items() if 'command' in k)<12,'all_slews_under100':max(v for k,v in allbounds.items() if 'slew' in k)<100,'recoveryPunder18':allbounds['recovery_PCC_max']<18,'noexport_service':allbounds['service_PCC_min']>=0,'matched_SOC_robust':out['matched_measurement']['low_noaccept_bit_margin']>0 and out['matched_measurement']['high_accept_bit_worst_error_margin']>0,'same_PCSstate_atdecision':all(x['buffer_at_decision']==0 for x in pre)}
 out['tests']={k:bool(v) for k,v in tests.items()};(R/'GRID_SERVICE_DECISION_RESULTS.json').write_text(json.dumps(out,indent=2));np.savez_compressed(R/'GRID_SERVICE_WITNESS.npz',t=tt,PCC_prefix=p_pre,PCC_service_recovery=Pafter,buffer_service_recovery=bsvc,command_service_recovery=cmdsvc,energy_service_recovery=Eafter)
 print(json.dumps({k:out[k] for k in ['exact_energy_certificate','analytic_bounds','matched_measurement','tests']},indent=2));assert all(tests.values())
if __name__=='__main__':main()
