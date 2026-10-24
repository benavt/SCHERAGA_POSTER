# Contributing

This repository accompanies a public conference poster. Contributions should help researchers, students and readers without a technical background find, understand and reuse the work.

## Writing and organization

- Use clear, audience-appropriate descriptions. Define technical terms when first introduced and link to detailed methods where helpful.
- Put study explanations in `docs/`, poster downloads in `poster/`, and dataset availability in `data/`. Keep the main README focused on the study and navigation.
- Keep personal workspace details, machine addresses, credentials and session transcripts outside the repository. Use relative paths and environment variables in examples.
- Preserve author attribution, citations, license notices, scientific caveats and the distinction between available and planned resources.

## Scientific changes

For a correction, identify the affected result and its supporting source or calculation. Distinguish original predictions, matched refolds and experimental reference structures. Confidence scores, coordinate similarity and experimental state populations must remain clearly distinguished.

Final poster exports and dataset inventories carry checksums. Publish revised artifacts with a distinct version and an updated manifest rather than replacing an existing version silently. Data publication procedures are documented in [the deposition guide](zenodo/README.md).

## Local checks

The repository checks use Python 3 and its standard library:

```bash
python3 -m unittest discover -s tests
python3 tools/check_privacy.py --tracked --working-tree
```

The privacy checker is self-contained. It checks tracked working files for credential patterns, local filesystem paths, network addresses and disallowed artifact paths. It also checks for exact credentials from known local Zenodo credential files, when present, without printing their values. Automated checks supplement review of documents, images and packaged data.

To check the Git index before a commit:

```bash
python3 tools/check_privacy.py
```

An optional pre-commit hook runs the tracked-index check:

```bash
git config core.hooksPath .githooks
```

Bulk scientific outputs and local upload receipts belong in ignored directories or separately versioned data releases. Keep pull requests focused and describe the change, its purpose and the checks performed.
