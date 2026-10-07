"""Reproduce descriptive empirical W from the already-downloaded official CSV.
No network calls, no hardware calls, and no external source code are executed.
The model may use this PMF as trace-driven synthetic work; it is not an EOS reason trace.
"""
from pathlib import Path
import collections,csv,hashlib,json,statistics
P=Path(__file__).resolve().parent
raw=P/'AzureLLMInferenceTrace_conv.csv'
assert hashlib.sha256(raw.read_bytes()).hexdigest()=='2f1e5b666d4e3055fdbba98598ce2ec307767b9064e03e2fa46676dbcc7d0bf8'
rows=list(csv.DictReader(raw.open()))
assert rows and set(rows[0])=={'TIMESTAMP','ContextTokens','GeneratedTokens'}
x=[int(r['GeneratedTokens']) for r in rows]
assert all(v>=0 for v in x)
c=collections.Counter(x);n=len(x);xs=sorted(x)
def q(t):return xs[min(n-1,int(t*(n-1)))]
summary={'n_rows':n,'n_distinct_output_lengths':len(c),'generated_tokens':{'min':min(x),'max':max(x),'mean':statistics.mean(x),'p25':q(.25),'median':q(.5),'p75':q(.75),'p90':q(.9),'p95':q(.95),'p99':q(.99)},'zero_length_rows':c[0],'timestamp_min':min(r['TIMESTAMP'] for r in rows),'timestamp_max':max(r['TIMESTAMP'] for r in rows),'context_tokens_min':min(int(r['ContextTokens']) for r in rows),'context_tokens_max':max(int(r['ContextTokens']) for r in rows),'top_atoms':c.most_common(12),'date_note':'README says collected 2023-11-11, CSV timestamps start 2023-11-16; preserve observed timestamp range, do not silently reconcile','interpretation':'Observed generated-token distribution only; natural EOS vs cap reason absent; not constant-work tokens, not measured power'}
with (P/'empirical_output_length_pmf.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['generated_tokens','count','probability','cdf']);cum=0
 for v,ct in sorted(c.items()):cum+=ct;w.writerow([v,ct,ct/n,cum/n])
assert cum==n
(P/'empirical_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
