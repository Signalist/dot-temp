# Secondary window-shape ablation (explicitly post-primary)

This additional comparison was selected after inspecting the frozen primary L=8 outcomes. It is exploratory/analytical evidence, not a held-out or predeclared confirmation. Only the equal ray (0.5,0.5) is added, with (L,B)=(4,1), compared against the existing (8,2). No L=16 sweep was undertaken.

Both contracts have B/L=1/4, but the four-block contract forbids two nearby mismatches that the eight-block contract permits. Every eight-block window is two disjoint four-block windows, so K(4,1) is a subset of K(8,2); the difference tests local burst shape rather than asymptotic rate. Each envelope retains 256 past blocks, 2048 phase intervals and the inherited full continuous-phase/tail error.

| Source | (4,1) bracket MW | (8,2) bracket MW | Bracket-separated window-shape gain |
|---|---:|---:|---:|
| positive | 26.980117–27.036605 | 26.288363–26.341988 | 2.422% |
| wecc | 58.541994–58.721993 | 56.863310–57.033120 | 2.646% |

The same-information four-window LP independently checks each maximizing phase/output row, with direct-word discrepancies saved in SECONDARY_WINDOW_SHAPE.json. Raw complete phase supports are retained. Numerical uncertainty, physical/source scope, affine work assumptions, and old nonlinear/voltage limitations are exactly those in REPORT.md; no new nonlinear run was made. The primary protocol and primary result files are unchanged by this secondary calculation.
