from pathlib import Path
import sys,json,csv,os,hashlib
os.environ.setdefault('MPLCONFIGDIR','.cache/g3_mpl_cache');os.environ.setdefault('XDG_CACHE_HOME','.cache/g3_xdg_cache')
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'gate_a'));from dq_bench import signals,cnormclip
D=json.loads((R/'protocol/GATE_A_LOCKED_V2_1.json').read_text());I=D['I_phase_peak_base_A'];Vb=D['V_phase_peak_base_V'];w=D['omega_base_rad_s'];cname='fast_p_priority';p=R/f'baseline_allocation/results/{cname}_h1e-05.npz';z=np.load(p);ep=z['endpoint_trace'];st=z['normalized_state'];ct=z['control'];dense=z['dense_trace'];out=R/'baseline_allocation/results';rows=[];maxdiff=0.
for j,c in enumerate(ct):
 t=c[0];n=st[j,1:];y=ep[j,1:14];assert abs(ep[j,0]-t)<1e-11;rot0=np.exp(1j*w*t)
 ctl={'theta':n[4]+w*t,'zpll':n[5]*w,'zi':complex(n[6],n[7])*Vb,'applied':complex(n[8],n[9])*rot0,'queued':complex(n[10],n[11])*rot0,'omega':n[12]*w,'pb_command':n[13]*1e6}
 vs=.4 if .60005<=t<.75005 else 1.;i,vdc,u,v,pi,s,ps=signals(t,y,ctl,D,vs);rot=np.exp(1j*(w*t-ctl['theta']));ic=i*rot;vc=v*rot;mag=abs(vc);vn=max(mag,.1*Vb);errpll=vc.imag/vn;wu=w+D['pll_Kp_per_s']*errpll+ctl['zpll'];wn=np.clip(wu,2*np.pi*45,2*np.pi*75)
 a0=800000/(1.5*vn);b0=700000/(1.5*vn);a=np.clip(a0,-.95*I,.95*I);b=np.clip(b0,-np.sqrt(max(0,(.95*I)**2-a*a)),np.sqrt(max(0,(.95*I)**2-a*a)));ir=(a-1j*b)*vc/max(mag,1e-30)
 uu=vc+1j*wn*D['filter_L_H']*ic+D['current_Kp_ohm']*(ir-ic)+ctl['zi'];umax=.95*vdc/np.sqrt(3);us=cnormclip(uu,umax);aw=D['current_Kaw_per_s']*(us-uu);sr=1.5*vc*np.conj(ir)
 maxdiff=max(maxdiff,abs(a-c[5]),abs(b-c[6]),abs(abs(ir)/I-c[1]),abs(abs(us)/max(abs(uu),1e-30)-c[2]))
 rows.append([t,(t-.60005)*1000,np.hypot(a0,b0)/I,abs(ir)/I,abs(i)/I,a0/I,b0/I,a/I,b/I,ic.real/I,-ic.imag/I,float(np.angle(vc)*180/np.pi),wn/(2*np.pi),abs(uu),abs(us),umax,ctl['zi'].real,ctl['zi'].imag,abs(aw),sr.real,sr.imag,s.real,s.imag,mag/Vb])
a=np.array(rows);cols=['t_s','time_from_fault_ms','raw_reference_norm_pu','clipped_reference_norm_pu','actual_I_pu','raw_a_pu','raw_b_positiveQ_pu','limited_a_pu','limited_b_positiveQ_pu','actual_id_PLL_pu','actual_minus_iq_PLL_pu','PLL_phase_error_deg','new_PLL_Hz','u_unsat_norm_V','u_sat_norm_V','u_limit_V','PI_z_d_V','PI_z_q_V','antiwindup_correction_norm_V_per_s','reference_P_from_power_identity_W','reference_Q_from_power_identity_var','actual_sampled_P_W','actual_sampled_Q_var','PCC_voltage_pu']
with (out/'fast_p_priority_same_window_diagnostics.csv').open('w') as f:
 wr=csv.writer(f);wr.writerow(cols);wr.writerows(rows)
summary={'source_trace_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reconstruction':'From saved complete pre-update state; no physical trajectory was rerun. Same original dq equations and P-priority formula.','max_recomputed_vs_logged_reference_or_sat_difference':maxdiff,'min_PCC_voltage_pu':float(min(a[:,-1])),'max_raw_reference_norm_pu':float(max(a[:,2])),'max_clipped_reference_norm_pu':float(max(a[:,3])),'max_actual_current_pu_from_dense':float(max(dense[:,14])),'max_PLL_phase_error_abs_deg':float(max(abs(a[:,11]))),'max_antiwindup_correction_V_per_s':float(max(a[:,18])),'voltage_saturation_samples':int(np.sum(a[:,14]<a[:,13]-1e-9)),'all_reference_P_nonnegative':bool(min(a[:,19])>=-1e-6),'all_reference_Q_nonnegative':bool(min(a[:,20])>=-1e-6),'sign_convention':'Peak-amplitude dq; P+jQ=1.5 v conj(i); positiveQ means negative voltage-aligned iq. Actual current is state-derived, not clipped reference.','limit_status':'1.0pu is continuous hard current;1.1pu terminates this mathematical simulation, not a hardware-protection validation.'}
assert maxdiff<1e-8
(out/'fast_p_priority_same_window_diagnostics.json').write_text(json.dumps(summary,indent=2)+'\n')
fig,axs=plt.subplots(3,2,figsize=(11,10),constrained_layout=True);x=a[:,1];dx=(dense[:,0]-.60005)*1000
axs[0,0].plot(dx,dense[:,14],label='Actual current');axs[0,0].plot(x,a[:,2],'.-',label='Raw reference');axs[0,0].plot(x,a[:,3],'.-',label='Clipped reference');axs[0,0].axhline(1,color='crimson',ls='--',label='Hard I=1');axs[0,0].axhline(1.1,color='black',ls=':',label='Numerical stop=1.1');axs[0,0].set_ylabel('Current norm (pu)')
axs[0,1].plot(x,a[:,7],'.-',label='a ref (active)');axs[0,1].plot(x,a[:,8],'.-',label='b ref (positive Q)');axs[0,1].plot(x,a[:,9],'.-',label='Actual i_d PLL');axs[0,1].plot(x,a[:,10],'.-',label='Actual -i_q PLL');axs[0,1].set_ylabel('Peak current components (pu)')
axs[1,0].plot(dx,dense[:,16]/1e3,label='Actual P');axs[1,0].plot(dx,dense[:,17]/1e3,label='Actual Q');axs[1,0].plot(x,a[:,19]/1e3,'.--',label='Reference P from identity');axs[1,0].plot(x,a[:,20]/1e3,'.--',label='Reference Q from identity');axs[1,0].set_ylabel('Power (kW / kvar)')
axs[1,1].plot(x,a[:,11],'.-',color='tab:blue',label='PLL phase error (deg)');axs[1,1].plot(x,a[:,12]-60,'.-',color='tab:orange',label='PLL frequency error (Hz)');axs[1,1].set_ylabel('Degrees / Hz (labelled traces)')
axs[2,0].plot(x,a[:,13],'.-',label='Voltage before saturation');axs[2,0].plot(x,a[:,14],'--',label='Voltage after saturation');axs[2,0].plot(x,a[:,15],':',label='Modulation circle limit');axs[2,0].set_ylabel('Voltage norm (V)')
axs[2,1].plot(x,a[:,16],'.-',label='Current PI z_d');axs[2,1].plot(x,a[:,17],'.-',label='Current PI z_q');axs[2,1].set_ylabel('Integrator voltage (V)');axs[2,1].set_title(f"Antiwindup correction max: {max(a[:,18]):.3g} V/s")
for ax in axs.flat:ax.grid(alpha=.25);ax.legend(fontsize=8);ax.set_xlabel('Time from fault onset (ms)');ax.axvline(0,color='gray',lw=.5)
fig.suptitle('Fixed P-priority: same-state fast synthetic DC port; unchanged inner controller',fontsize=13);fig.savefig(out/'fast_p_priority_same_window_diagnostics.png',dpi=150);print(json.dumps(summary,indent=2))
