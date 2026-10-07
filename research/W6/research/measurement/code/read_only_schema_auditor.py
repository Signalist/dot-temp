"""Data-only schema helpers, reconstructed after workspace reset.

This is NOT the lost original raw audit or a calibrated measurement parser.
Its synthetic self-tests validate parsing only. No hardware/module code is run.
"""
import csv, datetime, hashlib, io, json, math, statistics
from pathlib import Path

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def require_hash(path,expected):
    actual=sha256_file(path)
    if actual!=expected:raise ValueError('source checksum mismatch')
    return actual

def timing(values):
    if not values:raise ValueError('no samples')
    if not all(math.isfinite(v) for v in values):raise ValueError('nonfinite time')
    ds=[b-a for a,b in zip(values,values[1:])];positive=[d for d in ds if d>0]
    return {'rows':len(values),'first':values[0],'last':values[-1],
            'nonincreasing':sum(d<=0 for d in ds),
            'median_positive_dt':statistics.median(positive) if positive else None,
            'max_dt':max(ds) if ds else None}

def read_nlr(stream):
    times=[];header=None;rows=0
    for line in stream:
        if line.startswith('# timestamp'):header=line.strip()
        if not line.strip() or line.startswith('#'):continue
        fields=line.split()
        if len(fields)!=10:raise ValueError('unexpected NLR field count')
        stamp=datetime.datetime.strptime(fields[0],'%Y-%m-%d_%H:%M:%S.%f')
        times.append((stamp-datetime.datetime(1970,1,1)).total_seconds())
        nums=[float(v) for v in fields[1:]]
        if not all(math.isfinite(v) for v in nums):raise ValueError('nonfinite telemetry')
        rows+=1
    return {'header':header,'timing_s':timing(times),'rows':rows,
            'timezone_asserted':False,'physical_bandwidth_identified':False,
            'nominal_clock_not_synchronized':True}

def read_darus(stream):
    reader=csv.DictReader(stream,delimiter=';')
    if reader.fieldnames!=['sensor','time[ms]','power[W]','run','status']:raise ValueError('unexpected DaRUS schema')
    groups={};rows=0
    for r in reader:
        key=(r['run'],r['status'].split(' ',1)[-1],r['sensor'])
        t=float(r['time[ms]']);p=float(r['power[W]'])
        if not math.isfinite(t) or not math.isfinite(p):raise ValueError('nonfinite record')
        groups.setdefault(key,[]).append(t);rows+=1
    return {'fields':reader.fieldnames,'rows':rows,
            'groups':[{'run':k[0],'page':k[1],'sensor':k[2],'timing_ms':timing(v)} for k,v in groups.items()],
            'groups_are_not_independent_acquisitions':True}

def read_json_or_jsonl(text):
    try:return json.loads(text)
    except json.JSONDecodeError:return [json.loads(line) for line in text.splitlines() if line.strip()]

def matching_gate(metadata):
    """Fail closed. Booleans refer to verified coverage, never inferred capability."""
    required=['same_acquisition','actual_power','command_timeline','progress_timeline',
              'true_EOS_and_reason','controller_EOS_visibility','full_recovery',
              'clock_error_bound','electrical_boundary','independent_units','licensed_access']
    if metadata.get('claim_PCC',False):required+=['simultaneous_PCC','PCC_mapping_validation']
    missing=[k for k in required if metadata.get(k) is not True]
    return {'admitted':not missing,'missing':missing,
            'structurally_ready_for_split_review':not missing,
            'numeric_or_physical_acceptance':None,
            'automatic_fit_authorization':False}

def self_test():
    checks={}
    sample='# timestamp reading-time[ns] gpu-0[mW] gpu-1[mW] gpu-2[mW] gpu-3[mW] gpu-0[C] gpu-1[C] gpu-2[C] gpu-3[C]\n2026-01-01_00:00:00.000000 1 1000 1000 1000 1000 40 40 40 40\n2026-01-01_00:00:00.100000 1 1000 1000 1000 1000 40 40 40 40\n'
    r=read_nlr(io.StringIO(sample));assert r['rows']==2 and abs(r['timing_s']['median_positive_dt']-.1)<1e-6 and not r['timezone_asserted'];checks['nlr_units_count_naive_clock']=True
    d='sensor;time[ms];power[W];run;status\nNVML;0;1;1;showing pageA\nNVML;5;1;1;showing pageA\nNVML;0;1;1;showing pageB\nNVML;0;1;1;showing pageB\n'
    r=read_darus(io.StringIO(d));assert len(r['groups'])==2 and r['groups'][1]['timing_ms']['nonincreasing']==1;checks['page_resets_preserved_duplicates_flagged']=True
    assert read_json_or_jsonl('{"a":1}\n{"a":2}\n')==[{'a':1},{'a':2}];checks['jsonl_not_confused_with_single_json']=True
    assert not matching_gate({'actual_power':True,'claim_PCC':True})['admitted'];checks['incomplete_coverage_rejected']=True
    try:read_nlr(io.StringIO(sample+'malformed\n'));raise AssertionError('bad row accepted')
    except ValueError:checks['malformed_rows_rejected']=True
    return {'status':'PASS','scope':'five synthetic parser/gate tests only; no physical measurement validation','checks':checks}

if __name__=='__main__':print(json.dumps(self_test(),indent=2))
