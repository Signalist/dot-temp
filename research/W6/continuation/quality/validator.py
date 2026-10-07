"""CPU-only validators. Never exec/eval/compile/import generated source.
The bounded interpreter is a small Python subset, not a Python runtime sandbox.
Unsupported constructs return UNKNOWN rather than pretending functional failure.
"""
import ast, copy, json, operator, re

class Unsupported(ValueError): pass
class Limit(ValueError): pass
class Returned(Exception):
    def __init__(self, value): self.value=value

class Interpreter:
    OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Mod:operator.mod,ast.FloorDiv:operator.floordiv}
    CMPS={ast.Eq:operator.eq,ast.NotEq:operator.ne,ast.Lt:operator.lt,ast.LtE:operator.le,ast.Gt:operator.gt,ast.GtE:operator.ge,ast.In:lambda x,y:x in y,ast.NotIn:lambda x,y:x not in y}
    BUILTINS={'len':len,'sum':sum,'sorted':sorted,'min':min,'max':max,'abs':abs,'range':range,'list':list,'reversed':reversed,'enumerate':enumerate}
    def __init__(self, function, budget=10000): self.fn=function;self.steps=budget
    def tick(self):
        self.steps-=1
        if self.steps<0: raise Limit('step_budget')
    def bound(self,v):
        # Count expanded nodes, including aliases, before any host comparison.
        remaining=[2048]
        def visit(x,depth,ancestors):
            remaining[0]-=1
            if remaining[0]<0 or depth>8:raise Limit('expanded_value_budget')
            if isinstance(x,int) and x.bit_length()>128:raise Limit('integer_bits')
            if isinstance(x,range):
                count=max(0,(x.stop-x.start+(x.step-1 if x.step>0 else x.step+1))//x.step)
                if count>256:raise Limit('range_size')
            elif isinstance(x,(list,tuple,dict,str)):
                if len(x)>256:raise Limit('container_size')
                if not isinstance(x,str):
                    if id(x) in ancestors:raise Limit('cyclic_value')
                    for y in (list(x.items()) if isinstance(x,dict) else x):visit(y,depth+1,ancestors|{id(x)})
        visit(v,0,set());return v
    def binary(self,op,a,b):
        self.bound(a);self.bound(b)
        if isinstance(op,(ast.Mod,ast.FloorDiv,ast.Sub)) and not (type(a) is int and type(b) is int):raise Unsupported('integer_operands_required')
        if isinstance(op,ast.Add) and not ((type(a) is int and type(b) is int) or (type(a) is type(b) and isinstance(a,(list,tuple,str)))):raise Unsupported('addition_types')
        if isinstance(op,ast.Mult):
            if isinstance(a,(str,list,tuple)) and isinstance(b,int) and len(a)*max(b,0)>256:raise Limit('allocation')
            if isinstance(b,(str,list,tuple)) and isinstance(a,int) and len(b)*max(a,0)>256:raise Limit('allocation')
        return self.bound(self.OPS[type(op)](a,b))
    def expr(self,n,e):
        self.tick()
        if isinstance(n,ast.Constant):
            if not isinstance(n.value,(int,str,bool,type(None))):raise Unsupported('constant')
            return self.bound(n.value)
        if isinstance(n,ast.Name):
            if n.id not in e:raise Unsupported('unknown_name:'+n.id)
            return e[n.id]
        if isinstance(n,(ast.List,ast.Tuple)):
            v=[self.expr(x,e) for x in n.elts];return self.bound(v if isinstance(n,ast.List) else tuple(v))
        if isinstance(n,ast.Subscript):
            v=self.expr(n.value,e)
            k=slice(*(self.expr(x,e) if x else None for x in (n.slice.lower,n.slice.upper,n.slice.step))) if isinstance(n.slice,ast.Slice) else self.expr(n.slice,e)
            return self.bound(v[k])
        if isinstance(n,ast.UnaryOp):
            v=self.expr(n.operand,e)
            if isinstance(n.op,ast.Not):return not v
            if isinstance(n.op,ast.USub):return self.bound(-v)
            raise Unsupported('unary')
        if isinstance(n,ast.BinOp) and type(n.op) in self.OPS:
            a,b=self.expr(n.left,e),self.expr(n.right,e)
            return self.binary(n.op,a,b)
        if isinstance(n,ast.Compare):
            a=self.expr(n.left,e)
            for op,x in zip(n.ops,n.comparators):
                if type(op) not in self.CMPS:raise Unsupported('compare')
                b=self.expr(x,e);self.bound(a);self.bound(b)
                if not self.CMPS[type(op)](a,b):return False
                a=b
            return True
        if isinstance(n,ast.BoolOp):
            for x in n.values:
                v=self.expr(x,e)
                if isinstance(n.op,ast.And) and not v:return v
                if isinstance(n.op,ast.Or) and v:return v
            return v
        if isinstance(n,ast.IfExp):return self.expr(n.body if self.expr(n.test,e) else n.orelse,e)
        if isinstance(n,ast.Call):
            if n.keywords:raise Unsupported('keyword_arguments')
            args=[self.expr(x,e) for x in n.args]
            self.bound(args)
            if isinstance(n.func,ast.Name) and n.func.id in self.BUILTINS:
                v=self.BUILTINS[n.func.id](*args)
                if isinstance(v,(enumerate,type(reversed([])))):v=list(v)
                return self.bound(v)
            if isinstance(n.func,ast.Attribute) and n.func.attr=='append' and len(args)==1:
                target=self.expr(n.func.value,e)
                if not isinstance(target,list):raise Unsupported('append_non_list')
                if len(target)>=256:raise Limit('append_size')
                self.bound(target+[args[0]])
                if args[0] is target:raise Limit('cyclic_value')
                target.append(args[0]);self.bound(target);return None
            raise Unsupported('call')
        if isinstance(n,ast.ListComp):
            if len(n.generators)!=1 or n.generators[0].is_async:raise Unsupported('comprehension')
            g=n.generators[0];out=[]
            for v in self.expr(g.iter,e):
                ee=e.copy();self.assign(g.target,v,ee)
                if all(self.expr(c,ee) for c in g.ifs):out.append(self.expr(n.elt,ee));self.bound(out)
            return out
        raise Unsupported(type(n).__name__)
    def assign(self,n,v,e):
        self.tick()
        if isinstance(n,ast.Name):e[n.id]=v
        elif isinstance(n,(ast.Tuple,ast.List)) and len(n.elts)==len(v):
            for a,b in zip(n.elts,v):self.assign(a,b,e)
        else:raise Unsupported('assignment_target')
    def block(self,body,e):
        for n in body:
            self.tick()
            if isinstance(n,ast.Return):raise Returned(self.expr(n.value,e) if n.value else None)
            if isinstance(n,ast.Assign):
                v=self.expr(n.value,e)
                for t in n.targets:self.assign(t,v,e)
            elif isinstance(n,ast.AugAssign):
                if not isinstance(n.target,ast.Name) or type(n.op) not in self.OPS:raise Unsupported('augassign')
                if type(e[n.target.id]) is not int:raise Unsupported('augassign_integer_only')
                self.assign(n.target,self.binary(n.op,e[n.target.id],self.expr(n.value,e)),e)
            elif isinstance(n,ast.Expr):self.expr(n.value,e)
            elif isinstance(n,ast.If):self.block(n.body if self.expr(n.test,e) else n.orelse,e)
            elif isinstance(n,ast.For):
                for v in self.expr(n.iter,e):self.assign(n.target,v,e);self.block(n.body,e)
                self.block(n.orelse,e)
            elif isinstance(n,ast.Pass):pass
            elif not isinstance(n,(ast.Return,ast.Assign)):raise Unsupported(type(n).__name__)
    def call(self,args):
        if self.fn.args.defaults or self.fn.args.kwonlyargs or self.fn.args.vararg or self.fn.args.kwarg:raise Unsupported('signature')
        if len(args)!=len(self.fn.args.args):raise ValueError('arity')
        self.bound(args);before=copy.deepcopy(args);e=dict(zip([x.arg for x in self.fn.args.args],args))
        try:self.block(self.fn.body,e);value=None
        except Returned as x:value=x.value
        return value,args==before

def parse_function(text,name=None,require_example=True):
    if len(text)>20000:raise Limit('source_bytes')
    if '```' in text:raise ValueError('markdown_fence')
    tree=ast.parse(text)
    if len(list(ast.walk(tree)))>2000:raise Limit('ast_nodes')
    if len(tree.body)!=1 or not isinstance(tree.body[0],ast.FunctionDef):raise ValueError('exactly_one_function')
    fn=tree.body[0]
    if name and fn.name!=name:raise ValueError('function_name')
    if fn.decorator_list or fn.returns or any(a.annotation for a in fn.args.args):raise Unsupported('decorator_annotation')
    doc=ast.get_docstring(fn)
    if not doc:raise ValueError('missing_docstring')
    if require_example and not re.search(r'>>>\s*'+re.escape(fn.name)+r'\(',doc):raise ValueError('missing_doctest_example')
    for n in ast.walk(fn):
        if isinstance(n,(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal,ast.ClassDef,ast.Lambda,ast.AsyncFunctionDef,ast.With,ast.Try,ast.While)):raise Unsupported(type(n).__name__)
        if isinstance(n,ast.Name) and n.id.startswith('__'):raise Unsupported('dunder')
        if isinstance(n,ast.Attribute) and n.attr!='append':raise Unsupported('attribute')
    return fn

def code_score(task,text):
    try:
        fn=parse_function(text,task['function']);results=[]
        doc=ast.get_docstring(fn)
        example=re.search(r'>>>\s*(.+)\n\s*([^\n]+)',doc)
        if not example:raise ValueError('example_missing_expected_result')
        call=ast.parse(example.group(1),mode='eval').body
        if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Name) or call.func.id!=fn.name or call.keywords:raise ValueError('example_call')
        args=[ast.literal_eval(a) for a in call.args]
        expected=ast.literal_eval(example.group(2).strip())
        if any(not isinstance(a,list) or len(a)>64 or any(type(x)!=int or abs(x)>100000 for x in a) for a in args):raise ValueError('example_input_bounds')
        actual,pure=Interpreter(fn).call(args)
        if actual!=expected or type(actual)!=type(expected) or not pure:raise ValueError('incorrect_doctest_example')
        for c in task['cases']:
            v,pure=Interpreter(fn).call(copy.deepcopy(c['args']))
            results.append({'pass':v==c['expected'] and type(v)==type(c['expected']) and pure,'input_unchanged':pure})
        return {'status':'PASS_FUNCTIONAL_SUBSET' if all(c['pass'] for c in results) else 'FAIL_FUNCTIONAL','checks':results,'complete_python_semantics':False}
    except Unsupported as e:return {'status':'UNKNOWN_UNSUPPORTED','reason':str(e)}
    except (ValueError,SyntaxError,TypeError,KeyError,IndexError,ZeroDivisionError,Limit,RecursionError,OverflowError) as e:return {'status':'FAIL_VALIDATION','reason':str(e)}

def strict_json(text):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('duplicate_key')
            d[k]=v
        return d
    if len(text)>20000:raise ValueError('too_long')
    return json.loads(text,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))

def math_score(task,text):
    try:
        d=strict_json(text)
        if not isinstance(d,dict) or set(d)!={'answer','check'}:raise ValueError('exact_keys')
        if type(d['answer']) is not int or d['answer']!=task['answer']:raise ValueError('wrong_answer')
        if d['check']!=task['check']:raise ValueError('wrong_inverse_check')
        return {'status':'PASS_EXACT_ANSWER_AND_CHECK','reasoning_certified':False}
    except (ValueError,TypeError,RecursionError,OverflowError) as e:return {'status':'FAIL_VALIDATION','reason':str(e)}

def writing_score(task,text):
    try:
        d=strict_json(text)
        if not isinstance(d,dict) or set(d)!={'sentences'}:raise ValueError('exact_keys')
        s=d['sentences']
        if not isinstance(s,list) or len(s)!=len(task['facts']) or not all(isinstance(x,str) for x in s):raise ValueError('sentence_count')
        checks=[]
        for sentence,fact in zip(s,task['facts']):
            tokens=re.findall(r"[A-Za-z]+|\d+(?::\d+)?",sentence.lower())
            anchors=all(re.search(r'(?<!\w)'+re.escape(a.lower())+r'(?!\w)',sentence.lower()) for a in fact['anchors'])
            neg=bool(set(tokens)&{'not','never','cancelled','canceled','closed','false'})
            nums=re.findall(r'\d+(?::\d+)?',sentence)
            good=anchors and not neg and nums==fact['numbers'] and len(tokens)>=5 and len(tokens)<=30 and len(re.findall(r'[.!?](?:\s|$)',sentence))==1
            checks.append(good)
        if not all(checks):raise ValueError('fact_coverage_number_or_sentence_gate')
        return {'status':'MACHINE_GATE_PASS_HUMAN_PENDING','fact_gates':checks,'semantic_quality_certified':False,'human_rubric':['All source facts accurately conveyed','No unsupported factual additions','Coherent and useful for the specified audience','Genre and tone fit the task']}
    except (ValueError,TypeError,RecursionError,OverflowError) as e:return {'status':'FAIL_VALIDATION','reason':str(e)}

def stop_score(meta):
    if not isinstance(meta,dict) or not meta:return 'UNKNOWN_NO_TERMINAL_EVIDENCE'
    token=meta.get('terminal_eos_token_id');declared=meta.get('declared_eos_token_ids')
    valid_eos=type(token) is int and token>=0 and isinstance(declared,list) and all(type(x) is int and x>=0 for x in declared) and token in declared
    if meta.get('finish_reason')=='length':return 'TRUNCATED_LENGTH'
    if meta.get('finish_reason')=='stop' and meta.get('ignore_eos') is False and valid_eos and meta.get('stop_class')=='natural_eos_token_host_verified':return 'NATURAL_EOS_HOST_METADATA'
    return 'UNKNOWN_OR_CUSTOM_STOP'

def score(task,text,terminal=None):
    result={'code':code_score,'math':math_score,'writing':writing_score}[task['domain']](task,text)
    result['termination']=stop_score(terminal)
    result['eligible_quality_matched_claim']=result['status'] in {'PASS_FUNCTIONAL_SUBSET','PASS_EXACT_ANSWER_AND_CHECK'} and result['termination']=='NATURAL_EOS_HOST_METADATA'
    return result
