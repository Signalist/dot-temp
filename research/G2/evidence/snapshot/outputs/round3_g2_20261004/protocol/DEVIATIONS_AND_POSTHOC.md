# Deviations, failures, and post-hoc work

- The nine frozen matched-support cases and all frozen baseline sizes ran unchanged. All primary numerical checks in the experimental script passed.
- The independent physical-convolution audit initially used a second-order finite difference with step 1e-5 to verify F''=q. That diagnostic failed its 1e-7 threshold because subtractive cancellation amplified rounding. The failed log is preserved as `audit/matched_support_qa_attempt1.log`. It was replaced with a fourth-order five-point stencil at step 2e-4; maximum error was then below 2e-9. Physical convolution, work moments, and the experiment itself were not altered.
- The epsilon=.0025 cases unexpectedly already had two-switch LINEARIZED optimizers for N=2,8,32. This observation is post-hoc, not a general nonlinear theorem. The exact nonlinear sign-coherent theorem is used only for epsilon>=A/2, including the frozen .01 case.
- Finite-jerk and finite-bandwidth results are analytic development; their numerical confirmations are separately frozen before execution. They do not retroactively change the old acceleration-arc class.
