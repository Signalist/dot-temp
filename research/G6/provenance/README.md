# Public source provenance and rights boundary

The handoff includes original research scripts, mathematical reports, generated numerical results and compact benchmark-derived matrices/kernels. It does not include third-party paper PDFs, raw benchmark workbooks, proprietary sources, virtual environments, compiled binaries, private notes, credentials or delivery receipts.

## Upstream benchmark lineage

The compact network fixtures are generated from public ANDES v2.0.0 benchmark workbooks. The pinned official source is https://github.com/CURENT/andes/tree/v2.0.0/andes/cases and package page https://pypi.org/project/andes/2.0.0/ . The GPL text is preserved unmodified as ANDES_LICENSE_GPL3.txt; upstream license is https://github.com/CURENT/andes/blob/v2.0.0/LICENSE . UPSTREAM.json identifies relevant case paths, exact original workbook SHA256 values and the benchmark transformation. The original workbooks are not bundled. Their license/source URLs were checked on 2026-10-07.

Derived fixture lineage is documented by the original qualification/provenance reports and the SOURCE_TO_PUBLIC.json hashes. These are public benchmark-derived coefficients, not measured electrical grids or private compute workloads. The retained upstream license applies to its covered material; it is not an invented blanket license for every research file. No new license grant for original research code is assigned here. Any reuse license or additional third-party rights decision belongs to the rights holder/repository owner before redistribution beyond the approved publication.

## Download and verification recipe

Run from the handoff root, only when original upstream workbooks are needed:

```sh
python provenance/fetch_upstream_cases.py --directory ./upstream_cases
```

This optional script downloads exact versioned official GitHub raw URLs, verifies the recorded SHA256 before writing each workbook, refuses overwrites and saves outside evidence. It does not execute downloaded content, run ANDES, regenerate kernels or qualify nonlinear models. It is not invoked by any default replay. Alternatively install the official pinned package in a separately authorized environment with `python -m pip install andes==2.0.0` and verify the matching case files against UPSTREAM.json. No fresh package installation or original-workbook re-download was performed during this handoff.

## Scientific papers

LITERATURE.json records authors, titles, official/author URLs, inspected locations, reduction claims and source-access caveats from the scientific dossiers. It contains bibliographic/analysis metadata, not full-text PDFs or long extracts. Those historical reading levels are not a claim that every paper was newly re-read in this handoff. Follow each publisher's/author repository's terms for obtaining articles. Missing full text stays an open novelty limitation; no access control is bypassed.

## Integrity and modifications

SOURCE_TO_PUBLIC.json maps every retained archived file's source-relative path and original SHA256 to its public relative path, current SHA256 and bytes. Path redactions and replacement historical entry pages are marked; numerical source is otherwise preserved. MANIFEST.json at the handoff root is the current payload integrity authority. Old hashes embedded in scientific reports refer to old byte sequences and do not verify this reorganized handoff. OMISSIONS.json records omitted redundant packaging/history/visual files. Main README and REPRODUCE.md override historical entry commands requiring unavailable workspaces.

Checksums show consistency, not independent authorship, physical truth, originality or a legal opinion. No publishing, repository permission changes, licensing decisions, third-party uploads or new external commitments were made by the package preparer.
