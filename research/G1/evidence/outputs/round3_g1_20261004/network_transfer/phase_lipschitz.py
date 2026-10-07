from design_controller import *
def expbound(z,h,tol=1e-8):
 z1=np.exp(lam*h)*z;y0=(CV@z).real;y1=(CV@z1).real
 err=abs(CV)@(abs(lam)**2*abs(z))*h*h/8
 if np.max(err)<=tol:return max(np.max(abs(y0)),np.max(abs(y1)))+np.max(err)
 return max(expbound(z,h/2,tol),expbound(np.exp(lam*h/2)*z,h/2,tol))
q=np.exp(lam*5);vals=[]
for m in range(20):
 z=bm*(1-(-q)**(m+1))/(1+q)
 vals.append(float(expbound(z,5)))
per=float(expbound(bm/(1+q),5));tail=per+float(np.max(abs(CV)@(abs(bm/(1+q))*abs(q)**21)))
r={'finite_20_segments_max_perMW_s':max(vals),'asymptotic_upper_perMW_s':per,'tail_after100_upper_perMW_s':tail,'phase_Lipschitz_Hz_per_s':50*max(max(vals),tail),'half_information_bin_s':.05,'all_future_midpoint_phase_allowance_Hz':2.5*max(max(vals),tail),'formula':'phase derivative=50 alternating impulse-response train; geometric modal series plus analytic curvature envelope; fixed same-information controls cancel','numeric_scope':'analytic floating point, not interval arithmetic'}
(OUT/'PHASE_LIPSCHITZ_BOUND.json').write_text(json.dumps(r,indent=2));print(r)
