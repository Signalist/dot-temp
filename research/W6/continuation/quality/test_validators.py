import copy,hashlib,json,pathlib,unittest
from validator import *
ROOT=pathlib.Path(__file__).resolve().parent
POOL=json.loads((ROOT/'benchmark.json').read_text());TASKS={x['id']:x for x in POOL['tasks']};GOLD=json.loads((ROOT/'reference_fixtures.json').read_text())
TERMINAL={'finish_reason':'stop','ignore_eos':False,'terminal_eos_token_id':151645,'declared_eos_token_ids':[151645,151643],'stop_class':'natural_eos_token_host_verified'}
class Tests(unittest.TestCase):
    def test_all_reference_fixtures(self):
        for tid,t in TASKS.items():
            with self.subTest(task=tid):
                r=score(t,GOLD[tid],TERMINAL)
                expected={'code':'PASS_FUNCTIONAL_SUBSET','math':'PASS_EXACT_ANSWER_AND_CHECK','writing':'MACHINE_GATE_PASS_HUMAN_PENDING'}[t['domain']]
                self.assertEqual(r['status'],expected,r)
                self.assertEqual(r['eligible_quality_matched_claim'],t['domain']!='writing')
    def test_code_structural_properties(self):
        for t in TASKS.values():
            if t['domain']!='code':continue
            fn=parse_function(GOLD[t['id']])
            for case in t['cases']:
                xs=case['args'][0];got,pure=Interpreter(fn).call([xs.copy()]);self.assertTrue(pure)
                if t['function'].startswith('count_'):self.assertTrue(0<=got<=len(xs))
                elif t['function']=='prefix_sums':
                    self.assertEqual(len(got),len(xs));self.assertEqual([got[i]-(got[i-1] if i else 0) for i in range(len(got))],xs)
                elif t['function']=='suffix_sums':
                    self.assertEqual(len(got),len(xs));self.assertEqual([got[i]-(got[i+1] if i+1<len(got) else 0) for i in range(len(got))],xs)
                else:
                    self.assertEqual([x for run in got for x in run],xs)
                    self.assertTrue(all(len(run)>0 for run in got))
                    delta=1 if t['function']=='consecutive_runs' else 0
                    self.assertTrue(all(b-a==delta for run in got for a,b in zip(run,run[1:])))
                    self.assertTrue(all(b[0]-a[-1]!=delta for a,b in zip(got,got[1:])))
    def test_family_separation(self):
        groups={}
        for t in TASKS.values():groups.setdefault(t['family'],set()).add(t['split'])
        self.assertEqual(len(groups),9);self.assertTrue(all(len(x)==1 for x in groups.values()))
        self.assertEqual(len(TASKS),18)
    def test_frozen_hash(self):
        freeze=json.loads((ROOT/'BENCHMARK_FREEZE.json').read_text())
        self.assertEqual(freeze['benchmark_sha256'],hashlib.sha256((ROOT/'benchmark.json').read_bytes()).hexdigest())
    def test_code_negative_fixtures(self):
        t=TASKS['code_consecutive_runs'];s=GOLD[t['id']]
        mutants=[('fences','```python\n'+s+'```'),('extra_function',s+'\ndef extra(xs):\n    return xs\n'),('wrong_example',s.replace('[[1, 2], [5]]','[[1, 2]]')),('missing_last',s.replace('for x in xs:', 'for x in xs[:-1]:')),('wrong_predicate',s.replace('current[-1] + 1','current[-1] + 2'))]
        for label,m in mutants:
            with self.subTest(label=label):self.assertNotEqual(code_score(t,m)['status'],'PASS_FUNCTIONAL_SUBSET')
    def test_code_no_io_or_execution(self):
        t=TASKS['code_count_positive']
        for body in ['return open("/etc/passwd").read()','return __import__("os").system("echo BAD")','while True:\n        pass','return ().__class__.__bases__','return eval("1+1")','return [0] * 999999999','return len(range(999999999))']:
            src='def count_positive(xs):\n    """Count positives.\n    >>> count_positive([1])\n    1\n    """\n    '+body+'\n'
            with self.subTest(body=body):self.assertNotEqual(code_score(t,src)['status'],'PASS_FUNCTIONAL_SUBSET')
    def test_resource_bounds(self):
        t=TASKS['code_count_positive']
        bodies=["return '%257s' % 'x'",'y=xs\n    y += [0]\n    return len([x for x in xs if x > 0])','x=[0]\n    x *= 257\n    return 1','return len(range(10**100))','x=[0]\n    for i in range(9):\n        x=[x]*4\n    return 1','x=[]\n    x.append(x)\n    return 1']
        for body in bodies:
            src='def count_positive(xs):\n    """Count positive integers.\n    >>> count_positive([1])\n    1\n    """\n    '+body+'\n'
            with self.subTest(body=body):self.assertNotEqual(code_score(t,src)['status'],'PASS_FUNCTIONAL_SUBSET')
        with self.assertRaises(Limit):Interpreter(None).bound(range(0,10**100))
        for dom,tid in [('writing','writing_library_notice'),('math','math_book_stock')]:
            self.assertEqual(score(TASKS[tid],'['*2000+']'*2000)['status'],'FAIL_VALIDATION')
    def test_code_constant_overfit(self):
        t=TASKS['code_count_positive'];src=GOLD[t['id']].replace('return len([x for x in xs if x > 0])','return 1')
        self.assertEqual(code_score(t,src)['status'],'FAIL_FUNCTIONAL')
    def test_math_false_positive_stress(self):
        t=TASKS['math_book_stock']
        for s in ['41','{"answer": true, "check":"41-12+8=37"}','{"answer":41,"answer":0,"check":"41-12+8=37"}','{"answer":41,"check":"41-12+8=38"}','{"answer":41,"check":"41-12+8=37","extra":0}','{"answer":NaN,"check":"41-12+8=37"}']:
            self.assertEqual(math_score(t,s)['status'],'FAIL_VALIDATION')
    def test_writing_content_and_format(self):
        t=TASKS['writing_library_notice'];s=json.loads(GOLD[t['id']])
        for mutation in ['wrong_time','missing_fact','negated','extra_sentence','duplicate_key']:
            d=copy.deepcopy(s)
            if mutation=='wrong_time':d['sentences'][0]=d['sentences'][0].replace('09:00','10:00')
            if mutation=='missing_fact':d['sentences'][1]='Visitors can enjoy their time inside.'
            if mutation=='negated':d['sentences'][0]=d['sentences'][0].replace('opens','never opens')
            if mutation=='extra_sentence':d['sentences'].append('Please visit us soon.')
            text=json.dumps(d) if mutation!='duplicate_key' else '{"sentences":[],"sentences":[]}'
            self.assertEqual(writing_score(t,text)['status'],'FAIL_VALIDATION')
    def test_writing_semantic_loophole_requires_human(self):
        t=TASKS['writing_room_comparison'];d=json.loads(GOLD[t['id']]);d['sentences'][0]='The reading room has 12 seats and a swimming pool.'
        r=score(t,json.dumps(d),TERMINAL)
        self.assertEqual(r['status'],'MACHINE_GATE_PASS_HUMAN_PENDING');self.assertFalse(r['eligible_quality_matched_claim'])
    def test_eos_and_truncation(self):
        self.assertEqual(stop_score(TERMINAL),'NATURAL_EOS_HOST_METADATA')
        self.assertEqual(stop_score({'finish_reason':'length'}),'TRUNCATED_LENGTH')
        for d in [None,{},[],dict(TERMINAL,terminal_eos_token_id=None,declared_eos_token_ids=[None]),dict(TERMINAL,ignore_eos=True),dict(TERMINAL,terminal_eos_token_id=3),dict(TERMINAL,stop_class='custom_stop')]:self.assertNotEqual(stop_score(d),'NATURAL_EOS_HOST_METADATA')
        t=TASKS['math_book_stock'];self.assertFalse(score(t,GOLD[t['id']],{'finish_reason':'length'})['eligible_quality_matched_claim'])
if __name__=='__main__':unittest.main(verbosity=2)
