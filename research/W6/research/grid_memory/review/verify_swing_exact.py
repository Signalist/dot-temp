"""Fresh post-reset verification: exact piecewise-ramp LTI responses.
Every inter-knot stationary point is enumerated analytically; zero-input tail
needs only its first two stationary points, since successive absolute extrema
have the exact geometric decay exp(-alpha*pi/beta).
"""
import mpmath as mp
import json
import os
from pathlib import Path
mp.mp.dps=int(os.environ.get("MP_DPS", "60"))
D=Path(__file__).resolve().parent

def S(x): return mp.mpf(str(x))
def response(knots, powers, alpha, beta, gain):
    knots=list(map(S,knots));powers=list(map(S,powers));alpha=S(alpha);beta=S(beta);gain=S(gain)
    slopes=[(powers[i+1]-powers[i])/(knots[i+1]-knots[i]) for i in range(len(knots)-1)]
    changes=[slopes[0]]+[slopes[i]-slopes[i-1] for i in range(1,len(slopes))]+[-slopes[-1]]
    k=alpha*alpha+beta*beta
    def F(t):
        if t<0: return mp.mpf('0')
        return (1-mp.exp(-alpha*t)*(mp.cos(beta*t)+alpha/beta*mp.sin(beta*t)))/k
    def y(t): return gain*sum(c*F(t-tj) for tj,c in zip(knots,changes) if tj<=t)
    candidates=[(t,y(t),'knot') for t in knots]
    for j,left in enumerate(knots):
        right=knots[j+1] if j+1<len(knots) else None
        active=range(j+1)
        aa=sum(changes[i]*mp.exp(alpha*knots[i])*mp.cos(beta*knots[i]) for i in active)
        bb=sum(changes[i]*mp.exp(alpha*knots[i])*mp.sin(beta*knots[i]) for i in active)
        if mp.hypot(aa,bb)<mp.mpf('1e-50'):continue
        theta=mp.atan2(bb,aa)
        n=int(mp.ceil((beta*left-theta)/mp.pi))
        roots=0
        while True:
            t=(theta+n*mp.pi)/beta;n+=1
            if t<=left+mp.mpf('1e-45'):continue
            if right is not None and t>=right-mp.mpf('1e-45'):break
            candidates.append((t,y(t),'stationary' if right is not None else 'tail stationary'))
            roots+=1
            if right is None and roots>=2:break
    peak=max(candidates,key=lambda q:abs(q[1]))
    tail=[q for q in candidates if q[0]>=knots[-1]]
    return {'peak_abs':mp.nstr(abs(peak[1]),40),'peak_time':mp.nstr(peak[0],40),'peak_signed':mp.nstr(peak[1],40),'peak_type':peak[2],
      'return_time':mp.nstr(knots[-1],40),'tail_peak_abs':mp.nstr(max(abs(q[1]) for q in tail),40),'tail_extrema_decay_ratio':mp.nstr(mp.exp(-alpha*mp.pi/beta),40),'all_extrema':[[mp.nstr(t,40),mp.nstr(v,40),kind] for t,v,kind in candidates]}, y

# Analytic zero-state projection violation.
a=4*mp.pi/3;R=mp.mpf('.01');alpha=mp.mpf('.01');beta=mp.mpf('1');T=mp.mpf('2.5')*a
orig,yo=response([0,a,mp.mpf('1.5')*a,T],[0,R*a,R*a,0],alpha,beta,1)
proj,yc=response([0,a,2*a],[0,R*a,0],alpha,beta,1)
projection={'origin':'fresh post-reset rerun from mathematical formulas, not recovered raw output','s':'p','R':str(R),'M':mp.nstr(R*a*a,40),'grid':'delta_ddot + .02 delta_dot + 1.0001 delta = -p; y=-delta_dot','initial_grid_state':[0,0], 'budget':'0.025','original':orig,'projected':proj,'projected_y_at_original_return':mp.nstr(yc(T),40),'analytic_uniform_F_error_bound':mp.nstr(alpha*(T+1)+2*alpha*alpha,40)}
(D/'ZERO_STATE_PROJECTION_VERIFIED.json').write_text(json.dumps(projection,indent=2)+'\n')

z1=[0,.125,.21026169860877808,.08526169860877808,.21026169860877808,.3352616986087781,.3055598229597505,.18055982295975048,.3055598229597505,.4305598229597505,.4995976881251713,.3745976881251713,.2495976881251713,.3745976881251713,.25,.125,0]
z2=[0,.09339096875183897,.21839096875183897,.15360815276463885,.10281095161329798,.22781095161329798,.352810951613298,.477810951613298,.4492056805697694,.3242056805697694,.1992056805697694,.3242056805697694,.4492056805697694,.3419828349940685,.2169828349940685,.125,0]

def work_to_time(z):
    z=list(map(S,z));dx=mp.mpf('.125');pp=[(mp.mpf('1.5')*v)**(mp.mpf(2)/3) for v in z];tt=[mp.mpf(0)]
    for i in range(len(z)-1):
        slope=(z[i+1]-z[i])/dx
        dt=(pp[i+1]-pp[i])/slope if slope else dx/mp.sqrt(pp[i])
        tt.append(tt[-1]+dt)
    return tt,pp

def verify_set(name,z1,z2,gain_value="36.9"):
    z1=list(map(S,z1));z2=list(map(S,z2));zmid=[(x+y)/2 for x,y in zip(z1,z2)]
    omega=2*mp.pi*mp.mpf('.4');alpha=mp.mpf('.08')*omega;beta=omega*mp.sqrt(1-mp.mpf('.08')**2);gain=-mp.mpf(gain_value)/(mp.mpf(400)/3)
    out={}
    for tag,z in [('z1',z1),('z2',z2),('midpoint',zmid)]:
        tt,pp=work_to_time(z);result,_=response(tt,pp,alpha,beta,gain)
        slopes=[abs(z[i+1]-z[i])/mp.mpf('.125') for i in range(16)]
        result['work_nodes']=[mp.nstr(v,40) for v in z];result['physical_time_knots']=[mp.nstr(v,40) for v in tt]
        result['max_abs_z_slope']=mp.nstr(max(slopes),40)
        result['recovery_cap_slack_min']=mp.nstr(min(2-mp.mpf('.125')*i-v for i,v in enumerate(z)),40)
        result['initial_reach_cap_slack_min']=mp.nstr(min(mp.mpf('.125')*i-v for i,v in enumerate(z)),40)
        result['critical_cap_slack_min']=mp.nstr(mp.mpf(2)/3-max(z),40)
        out[tag]=result
    return out
convexity={'origin':'fresh post-reset independent rerun of parent-supplied arrays','grid':'delta_dot=2*pi*f; f_dot=-omega^2*delta/(2*pi)-2*zeta*omega*f-(g/(400/3))*p','omega':'2*pi*.4','zeta':'.08','budget':'.05','s':'sqrt(p)','R':1,'M':2,'c':1,'initial_grid_state':[0,0], 'original_precision':verify_set('full',z1,z2),'rounded_three_decimals':verify_set('rounded',[f'{v:.3f}' for v in z1],[f'{v:.3f}' for v in z2])}
convexity['rounded_three_decimals_gain36_8']=verify_set('rounded-safe',[f'{v:.3f}' for v in z1],[f'{v:.3f}' for v in z2],'36.8')
convexity['variant_gains']={'original_precision':'36.9','rounded_three_decimals':'36.9','rounded_three_decimals_gain36_8':'36.8'}
convexity['recommended_fixture']='rounded_three_decimals_gain36_8'
convexity['precision_decimal_digits']=mp.mp.dps
(D/'CONVEXITY_INDEPENDENT_VERIFIED.json').write_text(json.dumps(convexity,indent=2)+'\n')
print('ZERO-STATE PROJECTION:', {k:projection[k] for k in ['M','projected_y_at_original_return']})
for name,q in [('original',orig),('projected',proj)]:print(name, q['peak_abs'],q['peak_time'],q['peak_type'])
for variant in ['original_precision','rounded_three_decimals','rounded_three_decimals_gain36_8']:
 print(variant)
 for tag,q in convexity[variant].items():print(tag,q['peak_abs'],q['peak_time'],q['peak_type'],q['tail_peak_abs'],q['max_abs_z_slope'])
