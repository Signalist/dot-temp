"""Deterministic public synthetic pilot, disjoint structural families by split.
References are validator fixtures, never model outputs or GPU measurements.
"""
import hashlib,json,pathlib,random
ROOT=pathlib.Path(__file__).resolve().parent

def sha(x):return hashlib.sha256(x).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def prefix(xs):
    out=[];v=0
    for x in xs:v+=x;out.append(v)
    return out
def suffix(xs):return list(reversed(prefix(list(reversed(xs)))))
def runs(xs,equal=False):
    out=[]
    for x in xs:
        if out and (x==out[-1][-1] if equal else x==out[-1][-1]+1):out[-1].append(x)
        else:out.append([x])
    return out
SOURCES={
'count_positive':'''def count_positive(xs):
    """Count positive integers.\n    >>> count_positive([0, 2, -1])\n    1\n    """
    return len([x for x in xs if x > 0])
''',
'count_negative':'''def count_negative(xs):
    """Count negative integers.\n    >>> count_negative([0, 2, -1])\n    1\n    """
    return len([x for x in xs if x < 0])
''',
'prefix_sums':'''def prefix_sums(xs):
    """Return inclusive prefix sums.\n    >>> prefix_sums([1, 2, 3])\n    [1, 3, 6]\n    """
    out = []
    total = 0
    for x in xs:
        total += x
        out.append(total)
    return out
''',
'suffix_sums':'''def suffix_sums(xs):
    """Return inclusive suffix sums in original index order.\n    >>> suffix_sums([1, 2, 3])\n    [6, 5, 3]\n    """
    out = []
    total = 0
    for x in reversed(xs):
        total += x
        out.append(total)
    return list(reversed(out))
''',
'consecutive_runs':'''def consecutive_runs(xs):
    """Partition into maximal contiguous +1 runs; preserve all values.\n    >>> consecutive_runs([1, 2, 5])\n    [[1, 2], [5]]\n    """
    out = []
    current = []
    for x in xs:
        if current and x != current[-1] + 1:
            out.append(current)
            current = []
        current.append(x)
    if current:
        out.append(current)
    return out
''',
'equal_runs':'''def equal_runs(xs):
    """Partition into maximal contiguous equal runs.\n    >>> equal_runs([1, 1, 5])\n    [[1, 1], [5]]\n    """
    out = []
    current = []
    for x in xs:
        if current and x != current[-1]:
            out.append(current)
            current = []
        current.append(x)
    if current:
        out.append(current)
    return out
'''}

def build():
    tasks=[];gold={};rng=random.Random(20261007)
    specs=[('development','sign_count','count_positive','Count integers strictly greater than zero.',lambda xs:sum(x>0 for x in xs)),('development','sign_count','count_negative','Count integers strictly less than zero.',lambda xs:sum(x<0 for x in xs)),('calibration','cumulative_scan','prefix_sums','Return the inclusive prefix sum at every input index.',prefix),('calibration','cumulative_scan','suffix_sums','Return the inclusive suffix sum at every input index, keeping original index order.',suffix),('heldout','contiguous_segmentation','consecutive_runs','Partition every element into maximal contiguous runs whose neighboring values increase by exactly one; preserve order and singleton runs.',runs),('heldout','contiguous_segmentation','equal_runs','Partition every element into maximal contiguous runs of equal values; preserve order and singleton runs.',lambda xs:runs(xs,True))]
    for split,family,name,meaning,oracle in specs:
        arrays=[[],[0],[7],[-2,-1,0,1,2],[1,2,3],[3,2,1],[1,1,2,5,6],[0,0,0]]+[[rng.randint(-4,4) for _ in range(rng.randint(0,20))] for _ in range(40)]
        tid='code_'+name
        tasks.append({'id':tid,'domain':'code','family':'code_'+family,'split':split,'function':name,'prompt':f'Return exactly one pure Python function named {name}(xs). {meaning} Input is a list of integers. Return [] for empty sequence outputs and 0 for empty count outputs. Do not mutate xs. Include a descriptive docstring with one runnable >>> example and its expected result. Output source only, no fences, imports, external I/O, or top-level execution. Use built-ins and simple loops or comprehensions; no recursion. Finish naturally.','cases':[{'args':[xs],'expected':oracle(xs)} for xs in arrays]})
        gold[tid]=SOURCES[name]
    ms=[('development','stock_flow','book_stock','There are 37 books. 12 arrive and 8 leave. How many remain?',41,'41-12+8=37'),('development','stock_flow','seed_stock','There are 63 seeds. 17 are planted and 9 added. How many remain?',55,'55+17-9=63'),('calibration','rectangle_geometry','perimeter','A rectangle has side lengths 7 and 11. Find its perimeter.',36,'36/2-7=11'),('calibration','rectangle_geometry','area','A rectangle has side lengths 9 and 13. Find its area.',117,'117/9=13'),('heldout','unordered_pairs','pairs','How many unordered pairs of distinct items can be chosen from 8 items?',28,'28*2=8*7'),('heldout','unordered_pairs','handshakes','Each of 11 people shakes every other person once. How many handshakes occur?',55,'55*2=11*10')]
    for split,fam,name,q,a,check in ms:
        tid='math_'+name;tasks.append({'id':tid,'domain':'math','family':'math_'+fam,'split':split,'answer':a,'check':check,'prompt':q+' Return only JSON with exactly answer (integer) and check (string). Use this inverse/counting check template, replacing {answer} with your numeric answer, with no spaces: '+check.replace(str(a),'{answer}',1)+'. Verify it is true. Finish naturally.'});gold[tid]=json.dumps({'answer':a,'check':check})
    ws=[('development','public_notice','library_notice','a short public notice',[('The library opens at 09:00 on Monday.',['library','opens','09:00','Monday'],['09:00']),('Visitors enter through the east door.',['Visitors','east','door'],[])]),('development','public_notice','garden_notice','a short public notice',[('The garden opens at 08:00 on Tuesday.',['garden','opens','08:00','Tuesday'],['08:00']),('Visitors enter through the north gate.',['Visitors','north','gate'],[])]),('calibration','procedure','sorting_steps','ordered instructions',[('First place returned books on the blue cart.',['First','returned','books','blue','cart'],[]),('Next arrange the books by title.',['Next','books','title'],[])]),('calibration','procedure','seed_steps','ordered instructions',[('First place dry seeds in the green tray.',['First','dry','seeds','green','tray'],[]),('Next label the tray by plant name.',['Next','tray','plant','name'],[])]),('heldout','comparison','room_comparison','a factual comparison',[('The reading room has 12 seats.',['reading','room','12','seats'],['12']),('The study room has 8 seats.',['study','room','8','seats'],['8'])]),('heldout','comparison','shelf_comparison','a factual comparison',[('The upper shelf holds 20 books.',['upper','shelf','20','books'],['20']),('The lower shelf holds 15 books.',['lower','shelf','15','books'],['15'])])]
    for split,fam,name,genre,rows in ws:
        tid='writing_'+name;facts=[{'source':s,'anchors':a,'numbers':n} for s,a,n in rows]
        tasks.append({'id':tid,'domain':'writing','family':'writing_'+fam,'split':split,'facts':facts,'prompt':f'Write {genre} for a general audience using only these facts: '+ ' '.join(r[0] for r in rows)+f' Return only JSON with key sentences, an array of {len(rows)} complete brief English sentences, one fact per sentence in the given order. Preserve names, numbers and directional words. Do not add facts. Finish naturally.'});gold[tid]=json.dumps({'sentences':[x[0] for x in rows]})
    pool={'version':'w6-quality-pilot-v1','public_synthetic':True,'external_corpus':False,'new_model_outputs':False,'generation_protocol':'Author-built structural families. Deterministic case seed 20261007. References are validator fixtures only. No prompts selected using measured energy.','splits':{'development':'Author and debug validators/candidates only','calibration':'Estimate feasibility and variance; no heldout inspection during candidate tuning','heldout':'One locked confirmatory pilot after candidate/protocol freeze; known to benchmark authors, not a secret external benchmark'},'tasks':tasks}
    dump(ROOT/'benchmark.json',pool);dump(ROOT/'reference_fixtures.json',gold)
    freeze={'benchmark_sha256':sha((ROOT/'benchmark.json').read_bytes()),'reference_fixtures_sha256':sha((ROOT/'reference_fixtures.json').read_bytes()),'tasks':len(tasks),'family_split':{x['family']:x['split'] for x in tasks},'task_hashes':{x['id']:sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode()) for x in tasks},'warning':'18-task pilot, 9 distinct structural families; two variants per family are clustered. No population-level quality certification. Public synthetic heldout is not contamination-proof.'}
    assert len(freeze['family_split'])==9
    for f in freeze['family_split']:assert len({x['split'] for x in tasks if x['family']==f})==1
    dump(ROOT/'BENCHMARK_FREEZE.json',freeze)
    print(json.dumps({'tasks':len(tasks),'families':9,'benchmark_sha256':freeze['benchmark_sha256']}))
if __name__=='__main__':build()
