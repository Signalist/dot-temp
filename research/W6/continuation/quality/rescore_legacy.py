"""Independent legacy-data rescore; raw inputs remain unchanged."""
import ast,collections,hashlib,json,pathlib,re
from validator import Interpreter,parse_function,stop_score
HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE/'legacy_inputs'

def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,x):(HERE/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def analyze():
    rows=[];details={};source_hashes={}
    frozen=json.loads((HERE/'LEGACY_INPUT_FREEZE.json').read_text())['files']
    for rel,digest in frozen.items():
        if h(BASE/rel)!=digest:raise ValueError('Legacy input changed: '+rel)
    for p in sorted((BASE/'artifacts').glob('resident_*/attempt_*/**/public_output.txt')):
        r=json.loads((p.parent/'result.json').read_text())
        ev=json.loads((p.parent/'host_observations.json').read_text())
        terminal=[e for e in ev if e.get('event')=='engine_terminal']
        output=p.read_text();digest=h(p)
        for name in ['public_output.txt','result.json','host_observations.json']:
            f=p.parent/name;source_hashes[str(f.relative_to(BASE))]=h(f)
        row={'source':str(p.relative_to(BASE)),'phase':r['phase'],'task_id':r['task_id'],'text_sha256':digest,'text_hash_matches_result':digest==r['output_text_sha256'],'termination':stop_score(terminal[0]) if len(terminal)==1 else 'UNKNOWN_TERMINAL_COUNT','useful_tokens':r['useful_tokens']}
        if r['phase']=='MAIN':
            tid=r['task_id']
            if tid not in details:
                if tid=='writing_short_v2c':
                    sentences=[s for s in re.split(r'(?<=[.!?])\s+',output.strip()) if s]
                    paragraphs=[s for s in re.split(r'\n\s*\n',output.strip()) if s]
                    details[tid]={'quality_case_count':1,'status':'FAIL_EXPLICIT_FIVE_SENTENCE_REQUIREMENT','sentence_count':len(sentences),'paragraph_count':len(paragraphs),'sentence_required':5,'semantic_content':'Not declared wholly incorrect; format failure is explicit','full_quality_pass':False}
                elif tid=='code_short':
                    raw=output.strip();clean=re.sub(r'^```(?:python)?\n|\n```$','',raw);tree=ast.parse(clean)
                    fs=[n for n in tree.body if isinstance(n,ast.FunctionDef)];runs=next(n for n in fs if n.name=='find_runs')
                    diagnostics=[]
                    for xs in [[],[1],[1,2,3],[2,7],[1,2,5,6]]:
                        got,pure=Interpreter(runs).call([xs.copy()]);expected=[]
                        for x in xs:
                            if expected and x==expected[-1][-1]+1:expected[-1].append(x)
                            else:expected.append([x])
                        diagnostics.append({'input':xs,'bounded_ast_result':got,'expected_partition':expected,'pass':got==expected,'input_unchanged':pure})
                    details[tid]={'quality_case_count':1,'status':'FAIL_SOURCE_CONSTRAINTS_AND_RUN_PARTITION','function_count':len(fs),'required_functions':1,'markdown_fence':raw.startswith('```'),'example_markers':sum('>>>' in (ast.get_docstring(f) or '') for f in fs),'find_runs_checks':diagnostics,'generated_code_executed':False,'analysis_method':'New author-written bounded AST interpreter only','full_quality_pass':False}
                elif tid=='reasoning_medium':
                    finals=[int(x) for x in re.findall(r'The librarian needs (\d+) shelves',output)]
                    pairs=[(120,10),(150,15),(180,18),(210,21)]
                    details[tid]={'quality_case_count':1,'status':'PASS_FOUR_FINAL_ANSWERS_ONLY','parsed_answers':finals,'expected_answers':[a//b for a,b in pairs],'final_answers_correct':finals==[a//b for a,b in pairs],'alphabetic_words':len(re.findall(r'\b[A-Za-z]+\b',output)),'approximate_word_target':250,'new_retroactive_word_gate':False,'distinct_arithmetic_templates':1,'consistency_checks':'Restate inputs and assert consistency; no independently demonstrated new check','full_quality_pass':None}
            row['quality_status']=details[tid]['status']
        else:row['quality_status']='WARMUP_NOT_QUALITY_CASE'
        rows.append(row)
    main=[x for x in rows if x['phase']=='MAIN']
    for tid,d in details.items():
        selected=[x for x in main if x['task_id']==tid];d['measurement_repetitions']=len(selected);d['distinct_output_hashes']=len({x['text_sha256'] for x in selected});d['natural_eos_count']=sum(x['termination']=='NATURAL_EOS_HOST_METADATA' for x in selected)
    result={'source_commit':'f3cb19f0ffe4ecfdb72a7e57b93e512851bcad50','new_GPU_runs':0,'requests':len(rows),'main_requests':len(main),'warmups':len(rows)-len(main),'distinct_main_quality_cases':len({x['text_sha256'] for x in main}),'task_details':details,'termination_counts':dict(collections.Counter(x['termination'] for x in rows)),'source_hashes_all_match':all(x['text_hash_matches_result'] for x in rows),'quality_matching_eligible_existing_tasks':0,'note':'Writing/code definitively fail requested output conditions. Arithmetic is a limited answer-only pass; comprehensive quality unknown. Repetitions do not increase independent quality sample count.','rows':rows}
    assert len(rows)==108 and len(main)==72 and len(details)==3
    dump('LEGACY_RESCORE.json',result);dump('LEGACY_SOURCE_HASHES.json',source_hashes)
    print(json.dumps({k:result[k] for k in ['requests','main_requests','warmups','distinct_main_quality_cases','termination_counts','source_hashes_all_match']}))
if __name__=='__main__':analyze()
