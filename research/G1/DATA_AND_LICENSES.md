# Data provenance, download routes and rights

## Included evidence

The source is the research-generated compact archive `G1_evidence_20261004.zip`. Its SHA-256 and each file's original/public hashes are in `SOURCE_PROVENANCE.json`. Results date from 2026-10-04; this public copy dates from 2026-10-07. It contains synthetic normalized load/controller data, generated numerical certificates, canonical network replay inputs, research scripts and representative simulation outputs. These are not proprietary operational traces, measurements from a data center, or private user records.

The archive is incomplete for full nonlinear regeneration by design: `evidence/PACKAGE_SCOPE.json` lists 41 omitted raw arrays and historical simulator/source dependencies, with their exact byte sizes and SHA-256. The omitted original arrays cannot be downloaded from an invented public URL. Recover them from a lawful original archive or regenerate in a separately qualified environment and report numerical rather than byte equivalence.

## ANDES / Kundur

Public upstream: https://github.com/CURENT/andes

Official documentation: https://docs.andes.app/en/stable/

Upstream license: https://github.com/CURENT/andes/blob/master/LICENSE

The qualified upstream release is ANDES 2.0.0, using the official `kundur/kundur_full.xlsx`. The retained `evidence/outputs/round2_20261003/grid_transfer/ANDES_LICENSE_GPL3.txt` carries the GNU GPLv3 terms. Upstream license and current stable documentation were checked on 2026-10-07. No statement here relicenses third-party software. Preserve its license, attribution and applicable source obligations when redistributing or extending any derived component.

The compact archive includes the previously qualified `kundur_reduced51.npz` plus adapter/replay sources and original provenance lock. This is a generated model representation, not measured data. Exact expected input/source hashes are retained in `evidence/outputs/round3_g1_20261004/network_transfer/EXECUTION_ENVIRONMENT_LOCK.json` and `evidence/outputs/round2_20261003/grid_transfer/`. Obtain the official release using its supported package/repository distribution, check the declared source/case hashes, and rebuild in a fresh environment. Do not treat a newer public release as hash-equivalent.

## Literature

Only research-authored comparison/analysis and bibliographic links are included. Third-party paper full texts are not bundled. The closest-source reading level, including inaccessible full texts, is recorded in `theory_audit/FOCUSED_PRIMARY_PRIOR_MAP.md`. Citation accessibility does not establish redistribution permission.

## Research-code license

No explicit blanket outbound license for all original research code was present in the recovered archive. Publication is owner-authorized, but this handoff does not invent an MIT/BSD or other new license grant. Apply only an actual applicable repository license and retained file-specific notices; ask the owner to choose a research-code license if reuse terms are needed. GPL-covered third-party components retain their own conditions regardless of a repository-wide license.

## Check the release

`python3 evidence/verify_package.py` verifies the public evidence package. The route-level `PUBLIC_MANIFEST.json` covers all final public files. Historical scientific manifests may include hashes of original files that were path-sanitized; they remain provenance, not the authoritative public-copy integrity manifest. Scientific numerical arrays and canonical CSV bytes were not altered.
