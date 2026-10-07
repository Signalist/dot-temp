from exact_outer import *
root=Path(__file__).resolve().parents[1];rows=[]
for alpha,beta in [(0,0),(0,900),(100,600),(100,900),(200,0),(300,1200)]:
 for n in [40,80,160]:
  for tighten in [False,True]:
   r=solve_exact_outer(alpha,beta,n,tighten=tighten,max_iter=120,save=root/'results'/f'exact_a{alpha}_q{beta}_n{n}_tight{int(tighten)}.npz')
   rows.append(r);print(alpha,beta,n,tighten,r['status'],r.get('margin_kJ'),r.get('iterations'),flush=True)
   (root/'results'/'EXACT_CELL_CAMPAIGN.json').write_text(json.dumps(rows,indent=2))
