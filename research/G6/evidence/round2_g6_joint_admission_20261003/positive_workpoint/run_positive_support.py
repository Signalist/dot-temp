"""Apply frozen original two-input support code to newly qualified positive point."""
from pathlib import Path
import sys,os,json,hashlib,importlib.util
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
import numpy as np
ROOT=Path(__file__).resolve().parent
source=ROOT.parent/'transfer/run_transfer.py'
spec=importlib.util.spec_from_file_location('g6_support',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=ROOT
q=json.loads((ROOT/'QUALIFICATION.json').read_text());assert q['qualification_pass'],'Do not use unqualified positive working point'
d=np.load(ROOT/'positive_kernel.npz');q2={'new_workpoint_qualification':'QUALIFICATION.json','qualification_pass':q['qualification_pass'],'max_eigenvalue_real':q['transfer']['max_eigenvalue_real'],'max_resolvent_relative_error':q['transfer']['max_resolvent_relative_error'],'source_support_script':str(source),'source_support_script_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'positive_compute_bases_MW':[50,50]}
m.run('positive',d['lam'],d['R'],q2)
