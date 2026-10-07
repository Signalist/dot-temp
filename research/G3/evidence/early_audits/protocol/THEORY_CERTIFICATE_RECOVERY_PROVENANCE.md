# Theory/certificate text recovery provenance

Recovery date: 2026-10-02. Author: G3 theory/certificate worker. Scope: text restoration only at the time this record was written; no calculator or simulation executed in this recovery step.

## Source and recoverability

The original . tree is unavailable. The worker searched existing /workspace and /tmp paths read-only for the named G3 artifacts and archives; none was recovered. This restoration uses the worker's own earlier visible tool-call input text and numerical tool-result records, not prohibited session directories or hidden files. No original NPZ, raw log, checkpoint JSON, or original certificate JSON was recreated or fabricated.

The calculator text is reconstructed from the earlier complete heredoc and the recorded V2.1 transformation. This aims to reproduce the recorded source text, but byte identity against the vanished original files cannot be independently verified because their original source SHA256 values were not recorded. The new hashes identify the recovered text only.

## Files and changes

1. recovered_source/dc_bound_gate_a.py
   - Legacy calculator reconstructed from the complete original source-writing tool call
   - Includes the later recorded wording update excluding unmodeled brake/chopper/freewheel/shutdown channels
   - Retains the historical 0.20005 s diagnostic-state input convention and legacy filenames
   - Archival source text only; do not use this as the new V2.1 evidence calculator

2. recovered_source/recover_v2_1_from_legacy.py
   - Restores the previously recorded textual transformation into the V2.1 calculator
   - Its recovery wrapper paths were changed to recovered_source and the current root
   - Running this file during recovery only wrote source text; it did not import or execute either calculator

3. recovered_source/dc_bound_gate_a_v2_1.py
   - Generated from that reconstructed legacy text using the recorded V2.1 edits
   - Reads parameters and exact fault-onset state from trajectory/checkpoint evidence; it does not inject historical checkpoint numbers
   - Frozen conservative rounding thresholds remain assertions against the input state, not an assumed state

4. gate_a/dc_bound_gate_a_v2_1.py
   - New active adaptation of item 3
   - Adds an explicit --new-evidence execution guard
   - Writes protocol/DC_BOUND_GATE_A_V2_1_REVALIDATED.json rather than recreating an old certificate filename
   - Replaces historical fixed-time/result wording with wording tied to actual newly supplied evidence
   - Adds recovery provenance to any future calculated JSON
   - ROOT remains relative to the script and now resolves to the authorized recovery project
   - All numerical formulas, source/state readers, physical caps, rounding thresholds and selfchecks otherwise remain the reconstructed ones

5. protocol/THEORY_REVIEW_RECOVERED.md
   - A condensed, newly organized reconstruction of the prior theory review
   - Preserves the exact endpoint scalar bound and proof, efficiency/viability caveats, physical-energy lifting, periodic-orbit cautions, realistic scale checks, strong-MPC protocol and stop criteria
   - Not represented as a byte-for-byte recovered original

6. protocol/DC_CERTIFICATE_HISTORICAL_RECORD.md
   - A new explanatory historical record, not an old artifact or current certificate
   - Distinguishes latest V2.1 17.088204 ms / 20 ms 595.60651 J results from the legacy 17.035 ms state
   - Marks every remembered number and cross-audit report as historical and not revalidated
   - The standalone original V2.1 Markdown certificate was never completed before interruption

## Validation boundary

Only Python AST parsing and file hashing are permitted in this text-restoration step. The historical calculator's embedded numerical selfchecks are source code, not completed new checks. No old selfcheck log has been recreated.

The parent subsequently authorized minimal revalidation conditionally: wait for newly generated 10 us and 5 us trajectories/checkpoint files and the parent's completion notification, then run the active calculator with --new-evidence. Do not use partially written inputs, impute a checkpoint, alter the protocol, rerun the legacy state as the final result, or start Gate B. Newly calculated output, if later produced, must cite the fresh source hashes and remain distinct from the historical record.
