# W6 measurement audit deliverables

Decision: no source admitted for full W6 physical calibration. Continue conditional theory/model work; retain the real GPU/PCC validation gap.

Read MEASUREMENT_FEASIBILITY_REPORT.md for findings, SOURCE_COVERAGE_MATRIX.csv for field-by-field coverage, and protocol/MINIMAL_MEASUREMENT_PROTOCOL.md for the design-only acquisition and error budget. MEASUREMENT_STATUS.json is the machine-readable gate.

Actual read scope: both complete existing NLR raw inference power logs and DaRUS CSVs, Azure CSV, eight paired compact sensor records, actual NLR metadata/aggregate results, 13 SweetSpot representative traces and complete archive inventory, plus small new public repository/schema samples. No cross-source measured pairs were constructed. No fit, policy hardware evaluation or new holdout was run.

The workspace reset during the task. Completed tool observations survive in results/OBSERVED_SOURCE_FACTS.json; the missing raw data/new raw-audit manifests are explicitly listed. Hashes copied from prior manifests are labeled as such, not asserted to be newly recovered byte evidence. Do not claim a post-reset raw replay passed.

The reconstructed self-authored schema helper has five passing synthetic tests only:

    python code/read_only_schema_auditor.py

These tests validate parsers and the fail-closed admission gate, not the absent physical contract. build_audit_tables.py rebuilds the coverage and budget tables from declared observations; it is not a replacement raw-data audit.

The entire task is complete at the bounded feasibility-audit stopping condition. The prospective hardware protocol has never been executed and does not authorize hardware control or data transmission.
