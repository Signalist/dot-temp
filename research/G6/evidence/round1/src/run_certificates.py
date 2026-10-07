from g6_model import *
import json,time,heapq,sys,platform,hashlib
OUT=Path(__file__).resolve().parents[1]

def certify(model,rtol=.02,maxboxes=60000):
    """Branch and bound enclosing full continuous (f,kappa) domain.
    Returns entrywise supports with explicitly conservative per-site grid maxima.
    """
    t0=time.time();lb=np.zeros((2,model.J,2)); witness=np.zeros((*lb.shape,2));leaves=[];heap=[];counter=0;evals=0;history=[]
    whole=[float(down(.08)),float(up(.75)),float(down(.85)),float(up(1.15))]
    # Feasible seeds are included only as lower bounds; never define upper bounds.
    for f in np.linspace(.08,.75,17):
        for k in [float(up(.85)),1.,float(down(1.15))]:
            l,u=model.bounds([f,f,k,k]);im=l>lb;lb=np.maximum(lb,l);witness[im]=[f,k]
    def create(b):
        nonlocal counter,evals,lb,witness
        l,u=model.bounds(b);fc=(b[0]+b[1])/2;kc=(b[2]+b[3])/2
        cl,cu=model.bounds([fc,fc,kc,kc]);im=cl>lb;lb=np.maximum(lb,cl);witness[im]=[fc,kc]
        counter+=1;evals+=1
        score=float(np.max(u/(lb+1e-20)))
        return (-score,counter,np.array(b),u)
    heapq.heappush(heap,create(whole))
    while heap and evals<maxboxes:
        _,i,b,u=heapq.heappop(heap)
        if np.all(u<=lb*(1+rtol)+1e-8):leaves.append((b,u));continue
        # normalized bisection ensures both dimensions shrink, no blind frequency grid.
        if (2*model.M*(2*np.pi*(b[0]+b[1])/2)+model.D)*(b[1]-b[0]) >= max(model.lam)*(b[3]-b[2]):
            mid=(b[0]+b[1])/2;children=([b[0],mid,b[2],b[3]],[mid,b[1],b[2],b[3]])
        else:
            mid=(b[2]+b[3])/2;children=([b[0],b[1],b[2],mid],[b[0],b[1],mid,b[3]])
        for c in children:heapq.heappush(heap,create(c))
        if evals%1000<2:
            history.append({'evals':evals,'heap':len(heap),'leaves':len(leaves),'elapsed_s':time.time()-t0})
            print(model.cfg['name'],history[-1],flush=True)
    leaves.extend([(r[2],r[3]) for r in heap])
    boxes=np.array([r[0] for r in leaves]);upper=np.array([r[1] for r in leaves]);ub=upper.max(axis=0)
    meta={'model':model.cfg,'relative_tolerance':rtol,'maxboxes':maxboxes,'evaluated_boxes':evals,'leaf_count':len(leaves),'seconds':time.time()-t0,'max_relative_gap':float(np.max((ub-lb)/lb)),'tolerance_met':bool(np.all(ub<=lb*(1+rtol)+1e-8)),'arithmetic':'IEEE754 basic operations outward-rounded one ulp; mpmath.iv80 interval trigonometric constants rounded outward to binary64','historical_old_g6_used_as_test':False,'history':history}
    np.savez_compressed(OUT/'raw'/f"{model.cfg['name']}_certificate.npz",boxes=boxes,leaf_upper=upper,lower=lb,upper=ub,witness=witness)
    (OUT/'results'/f"{model.cfg['name']}_certificate.json").write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta),flush=True)
    return meta

if __name__=='__main__':
    selected=sys.argv[1:]
    for cfg in MODELS:
        if selected and cfg['name'] not in selected:continue
        certify(Model(cfg))
