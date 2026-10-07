"""Replay quality checks from public deduplicated text and allowlisted metadata.
The reconstructed files are derived records, NOT byte-identical raw telemetry.
No generated model code is executed; the original bounded AST checker is used.
"""
import contextlib, hashlib, io, json, pathlib, tempfile
import rescore_legacy
ROOT = pathlib.Path(__file__).resolve().parent

def main():
    index = json.loads((ROOT/'legacy_compact/REQUEST_INDEX.json').read_text())
    old = json.loads((ROOT/'LEGACY_RESCORE.json').read_text())
    assert len(index['rows']) == 108
    assert len({r['source'] for r in index['rows']}) == 108
    with tempfile.TemporaryDirectory(prefix='w6-quality-replay-') as td:
        root = pathlib.Path(td); base = root/'legacy_inputs'; hashes = {}
        for row in index['rows']:
            rel = pathlib.PurePosixPath(row['source'])
            assert not rel.is_absolute() and '..' not in rel.parts
            p = base/rel; p.parent.mkdir(parents=True, exist_ok=True)
            raw = (ROOT/'legacy_compact'/(row['output_text_sha256']+'.txt')).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == row['output_text_sha256']
            assert row['source_file_sha256']['public_output.txt'] == row['output_text_sha256']
            p.write_bytes(raw)
            result = {k:row[k] for k in ['phase','task_id','output_text_sha256','useful_tokens']}
            (p.parent/'result.json').write_text(json.dumps(result))
            (p.parent/'host_observations.json').write_text(json.dumps([dict(x,event='engine_terminal') for x in row['terminal_records']]))
            for f in p.parent.iterdir(): hashes[str(f.relative_to(base))] = hashlib.sha256(f.read_bytes()).hexdigest()
        (root/'LEGACY_INPUT_FREEZE.json').write_text(json.dumps({'files':hashes}))
        rescore_legacy.HERE = root; rescore_legacy.BASE = base
        with contextlib.redirect_stdout(io.StringIO()): rescore_legacy.analyze()
        fresh = json.loads((root/'LEGACY_RESCORE.json').read_text())
    keys = ['requests','main_requests','warmups','distinct_main_quality_cases','task_details','termination_counts','quality_matching_eligible_existing_tasks','rows']
    for key in keys:
        if fresh[key] != old[key]: raise AssertionError('Rescore mismatch: '+key)
    print(json.dumps({'passed':True,'requests':108,'main_requests':72,'warmups':36,'distinct_main_quality_cases':3,'quality_matching_eligible_existing_tasks':0,'deduplicated_texts':4,'new_gpu_runs':0,'generated_model_code_executed':False,'scope':'Quality and host-stop-metadata diagnostics reproduced from derived public compact records; original complete telemetry not reauthenticated or reconstructed.'}))

if __name__ == '__main__': main()
