"""Optional official-source download; bounded size and frozen SHA256."""
import argparse, hashlib, pathlib, urllib.request
URL='https://raw.githubusercontent.com/Azure/AzurePublicDataset/790921015d50dd6aae7f7e47f39ba0e235ad6b08/data/AzureLLMInferenceTrace_conv.csv'
EXPECTED='2f1e5b666d4e3055fdbba98598ce2ec307767b9064e03e2fa46676dbcc7d0bf8'
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
with urllib.request.urlopen(URL,timeout=30) as r: raw=r.read(2_000_001)
if len(raw)!=719188 or hashlib.sha256(raw).hexdigest()!=EXPECTED: raise SystemExit('Unexpected data bytes; no file written')
out=pathlib.Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
with out.open('xb') as f: f.write(raw)
print('Wrote verified CC BY 4.0 Azure dataset; retain attribution and license notice')
