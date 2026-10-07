#!/usr/bin/env python3
"""Portable orchestration only: copies, never patches or imports archived producers."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source/G4_round3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_archive():
    manifest = json.loads((ROOT / 'EVIDENCE_INDEX.json').read_text())
    bad = []
    for row in manifest['files']:
        p = ROOT / row['path']
        if not p.is_file() or p.stat().st_size != row['bytes'] or sha(p) != row['sha256']:
            bad.append(row['path'])
    if bad:
        raise RuntimeError('Archive integrity failure: ' + repr(bad))
    return len(manifest['files'])


def normalize(value):
    # Producer execution timings and environment metadata are not scientific results.
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items() if k not in ('seconds', 'python', 'numpy', 'scipy')}
    if isinstance(value, list):
        return [normalize(x) for x in value]
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode', choices=('exact', 'checks', 'full'), default='checks')
    ap.add_argument('--output', type=Path, required=True, help='A new, nonexistent output directory outside this package')
    ap.add_argument('--historical-round2', type=Path, help='Optional original round2_g4_identifiability_20261003 directory. Its full manifest is copied and checked; absent by design in this package.')
    args = ap.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents or output.exists():
        ap.error('--output must be a new, nonexistent directory outside this package')
    checked = verify_archive()
    output.mkdir(parents=True)
    work = output / 'work/G4_round3'
    work.parent.mkdir(parents=True)
    shutil.copytree(SOURCE, work)
    logs = output / 'logs'
    logs.mkdir()
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', MPLCONFIGDIR=str(output/'mplconfig'), XDG_CACHE_HOME=str(output/'cache'))
    versions = {}
    for name in ('numpy', 'scipy', 'sympy', 'matplotlib'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    result = {'mode': args.mode, 'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
              'environment': {'python': sys.version, 'platform': platform.platform(), 'packages': versions},
              'archive_files_verified_before': checked, 'source_code_modified': False,
              'stages': [], 'comparisons': [],
              'historical_round2': 'not requested; excluded from portable archive',
              'note': 'Work is a disposable copy. Certificate verification is exact rational arithmetic. Theory/threshold suites mix exact witnesses with finite numerical LP checks, not a replacement for theorem proofs.'}

    def save():
        (output/'REPLAY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')

    def stage(name, rel):
        log = logs / (name + '.log')
        start = time.monotonic()
        with log.open('w') as f:
            p = subprocess.run([sys.executable, '-B', str(work/rel)], cwd=output, env=env, stdout=f, stderr=subprocess.STDOUT)
        row = {'name': name, 'script': rel, 'exit_code': p.returncode, 'elapsed_seconds': round(time.monotonic()-start,3), 'log': str(log.relative_to(output)), 'log_sha256': sha(log)}
        result['stages'].append(row)
        save()
        print(name + ': ' + ('PASS' if p.returncode == 0 else 'FAIL'), flush=True)
        if p.returncode:
            raise RuntimeError('Stage failed; inspect '+str(log))

    def compare(rel, producer=False):
        a = SOURCE/rel
        b = work/rel
        byte_match = sha(a) == sha(b)
        semantic = normalize(json.loads(a.read_text())) == normalize(json.loads(b.read_text()))
        row = {'file': rel, 'byte_identical': byte_match, 'scientific_json_identical': semantic,
               'ignored_for_semantic_comparison': ['seconds', 'python', 'numpy', 'scipy'],
               'saved_sha256': sha(a), 'replayed_sha256': sha(b)}
        result['comparisons'].append(row)
        save()
        if not semantic:
            raise RuntimeError('Scientific JSON mismatch: '+rel+'; inspect both files rather than accepting different results')

    try:
        stage('01_saved_exact_certificates','validation/independent_saved_certificate_check.py')
        compare('validation/independent_saved_certificate_check.json')
        if args.mode != 'exact':
            stage('02_independent_theory','validation/independent_theory_checks.py')
            compare('validation/independent_theory_checks.json')
            stage('03_independent_t6_threshold','validation/independent_t6_threshold_check.py')
            compare('validation/independent_t6_threshold_check.json')
        if args.mode == 'full':
            stage('04_produce_workloads','experiments/run_workload_study.py')
            stage('05_produce_boundaries','experiments/run_boundaries.py')
            for rel in ('dag_results.json','finite_horizons.json','leakage_results.json','SUMMARY.json','boundary_results.json'):
                compare('experiments/'+rel,producer=True)
            result['comparisons'].append({'file':'experiments/dag_results.csv','byte_identical': sha(SOURCE/'experiments/dag_results.csv') == sha(work/'experiments/dag_results.csv')})
            stage('06_rebuilt_exact_certificates','validation/independent_saved_certificate_check.py')
            data=json.loads((work/'validation/independent_saved_certificate_check.json').read_text())
            assert data['all_passed'] and data['records_checked'] == 89
            result['rebuilt_exact_certificates']={'records_checked': data['records_checked'],'all_passed': data['all_passed']}
            stage('07_figures','report/make_figures.py')
            result['figure_replay']=[{'file':str(p.relative_to(work)),'bytes':p.stat().st_size,'sha256':sha(p),'byte_identical_to_saved':sha(p)==sha(SOURCE/p.relative_to(work))} for p in sorted((work/'report/figures').iterdir()) if p.is_file()]
            assert len(result['figure_replay'])==4 and all(r['bytes']>1000 for r in result['figure_replay'])
        if args.historical_round2:
            old=args.historical_round2.resolve()
            dest=work.parent/'round2_g4_identifiability_20261003'
            manifest=json.loads((old/'SCIENCE_MANIFEST.json').read_text())
            dest.mkdir()
            shutil.copy2(old/'SCIENCE_MANIFEST.json',dest/'SCIENCE_MANIFEST.json')
            for r in manifest['files']:
                rel=Path(r['path'])
                if rel.is_absolute() or '..' in rel.parts:
                    raise RuntimeError('Unsafe historical manifest path')
                src=old/rel
                if not src.is_file() or sha(src)!=r['sha256']:
                    raise RuntimeError('Historical source integrity failure: '+str(rel))
                (dest/rel).parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(src,dest/rel)
            stage('08_optional_historical_and_producer_checker','validation/check_saved_certificates.py')
            result['historical_round2']={'manifest_files_copied_and_checked':len(manifest['files']),'all_passed':True}
        result['archive_files_verified_after']=verify_archive()
        result['all_requested_stages_passed']=True
        save()
        print('Replay complete: '+str(output/'REPLAY_RESULT.json'))
    except Exception as exc:
        result['all_requested_stages_passed']=False
        result['error']=str(exc)
        save()
        raise

if __name__ == '__main__':
    main()
