#!/usr/bin/env python3
"""Compile actual source backend and compare deterministic small cases with exhaustive words."""
from pathlib import Path
import ctypes,itertools,json,subprocess,tempfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'evidence/round3_g6_20261004/contracts/window_dp.cpp'
rng=np.random.default_rng(20261007);count=0
with tempfile.TemporaryDirectory(prefix='g6_dp_') as d:
 lib=Path(d)/'window_dp.so'
 subprocess.run(['g++','-O2','-std=c++17','-fopenmp','-shared','-fPIC',str(src),'-o',str(lib)],check=True)
 f=ctypes.CDLL(str(lib)).window_dp
 arr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
 f.argtypes=[arr,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,arr]
 for L in [2,4,8]:
  n=8;words=np.array(list(itertools.product([0,1],repeat=n)),dtype=int)
  for B in sorted(set([0,1,L//2,L])):
   rewards=np.ascontiguousarray(rng.normal(size=(3,n)));out=np.zeros(3)
   # Prefix/suffix windows use zero padding exactly as the production contract.
   padded=np.pad(words,((0,0),(L-1,L-1)))
   valid=np.all(np.stack([padded[:,j:j+L].sum(axis=1)<=B for j in range(n+L-1)]),axis=0)
   expected=(rewards@words[valid].T).max(axis=1)
   f(rewards,3,n,L,B,out)
   np.testing.assert_allclose(out,expected,rtol=1e-12,atol=1e-12);count+=3
print(json.dumps({'pass':True,'compiled_actual_cpp':True,'deterministic_small_rows':count,'scope':'finite DP implementation check, not an interval or physical certificate'}))
