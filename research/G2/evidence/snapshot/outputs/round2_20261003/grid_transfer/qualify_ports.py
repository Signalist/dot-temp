from grid_adapter import *
import logging,time
logging.basicConfig(level=logging.WARNING)
results={}
for slug in ['kundur','wecc']:
 s=build(slug,tf=8.);K,mass,G=descriptor(s);md=s._transfer_metadata
 sparse.save_npz(ROOT/f'{slug}_descriptor_K.npz',K);np.savez_compressed(ROOT/f'{slug}_descriptor_aux.npz',mass=mass,G=G,x0=s._transfer_x0,y0=s._transfer_y0,x_names=np.asarray(s.dae.x_name),y_names=np.asarray(s.dae.y_name))
 d={'metadata':md,'tests':[]}
 if slug=='kundur':d['reduced_export']=export_kundur_reduced(s,ROOT/'kundur_reduced51.npz')
 for node,bus in enumerate(s._transfer_buses):
  for typ in [0,1]:
   for scale in [.001,.01,.05]:
    s=build(slug,tf=8.);amp=md['local_original_P_MW'][node]*scale;sc=np.zeros((3,1+G.shape[1]));sc[:,0]=[0,1,2];sc[1,1+2*node+typ]=amp;schedule=install_schedule(s,sc)
    ok=bool(s.TDS.run());o=extract(s);z=linear_trace(s,K,mass,G,o['t'],schedule);idx=s.GENROU.omega.a;gen=[m for m in [s.GENROU,s.GENCLS] if m.n];idx=np.concatenate([m.omega.a for m in gen]);lf=z[:,idx]*s.config.freq;lv=z[:,s.dae.n+s.Bus.v.a]
    freq=o['frequency_deviation_Hz'];vol=o['bus_voltage_pu']-s._transfer_y0[s.Bus.v.a];dn=freq-lf;dv=vol-lv
    r={'bus':bus,'type':'P' if typ==0 else 'Q','scale_of_local_P':scale,'amplitude_MW_or_Mvar':amp,'system_base_pu':amp/s.config.mva,'tds_return':ok,'end_time':float(s.dae.t),'busted':bool(s.TDS.busted),'err_msg':s.TDS.err_msg,'peak_frequency_Hz':float(np.max(abs(freq))),'peak_coi_Hz':float(np.max(abs(o['coi_frequency_deviation_Hz']))),'peak_voltage_deviation_pu':float(np.max(abs(vol))),'linear_frequency_peak_Hz':float(np.max(abs(lf))),'frequency_Linf_error_Hz':float(np.max(abs(dn))),'frequency_relative_L2_error':float(np.linalg.norm(dn)/max(np.linalg.norm(lf),1e-30)),'voltage_relative_L2_error':float(np.linalg.norm(dv)/max(np.linalg.norm(lv),1e-30)),'frequency_squared_integral_equalweights_Hz2s':float(np.trapezoid(np.sum(freq**2,axis=1),o['t'])),'frequency_squared_integral_inertiaweights_Hz2s':float(np.trapezoid((freq**2)@o['coi_weights'],o['t']))}
    fname=f'{slug}_bus{bus}_{r["type"]}_{scale}';np.savez_compressed(ROOT/(fname+'.npz'),**o,linear_frequency_deviation_Hz=lf,linear_bus_voltage_deviation_pu=lv,schedule=schedule);d['tests'].append(r);results[slug]=d;(ROOT/'port_qualification.json').write_text(json.dumps(results,indent=2));print(slug,r,flush=True)
