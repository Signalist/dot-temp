"""Exact contract for the continuum phase proof and deployable class-target law.

Sampling index n denotes exact rational time n/10 s; edges repeat every50
sample periods. Finite phase strings are parsed as exact rational numbers. The online
policy never receives a phase and simply thresholds the received measured P.
The frozen numerical design helper is preserved for provenance and is NOT the
semantics of infinitesimal phase neighborhoods at sample boundaries.
"""
from fractions import Fraction
import numpy as np
from design_controller import nodes,nfree,ns,areaweights,ETA,RECOVERY_AREA

def first_edge_sample(r):
 x=r if isinstance(r,Fraction) else Fraction(str(r))
 if not 0<x<=5:raise ValueError('Need exact 0<r<=5')
 # Positive integer ceil: no decimal precision context or floating operation.
 return (10*x.numerator+x.denominator-1)//x.denominator

def class_at_sample(n,first_edge,initial_high):
 if n<first_edge:return int(initial_high)
 return int(bool(initial_high)^bool((1+(n-first_edge)//50)%2))

def bin_mapping(first_edge,initial_high,feedback=True):
 nv=nfree*(2 if feedback else 1);M=np.zeros((len(nodes),nv))
 for j in range(nfree):
  # Target ending at .05+.1j is selected at the prior knot. For j>=1,
  # the latest exactly arrived sample index is j-1; j=0 uses initial class.
  cls=int(initial_high) if j==0 else class_at_sample(j-1,first_edge,initial_high)
  M[j+1,j*(2 if feedback else 1)+(cls if feedback else 0)]=1
 D=areaweights@M[1:ns];M[-3]=M[-2]=-D/(ETA**2*RECOVERY_AREA)
 return M,D

def online_power_from_measured_samples(theta,initial_high,measured_samples,feedback=True):
 """No r/phase or true P is passed. Samples indexed by exact sampling clock."""
 p=np.zeros(len(nodes))
 for j in range(nfree):
  cls=int(initial_high) if j==0 else int(measured_samples[j-1]>=75.)
  p[j+1]=theta[j*(2 if feedback else 1)+(cls if feedback else 0)]
 D=areaweights@p[1:ns];p[-3]=p[-2]=-D/(ETA**2*RECOVERY_AREA)
 return p
