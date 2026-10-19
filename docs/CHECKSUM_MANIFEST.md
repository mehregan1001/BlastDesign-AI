# Checksum manifest policy

`CHECKSUMS.sha256` records the SHA-256 of the contents staged in Git for the selected reproducibility-critical files. SHA-256 is calculated on the file's stored blob bytes, without Git's object header. The manifest does not hash itself.

This policy replaces hashing arbitrary files found in a local working directory. The earlier method could include ignored research outputs available on only one computer and could produce different hashes after Git converted LF and CRLF line endings.

## Coverage

The inventory consists of staged, regular files matching the root-file list and patterns in `scripts/generate_checksums.py`. Those patterns cover the selected source code, tests, notebooks, documentation, processed CSV/JSON artifacts, workflows, packaging files, and source materials when they are version controlled. `.gitattributes` is included if present and tracked.

Ignored local artifacts are excluded and reported. Nonignored new files matching the inventory must be reviewed and staged before generation. Missing tracked inputs and unstaged edits to selected inputs cause failure before the manifest is replaced.

The current patterns do not cover every repository file. For example, generated figure PNG files are outside these patterns. A manifest check therefore certifies this inventory, not all files, the scientific accuracy of the models, or independently reproduced research results.

## Normal workflow

Run the scientific and software checks appropriate to the change. Review `git status --short`, then stage the intended input files using explicit paths:

```text
git add PATH_TO_CHANGED_INPUT PATH_TO_ANOTHER_CHANGED_INPUT
python scripts/generate_checksums.py
git add CHECKSUMS.sha256
python scripts/generate_checksums.py --check
git diff --cached --check
```

The first line is a template: replace its example paths with the actual files being committed. Review the staged diff before committing.

`--check` verifies the staged manifest against staged inputs and also rejects unstaged edits to the selected inputs or manifest. It does not regenerate the manifest to make a failure disappear. After changing an input again, stage that change and repeat generation and checking.

Use `python scripts/generate_checksums.py --dry-run` after staging to inspect the inventory without writing the manifest. The command requires a Git checkout and Git itself; it also looks for standard Git for Windows and GitHub Desktop installations if Git is absent from PATH.

## Line endings and binary files

Git may present a tracked text file with different line endings on different machines. Hashing the same staged blob yields the same digest regardless of that presentation. Stored CRLF bytes are retained if they are actually part of the Git blob; the script does not universally rewrite text to LF.

Binary files are hashed from their complete stored bytes. The script does not perform decoding, newline substitution, or text-mode reads on their payloads. LFS pointer files are rejected because the referenced external data needs a separate checksum policy. Selected symbolic links, submodules, and unresolved merge entries are also rejected.

The manifest is primarily a Git snapshot record. A Git source archive supplies stored blob contents, but any archive export transformations need separate review. A Windows working-directory copy cannot necessarily be checked by an ordinary raw-file checksum utility because Git may have converted its line endings. Use the project's `--check` command inside the checkout. Standalone archive-verification tooling is outside this change.

## Migration from the v1.0.0 manifest

The published v1.0.0 record remains immutable. Regenerating the manifest under this policy can change hashes and remove entries which were never version controlled. The command reports those exclusions by comparing the inventory with the manifest in `HEAD` and by listing eligible ignored local files.

The initial cross-computer review identified these four entries from the earlier manifest which were absent from the second computer's regenerated inventory:

- `data/processed/burden_decision_readiness_step_24_20.csv`
- `data/processed/burden_evidence_tiers_step_24_17.csv`
- `data/processed/burden_screening_scenarios_step_24_17.csv`
- `data/processed/burden_structural_uncertainty_step_24_18.csv`

Git reported no tracked `data/processed/burden_*.csv` files on that branch. Those artifacts must be recovered from retained originals or reproduced from their generating code and reviewed before being added to the archival inventory. Exclusion from the new manifest neither recovers them nor establishes that they are scientifically unnecessary. The generator does not delete local artifacts or change `.gitignore` rules.

The project should separately decide which historical research outputs to retain under version control. A checksum entry alone does not publish or back up a file.

<!-- BEGIN LEGACY CSV RECOVERY STATUS -->
## Legacy CSV archive recovery

The four missing CSVs listed above were reconstructed from reviewed code in
`notebooks/02_blastdesign_model_audit.ipynb`. Each reconstructed file matches its
original v1.0.0 SHA-256 exactly. The six surviving local CSVs were retained after
the same original-manifest check. See [Legacy research-output archive](LEGACY_OUTPUT_ARCHIVE.md)
for the ten-file inventory, reconstruction method, and interpretation limits.

These ten historical CSVs have explicit `.gitignore` exceptions and path-specific
`.gitattributes` rules preserving their original stored bytes, including CRLF.
`scripts/recover_legacy_csvs.py --check-staged` verifies the staged copies against
the original hashes. They enter the current manifest after being staged and after
normal checksum generation. The published v1.0.0 tag and manifest stay unchanged.
<!-- END LEGACY CSV RECOVERY STATUS -->

## Implementation references

- [Git index inventory and stage records](https://git-scm.com/docs/git-ls-files)
- [Reading stored Git object contents](https://git-scm.com/docs/git-cat-file)
- [Git text conversion and attributes](https://git-scm.com/docs/gitattributes)
