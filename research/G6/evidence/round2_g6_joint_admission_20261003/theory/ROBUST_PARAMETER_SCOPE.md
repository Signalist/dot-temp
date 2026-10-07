# Why exact-angle face complexity is not universal grid complexity

This is an analytical scope counterexample, not a new algorithm or a frozen numerical performance test.

## A shared parameter can change the representation class

Let 0<r<1 and let one unknown constant kappa in [0,pi/2] be shared by both ports and every block. Consider

    x[k+1] = r x[k] + s[k](a1 cos(kappa)+a2 sin(kappa)),
    x[0]=0, s[k] in {-1,+1}, a1,a2>=0.

For a fixed kappa, exact all-time robust support is

    (a1 cos(kappa)+a2 sin(kappa))/(1-r).

Taking the worst fixed kappa outside the whole trajectory support gives

    sup_kappa support = sqrt(a1^2+a2^2)/(1-r).

Thus each known-parameter domain is a halfspace but the correctly shared-parameter robust domain is a quarter disk. No adversarial parameter switching was used. In this special positive scalar model allowing switching happens to give the same boundary, but that coincidence is not true generally; the main rotating-model experiment supplies a strict counterexample.

The disk has an exact constant-size second-order-cone representation. Approximating any fixed nonzero angular arc by a polygon with uniform radial error epsilon instead needs Theta(epsilon^(-1/2)) sides. The lower bound follows because one of m straight pieces spans an angular gap of order 1/m and its midpoint sagitta is of order 1/m^2; equally spaced chords/tangents give the matching upper bound. This is classical circle approximation, included only as a warning about the scope of the arithmetic theorem.

## Balanced physical blocks are possible

Take the continuous first-order model

    xdot = -lambda x + cos(kappa) deltaP1 + sin(kappa) deltaP2,
    deltaPi(kT+t)=s[k] ai q(t),

where q is a bounded, nonzero, fixed zero-area template and its weighted integral against exp(-lambda(T-t)) is nonzero. Normalize the common template's block gain into ai. Then r=exp(-lambda T), and the block equation above follows without resetting x or changing kappa. Positive baselines make total power nonnegative. The same explicit affine power-work assumption used in the main report gives equal completed work per block. Since both ports use the same template and plant kernel, the full continuous-time peak also factors as a constant times a1 cos(kappa)+a2 sin(kappa), so the circular robust geometry is not limited to sampling in this example.

This is a deliberately simple synthetic input-output model. It does not assert that a measured grid parameter has this exact sine/cosine gain relation.

## Consequences for the claim ledger

- The new candidate lower bound concerns direct, non-lifted polyhedral representations of a fixed rotation model, on a fixed interior range of allocation slopes
- It is not a lower bound on arbitrary computation, conic certificates, lifted extended formulations, or IQC descriptions
- One cannot determine infinite Diophantine type from a finite-precision estimated modal angle
- A continuous uncertainty interval need not inherit the known-angle approximation class or its constants
- Parameter uncertainty remains part of the actual information contract, rather than something removed to obtain an attractive theorem
