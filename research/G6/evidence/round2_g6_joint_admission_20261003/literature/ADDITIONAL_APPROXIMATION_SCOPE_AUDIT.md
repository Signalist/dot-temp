# Additional approximation-neighbor check

Checked 2026-10-03 after the initial novelty audit, without changing numerical endpoints.

## Rote 1992: a direct mature polygon baseline

[Günter Rote, The convergence rate of the Sandwich algorithm for approximating convex functions, Computing 48 (1992)](https://page.mi.fu-berlin.de/rote/Papers/pdf/The%2Bconvergence%2Brate%2Bof%2Bthe%2BSandwich%2Balgorithm%2Bfor%2Bapproximating%2Bconvex%2Bfunctions.pdf) was opened in full. Sections 1–5 give adaptive chord/tangent enclosure methods, including nonsmooth convex functions, and worst-class quadratic decay of error with evaluation count. Its circle/parabola discussion explains the classical inverse-square polygon error used in our shared-parameter scope counterexample. The existing G6 adaptive-chord comparator is therefore explicitly a mature method. This general worst-class upper rate does not itself give the proposed instance-specific exponential-rotation arithmetic iff classification; it also does not establish that no earlier specialized theorem exists.

## Free-knot approximation

[Pham, Peiris and Sukhorukova, arXiv:2404.00008v1](https://arxiv.org/html/2404.00008v1) was opened and its main theorem and scope inspected. It addresses uniform approximation with free linear-spline knots, primarily one internal knot, sufficient optimality conditions, and mixed-integer formulations for sampled data. That is a pertinent approximation neighbor, but different from an asymptotic lower bound for every m-piece approximation of the particular infinite rotation series. We do not claim a new general free-knot optimizer or global optimality for our greedy chord experiments.

## 2012 IFS paper access remains incomplete

The official [INRIA ALICE 2012 bibliography](https://radar.inria.fr/rapportsactivite/RA2012/alice/bibliography.html) verifies the archival record [hal-00755842](https://hal.inria.fr/hal-00755842) for Mishkinis–Gentil–Lanquetin–Sokolov, *Approximate convex hull of affine iterated function system attractors*, DOI 10.1016/j.chaos.2012.07.015. The HAL record/document routes remained inaccessible through the available web retrieval tool, and no full text was obtained. The initial audit's abstract-level limitation therefore remains.

## Effect on the conclusion

The narrow proof has survived mathematical checking, and no matching complete arithmetic iff/threshold theorem was located in the inspected primary material. Originality remains provisional. The experiment comparison stays “representation theorem plus known approximation methods,” never “a new solver wins.”
