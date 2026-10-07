# Independent CPU-only continuation-kit audit

Status: passed for a bounded CPU-only handoff review; no unresolved issue found in the reviewed scope. This is a bounded implementation review, not a formal security proof or an experimental result.

## Verified findings

- The pilot contains 18 author-written tasks, 9 structural families, and 6 tasks in each of development, calibration, and heldout. Families do not cross splits. Benchmark, reference, and per-task hashes match.
- Reference outputs are validator fixtures, not model outputs. The inference-request exporter includes prompts and metadata only, excluding test cases, expected answers, and reference fixtures. Heldout is public synthetic and is not an external contamination-proof benchmark.
- Historical rescoring retains 108 requests: 72 MAIN and 36 warmups. MAIN has only 3 distinct output hashes, each repeated 24 times. Writing and code fail explicit requirements; arithmetic is only a limited final-answer check, not certified overall quality.
- All 324 consumed legacy input files are bundled and SHA256-pinned. No legacy repository program or generated Python source was imported, evaluated, compiled, or run by Python; the new bounded AST interpreter supplies the limited checks.
- The comparison design fixes model/tokenizer identity, BF16, temperature 0, seed 17, natural EOS, concurrency 1, and disabled prefix caching. Native graph capture and actual replay must be shown, not inferred from a flag.
- Full episode costs include startup, compilation/capture, warmup, all scheduled tasks, failures, recovery, logging, and shutdown. Missingness and failed quality are retained. Twelve paired blocks are exploratory, not a precision guarantee; physical GPU reuse is reported.
- Continuation phases Q/O/R0/R are explicitly separate from original W6 branches A–E. No new GPU acquisition, hardware actuation, paid resources, network work, repository mutation, or push was performed for this audit. J_W6 remains null and original physical W6 remains incomplete.

## Defects identified and repaired during review

1. Sequence augmented multiplication could allocate before checking its bound
2. Nested/shared containers lacked an expanded-size/depth/cycle budget before host comparisons
3. Oversized ranges and deeply nested JSON could escape as uncaught exceptions
4. String modulo formatting could allocate using a huge format width before its bound
5. Comparison metadata referenced a nonexistent pool and did not map its real schema
6. Continuation phase names conflicted with the original branch labels
7. Legacy rescoring depended on outside files and did not pin every consumed metadata input
8. Record-level validation could be mistaken for model or complete-experiment evidence

Final independent tests: 12 test methods passed, including the 18 reference fixtures and 288 differential cases; 7 separately constructed adversarial probes failed closed. An additional sequence augmented-assignment semantic defect was repaired by accepting integer-only augmented assignment; the alias/purity regression now returns UNKNOWN_UNSUPPORTED. Typed EOS metadata validation also passed regression tests.

## Final verification and limits

- Final integer-only augmented-assignment regression passed
- Comparison pins the final validator hash 14066cae918a6af30486de406aabd0ec3add22ed80006e1276e9d8362254e439; source and manifest hashes all verify
- All 324 legacy and 17 index-input hashes verify; legacy bytes also match the original source. The proposed index overlay has a valid detached checksum and no self-reference; original files remain unchanged
- Record diagnostics do not establish scheduled-denominator completeness, provenance, human writing quality, actual graph treatment, hardware closure, or any measured quality/cost effect

Machine-readable progress and final verification are in AUDIT.json.
