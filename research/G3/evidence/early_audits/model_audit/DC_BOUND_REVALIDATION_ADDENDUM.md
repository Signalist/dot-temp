# Independent bound revalidation, 2026-10-02

Status: reconstructed_then_rerun. The independent abc source and first-converged-checkpoint source were recovered byte-identically against their original printed SHA256 hashes, then only the authorized nominal and V2.1 cases were rerun at10/5µs. The old raw files were not retrieved. New files exist under `abc_reference/revalidation_results/`.

Both resolutions independently select the first qualifying checkpoint at0.600000s under the frozen V2.1 rule; the dip begins at0.600050s. The fine run gives actual-current peak1.00007464987327pu and DC upper-bound event0.605945969798161s. The0.007465% current excess is a small numerical model witness, not equipment validation. The initial S-limit violation is retained, and no safe-startup claim is made.

`DC_BOUND_ABC_REVALIDATED.json` recomputes the independent energy inequality from the NEW5µs abc fault-onset state. Its SHA256 is c242ab76e1b99f7b23e64f9c6c1292df2e2b7ade090eabcd66ec7d13da940157. The input NPZ SHA256 is9b19745f35669ae33ba4145c9d8ad38b6772e08ab35808dc54c363299716cd56.

- DC energy21915.13519323016J; source power815639.6755409637W; inductor energy276.71216930672244J
- Maximum DC-plus-inductor remaining headroom4341.250139483163J
- Optimistic mandatory energy increase by20ms4936.856650060683J
- Contradiction margin595.6065105775197J; relaxed first equality17.08820393246425ms after fault

The factor/sign/loss/headroom/ramp analysis in the text-recovered `DC_BOUND_INDEPENDENT_REVIEW.md` remains valid. In particular, peak-dq inductor energy uses3/4 L|i|²; copper loss uses3/2 R|i|²; remote-source export is bounded by retained-voltage times three-phase Sbase; the fastest source-ramp lower envelope is sign-correct through reversal; and maximum inductor storage is granted. No brake/chopper/disconnection or additional energy sink is modeled. The conclusion is only joint current/DC infeasibility for this specified model, source event and physical state, not an exact hardware failure time.

The new public motulator0.7.8 LFilter/PCC and capacitive-converter algebra checks passed at eight fixed points. This supports the circuit-equation implementation, not the synthetic source/controller calibration. Independent abc-versus-dq fresh checkpoint and peak comparisons also pass; see `abc_reference/revalidation_results/ABC_DQ_REVALIDATION_COMPARISON.json`.
