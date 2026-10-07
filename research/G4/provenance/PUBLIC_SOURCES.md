# Public sources and acquisition

The latest literature ledger is retained under evidence/round3. `PUBLIC_SOURCES.json` gives primary URLs, inspection limits and available hashes. Third-party paper full texts are intentionally absent. Missing hashes are stated as missing, not guessed. Source versions can change; a mismatch must be investigated before using a new document for a prior-art claim.

To download one permitted public source into a new directory outside this handoff:

```sh
python3 tools/fetch_source.py --id SOURCE_ID --output ../sources/SOURCE_ID.pdf
```

For records without a frozen hash, add `--allow-unpinned` only after deciding that an unpinned current version is appropriate; the tool prints a new SHA-256 and does not claim historical identity. Use the correct extension for HTML or wheels. Fetching literature is optional and not needed for the principal frozen scientific replay. Failed access is a research limitation, not authorization to bypass access controls. No download was performed by this handoff's tests.

Dependencies: install pinned requirements from the official package registry in a new virtual environment, then record resolved package versions. Python environments, wheels, compilers and third-party runtime source are not bundled. Package managers should verify their own transport/integrity; this handoff is not an offline lockfile with all wheel hashes.

`SOURCE_TO_PUBLIC.json` maps every recovered included artifact's original SHA-256 to its sanitized public SHA-256. `EXCLUDED_FILES.json` records intentional omissions and original hashes. Root `PUBLIC_MANIFEST.json` is the current included-file inventory; nested historical manifests remain historical even if they name omitted artifacts.
