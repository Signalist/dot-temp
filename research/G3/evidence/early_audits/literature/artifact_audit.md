# Recovery status: recovered_text

Recovered on 2026-10-02 from this worker's retained 2026-10-01 file-writing tool call. The text below describes the original October 1 audit; no downloads or source revalidation were repeated. The files, archives and extracted directories it mentions have NOT been recovered. The three recovered literature text files are the only restored deliverables from this worker. paper_ready=false remains in force.

# Reproducibility and source access audit

Completed 2026-10-01. Downloading and inspecting files is not independent reproduction of the reported results.

## Jaramillo et al.

- Publisher article and supplement both retrieved successfully
- The supplement is a ZIP containing CSV outputs, configuration snapshots, controller specification, binary MATLAB stage caches, a run manifest and external-validation input/template files
- No MATLAB source code is included. No downloaded code was executed
- The inspected manifest marks external EMT/HIL validation incomplete
- The archive can support auditing of reported outputs and reconstruction from the written model, but it is not a ready-to-run released simulator
- Its configuration is a finite 7 s event study, with constant base dispatch, post-fault support boost and repeated-fault parameters. No exogenous periodic-load generator is specified in the inspected configuration
- Source article Table 4 says 15/31 global/fallback scan points, whereas configuration_snapshot.csv records 17/41. This is a reproducibility discrepancy to resolve before exact numerical replication, not grounds to dismiss the prior contribution
- Metadata, SHA256 and archive inventory are in source_artifact_inventory.json
- Selected non-executable evidence documents are extracted to Jaramillo2026_supplement_inspected/

Primary links: https://www.mdpi.com/1996-1073/19/18/4464 and https://www.mdpi.com/article/10.3390/en19184464/s1

## Shamseldein

Direct publisher and Elsevier content-API fetches returned small “Site Unavailable” pages. Their filenames explicitly say fetch_status; do not treat them as article text. Primary publisher sections were nonetheless available in search-indexed full-text passages. This audit inspected the architecture, impedance screen, QP formulation/priority structure, combined scenario, weight sensitivity, conclusions and data-availability statement there.

Crossref JSON was retrieved and saved. It identifies the author and DOI and a January 2027 print issue; it has no published-online field. Its created timestamp is 2026-06-29T19:24:47Z. A DOI-registration timestamp must not be presented as first online publication.

No public code repository was verified. “Will be made available” and “on request” do not establish a runnable public artifact. The primary text is sufficient to establish the combined-forcing/QP collision; this audit cannot independently reproduce its performance numbers.

Primary links: https://www.sciencedirect.com/science/article/abs/pii/S0378779626008503 and https://api.crossref.org/works/10.1016/j.epsr.2026.113557

## General

The novelty report deliberately does not infer actual field performance, certification/compliance, or acceptance likelihood. It treats published performance as author-reported evidence and prospective distinguishing mechanisms as hypotheses. Missing code or limited validation narrows confidence in numerical reproduction; it does not make an already published conceptual contribution new again.
