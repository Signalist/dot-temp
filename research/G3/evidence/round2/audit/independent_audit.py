"""Independent physical/witness audit; imports no G3 model or admission code.
Units in coefficient checks: kW,kJ,kA,kV,s. Plant replay is entirely SI.
"""
from pathlib import Path
import numpy as np
import scipy.integrate as integrate
import scipy.optimize as optimize
import json, math, hashlib, datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'audit'

def extremum(c):
    """All real stationary points of degree<=3, independently via descending roots."""
    c=np.asarray(c,float)
    while len(c)>1 and abs(c[-1])<1e-18:c=c[:-1]
    dc=np.arange(1,len(c))*c[1:]
    roots=np.roots(dc[::-1]) if len(dc)>1 else []
    xs=[0.,1.]+[z.real for z in roots if abs(z.imag)<1e-9 and 0<z.real<1]
    vals=[sum(v*x**j for j,v in enumerate(c)) for x in xs]
    k=np.argmin(vals); j=np.argmax(vals)
    return float(vals[k]),float(xs[k]),float(vals[j]),float(xs[j])

def shape(t,start,end):
    return np.maximum(0,np.minimum(1,np.minimum((np.asarray(t)-start)/.005,(end-np.asarray(t))/.005)))

def scalarex(p,x):return sum(v*x**j for j,v in enumerate(p))

def independent_profiles(t,p,alpha,beta):
    v=p['v']; c=p['R']/(1500*v*v)
    p0=optimize.brentq(lambda z:z-c*z*z-p['D0'],p['D0'],2*p['D0'])
    def integral_balance(gamma):
        def rhs(x):
            g=shape(x,0,.040);gm=shape(x,.070,.110);r=shape(x,.125,.175)
            P=p0+alpha*(gm-g)+gamma*r;Q=beta*g;d=p['D0']+p['Aload']*(g-gm)
            return P-d-c*(P*P+Q*Q)
        return integrate.quad(rhs,0,p['T'],points=[.005,.035,.040,.070,.075,.105,.110,.125,.130,.170,.175],epsabs=1e-11,epsrel=1e-11)[0]
    f0=integral_balance(0)
    gamma=0 if abs(f0)<1e-10 else optimize.brentq(integral_balance,0,1000,xtol=1e-11)
    g=shape(t,0,.040);gm=shape(t,.070,.110);r=shape(t,.125,.175)
    return p0+alpha*(gm-g)+gamma*r,beta*g,p['D0']+p['Aload']*(g-gm),gamma,integral_balance(gamma)

def witness_audit(path, profile_generator=independent_profiles, nominal_n=None):
    z=np.load(path);p=json.loads(str(z['par_json']));t=z['t'];h=np.diff(t);N=len(h)
    P,Q,D,gamma,closure=profile_generator(t,p,float(z['alpha']),float(z['beta']))
    bc=np.column_stack((z['b'][:-1],z['a'],z['c']))
    vv=p['v'];Idq=np.column_stack((P,Q))/(1500*vv)
    W0=500*p['Cdc']*p['vdc0']**2;B0=p['B0'];Z0=750*p['L']*sum(Idq[0]**2)
    Wmin=500*p['Cdc']*p['vdcmin']**2;Wmax=500*p['Cdc']*p['vdcmax']**2
    checks={};where={};maxdiff={'W_coeff_kJ':0.,'B_coeff_kJ':0.,'u_coeff_kW':0.}
    Cstart=0.;netgrid=0.;Wseries=[];Useries=[];Eseries=[]
    density_errors={'power_balance_kW':0.,'total_energy_derivative_kW':0.,'phase_power_kW':0.,'phase_norm_sq_kA2':0.}
    phase_max=0.;mod_circle_max=0.;theta=2*np.pi*np.arange(3)/3
    def record(name,co,seg):
        lo,x,hi,xhi=extremum(co)
        if name not in checks or lo<checks[name]:checks[name]=lo;where[name]=float(t[seg]+h[seg]*x)
    for k in range(N):
        ih=Idq[k+1]-Idq[k];i=Idq[k]
        # Build directly from p,d and i dot i, rather than an imported energy offset.
        loss=1500*p['R']*np.array([i@i,2*i@ih,ih@ih])
        magnetic=750*p['L']*np.array([i@i,2*i@ih,ih@ih])
        gridnet=np.array([P[k]-D[k],P[k+1]-P[k]-D[k+1]+D[k],0.])-loss
        integgrid=np.array([netgrid,h[k]*gridnet[0],h[k]*gridnet[1]/2,h[k]*gridnet[2]/3])
        battery=np.array([Cstart,h[k]*bc[k,0],h[k]*bc[k,1]/2,h[k]*bc[k,2]/3])
        W=integgrid+battery;W[:3]-=magnetic;W[0]+=W0+Z0
        B=-battery;B[0]+=B0
        db=np.array([bc[k,1]/h[k],2*bc[k,2]/h[k],0.])
        u=bc[k]+p['tau']*db
        # dq in import-positive Park convention; q here is positive injection.
        e0=np.array([vv,0.])-p['R']*i-p['L']*ih/h[k]-p['omega']*p['L']*np.array([-i[1],i[0]])
        ed=-p['R']*ih-p['omega']*p['L']*np.array([-ih[1],ih[0]])
        floor=1500*p['Cdc']*np.array([e0@e0,2*e0@ed,ed@ed,0.])
        Wseries.append(W);Useries.append(u);Eseries.append((e0,ed))
        for name,c in [('W_lower_kJ',W-np.array([Wmin,0,0,0])),('W_upper_kJ',np.array([Wmax,0,0,0])-W),('B_lower_kJ',B-np.array([p['Bmin'],0,0,0])),('B_upper_kJ',np.array([p['Bmax'],0,0,0])-B),('modulation_kJ',W-floor)]:record(name,c,k)
        for tag,v,bnd in [('b',bc[k],p['bmax']),('u',u,p['umax']),('ramp',db,p['ramp'])]:
            record(tag+'_lower',v+np.array([bnd,0,0]),k);record(tag+'_upper',np.array([bnd,0,0])-v,k)
        maxdiff['W_coeff_kJ']=max(maxdiff['W_coeff_kJ'],float(np.max(abs(W-z['Wpoly'][k]))))
        maxdiff['B_coeff_kJ']=max(maxdiff['B_coeff_kJ'],float(np.max(abs(B-z['Bpoly'][k]))))
        maxdiff['u_coeff_kW']=max(maxdiff['u_coeff_kW'],float(np.max(abs(np.r_[u,0]-z['upoly'][k]))))
        # Dense independent physical identities in abc, using no dq power identity.
        x=np.linspace(0,1,101);times=t[k]+h[k]*x
        current=i[None,:]+x[:,None]*ih;deriv=ih/h[k]
        angles=p['omega']*times[:,None]-theta
        iabc=current[:,0,None]*np.cos(angles)-current[:,1,None]*np.sin(angles)
        didt=(deriv[0]-p['omega']*current[:,1])[:,None]*np.cos(angles)-(deriv[1]+p['omega']*current[:,0])[:,None]*np.sin(angles)
        vabc=vv*np.cos(angles);eabc=vabc-p['R']*iabc-p['L']*didt
        Pabc=1000*np.sum(vabc*iabc,axis=1);Pdc=1000*np.sum(eabc*iabc,axis=1)
        rho=1000*p['R']*np.sum(iabc*iabc,axis=1);dZ=1000*p['L']*np.sum(iabc*didt,axis=1)
        dW=sum(j*W[j]*x**(j-1)/h[k] for j in range(1,4));b=scalarex(bc[k],x);d=D[k]+x*(D[k+1]-D[k])
        density_errors['power_balance_kW']=max(density_errors['power_balance_kW'],float(np.max(abs(dW-(Pdc+b-d)))))
        density_errors['total_energy_derivative_kW']=max(density_errors['total_energy_derivative_kW'],float(np.max(abs(dW-b+dZ-Pabc+rho+d))))
        density_errors['phase_power_kW']=max(density_errors['phase_power_kW'],float(np.max(abs(Pabc-(P[k]+x*(P[k+1]-P[k]))))))
        density_errors['phase_norm_sq_kA2']=max(density_errors['phase_norm_sq_kA2'],float(np.max(abs((2/3)*np.sum(iabc*iabc,axis=1)-np.sum(current*current,axis=1)))))
        phase_max=max(phase_max,float(np.max(abs(iabc))))
        Vdc=np.sqrt(scalarex(W,x)/(500*p['Cdc']));mod_circle_max=max(mod_circle_max,float(np.max(np.sqrt(3)*np.linalg.norm(e0+x[:,None]*ed,axis=1)/Vdc)))
        Cstart=float(sum(battery));netgrid=float(sum(integgrid))
    bcont=z['b'][1:]-bc.sum(axis=1)
    ccont=z['charge'][1:]-z['charge'][:-1]-h*(bc[:,0]+bc[:,1]/2+bc[:,2]/3)
    fixed=t[:-1]<p['delay']-1e-12
    terminal={'b0_kW':float(z['b'][0]),'bT_kW':float(z['b'][-1]),'integral_b_kJ':Cstart,'W_restore_kJ':float(sum(Wseries[-1])-W0),'B_restore_kJ':-Cstart,'initial_hold_b_coeff_kW':float(np.max(abs(bc[fixed]))),'b_continuity_kW':float(np.max(abs(bcont))),'C_continuity_kJ':float(np.max(abs(ccont)))}
    minreal=min(checks.values());admitted=bool(float(z['sigma'])>1e-5 and minreal>-1e-5)
    out={'file':path.name,'alpha_kW':float(z['alpha']),'beta_kvar':float(z['beta']),'nominal_n':nominal_n if nominal_n is not None else int(path.stem.split('_n')[-1]),'intervals':N,'sigma_kJ':float(z['sigma']),'independent_admitted_numeric':admitted,'profile_max_error':float(max(np.max(abs(P-z['p'])),np.max(abs(Q-z['q'])),np.max(abs(D-z['d'])))),'gamma_kW':gamma,'grid_energy_closure_kJ':closure,'analytic_minimum_slacks':checks,'minimum_locations_s':where,'reconstructed_coeff_max_errors':maxdiff,'dense_physical_identity_errors':density_errors,'terminal_residuals':terminal,'current_envelope_squared_margin_kA2':float(p['imax']**2-np.max(np.sum(Idq**2,axis=1))),'sampled_phase_peak_kA':phase_max,'sampled_modulation_circle_ratio':mod_circle_max,'timestamps_strict_and_cover_horizon':bool(np.all(h>0) and t[0]==0 and abs(t[-1]-p['T'])<1e-14),'timestamp_has_hold_boundary':bool(np.min(abs(t-p['delay']))<1e-12)}
    return out,(p,t,P,Q,D,np.asarray(Wseries),np.asarray(Useries),np.asarray(Eseries))

def replay_abc(info,rtol=2e-10):
    p,t,P,Q,D,Wpol,U,E=info;v=p['v']*1000;phase=np.arange(3)*2*np.pi/3
    i0=P[0]*1000/(1.5*v)*np.cos(-phase)-Q[0]*1000/(1.5*v)*np.sin(-phase)
    y=np.r_[i0,500*p['Cdc']*p['vdc0']**2*1000,p['B0']*1000,0.]
    E0=y[3]+y[4]+.5*p['L']*sum(y[:3]**2)
    # Extra states integrate independently grid, copper, load and converter energies.
    y=np.r_[y,np.zeros(4)]
    err={k:0. for k in ['i_abc_A','W_J','B_J','b_W','P_W','Q_var','energy_closure_J','command_clip_W','modulation_clip_V','ramp_clip_Wps']};mins={'Vdc_V':np.inf,'Vdc_upper_slack_V':np.inf,'B_lower_J':np.inf,'B_upper_J':np.inf};peakphase=0;neval=0
    for k,h in enumerate(np.diff(t)):
        def rhs(s,y):
            x=np.clip((s-t[k])/h,0,1);ang=p['omega']*s-phase
            e=(E[k,0]+x*E[k,1])*1000
            edabc=e[0]*np.cos(ang)-e[1]*np.sin(ang)
            Vdc=np.sqrt(max(0,2*y[3]/p['Cdc']));fact=min(1,Vdc/(np.sqrt(3)*np.linalg.norm(e)))
            ec=edabc*fact;vg=v*np.cos(ang);dl=(vg-p['R']*y[:3]-ec)/p['L']
            u=1000*scalarex(U[k],x);uc=np.clip(u,-1000*p['umax'],1000*p['umax']);unclipped=(uc-y[5])/p['tau'];bd=np.clip(unclipped,-1000*p['ramp'],1000*p['ramp'])
            d=1000*(D[k]+x*(D[k+1]-D[k]));pin=vg@y[:3];rho=p['R']*(y[:3]@y[:3]);pdc=ec@y[:3]
            return np.r_[dl,pdc+y[5]-d,-y[5],bd,pin,rho,d,pdc]
        sol=integrate.solve_ivp(rhs,(t[k],t[k+1]),y,method='DOP853',rtol=rtol,atol=1e-8,dense_output=True,max_step=h/4)
        if not sol.success:raise RuntimeError(sol.message)
        neval+=sol.nfev;x=np.linspace(0,1,41);times=t[k]+h*x;ys=sol.sol(times).T;y=sol.y[:,-1]
        ang=p['omega']*times[:,None]-phase;id=(P[k]+x*(P[k+1]-P[k]))*1000/(1.5*v);iq=(Q[k]+x*(Q[k+1]-Q[k]))*1000/(1.5*v)
        it=id[:,None]*np.cos(ang)-iq[:,None]*np.sin(ang)
        bt=(U[k,0]-p['tau']*(0)) # overwritten via W derivative construction below
        # For independent b target recover its ODE solution from the witness W balance.
        # Polynomial b coefficients come from u=(b+tau*b') by backward coefficient recursion.
        b2=U[k,2];b1=U[k,1]-2*p['tau']*b2/h;b0=U[k,0]-p['tau']*b1/h
        btarget=1000*(b0+b1*x+b2*x*x)
        wtarget=1000*scalarex(Wpol[k],x)
        Cprefix=p['B0']*1000-ys[0,4]
        Btarget=ys[0,4]-1000*h*(b0*x+b1*x*x/2+b2*x*x*x/3)
        norm=np.sqrt(2/3*np.sum(ys[:,:3]**2,axis=1));Vdc=np.sqrt(2*ys[:,3]/p['Cdc'])
        pp=v*np.sum(np.cos(ang)*ys[:,:3],axis=1);qq=-v*np.sum(np.sin(ang)*ys[:,:3],axis=1)
        calc={'i_abc_A':np.max(abs(ys[:,:3]-it)),'W_J':np.max(abs(ys[:,3]-wtarget)),'B_J':np.max(abs(ys[:,4]-Btarget)),'b_W':np.max(abs(ys[:,5]-btarget)),'P_W':np.max(abs(pp-1000*(P[k]+x*(P[k+1]-P[k])))),'Q_var':np.max(abs(qq-1000*(Q[k]+x*(Q[k+1]-Q[k])))),'energy_closure_J':np.max(abs(ys[:,3]+ys[:,4]+.5*p['L']*np.sum(ys[:,:3]**2,axis=1)-E0-ys[:,6]+ys[:,7]+ys[:,8]))}
        us=1000*scalarex(U[k],x);uc=np.clip(us,-1000*p['umax'],1000*p['umax']);bd0=(uc-ys[:,5])/p['tau']
        calc['command_clip_W']=np.max(abs(us-uc));calc['ramp_clip_Wps']=np.max(abs(bd0-np.clip(bd0,-1000*p['ramp'],1000*p['ramp'])))
        emag=1000*np.linalg.norm(E[k,0]+x[:,None]*E[k,1],axis=1);calc['modulation_clip_V']=np.max(np.maximum(0,emag-Vdc/np.sqrt(3)))
        for key,val in calc.items():err[key]=max(err[key],float(val))
        mins['Vdc_V']=min(mins['Vdc_V'],float(Vdc.min()));mins['Vdc_upper_slack_V']=min(mins['Vdc_upper_slack_V'],float(1000*p['vdcmax']-Vdc.max()));mins['B_lower_J']=min(mins['B_lower_J'],float(ys[:,4].min()-1000*p['Bmin']));mins['B_upper_J']=min(mins['B_upper_J'],float(1000*p['Bmax']-ys[:,4].max()));peakphase=max(peakphase,float(np.max(abs(ys[:,:3]))))
    return {'method':'independent SI abc DOP853; physical converter circle/input/ramp clipping active in RHS; each knot is an integration boundary','rtol':rtol,'rhs_evaluations':neval,'max_errors_and_clipping':err,'sampled_limits':mins,'sampled_phase_peak_A':peakphase,'terminal':{'W_error_J':float(y[3]-500*p['Cdc']*p['vdc0']**2*1000),'B_error_J':float(y[4]-1000*p['B0']),'b_W':float(y[5])}}

def main():
    rows=json.loads((ROOT/'results/PRIMARY_CAMPAIGN.json').read_text());by={(r['alpha'],r['beta'],r['n']):r for r in rows}
    out={'timestamp_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independence':'No imports from src/model.py, src/admission.py, or validation solver. Profiles solved by quadrature+root; extrema from independent coefficient reconstruction and roots; SI abc plant replay uses clipped command, ramp and modulation.','witnesses':[],'campaign_rows':len(rows),'inner_outer_order_violations':[],'input_sha256':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [ROOT/'PROTOCOL.json',ROOT/'src/model.py',ROOT/'src/admission.py',ROOT/'results/PRIMARY_CAMPAIGN.json']}}
    for row in rows:
        a=row['inner'].get('margin_kJ');b=row['outer'].get('outer_margin_kJ')
        if a is not None and b is not None and a>b+1e-5:out['inner_outer_order_violations'].append({'alpha':row['alpha'],'beta':row['beta'],'n':row['n'],'inner_minus_outer_kJ':a-b})
    for f in sorted((ROOT/'results').glob('witness*.npz')):
        w,info=witness_audit(f);row=by.get((w['alpha_kW'],w['beta_kvar'],w['nominal_n']))
        w['campaign_certified']=bool(row and row['inner'].get('certified_numeric_inner'))
        if w['campaign_certified']:w['independent_SI_abc_replay']=replay_abc(info)
        out['witnesses'].append(w)
        print(f.name,w['sigma_kJ'],w.get('independent_SI_abc_replay',{}).get('max_errors_and_clipping',{}),flush=True)
        (OUT/'INDEPENDENT_AUDIT.json').write_text(json.dumps(out,indent=2))
    out['summary']={'witness_count':len(out['witnesses']),'claimed_admitted':sum(w['campaign_certified'] for w in out['witnesses']),'independently_admitted':sum(w['independent_admitted_numeric'] for w in out['witnesses']),'classification_disagreements':[w['file'] for w in out['witnesses'] if w['campaign_certified']!=w['independent_admitted_numeric']]}
    (OUT/'INDEPENDENT_AUDIT.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['summary']))
if __name__=='__main__':main()
