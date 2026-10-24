# Dataset package and command reference

This technical guide describes the deposition tools included with the poster companion. They require Python 3.11+, Git and an authenticated GitHub CLI (`gh`) for remote release verification. For public downloads, use the [dataset guide](../data/README.md). Check [resource availability](distribution-status.md) before working on an existing record.

## Prepare a configuration

The [historical templates](../zenodo/configs/README.md) show the configuration structure but contain unresolved fields. Make a separate configuration with verified scientific metadata and explicit asset selections.

| Field | Required information |
| --- | --- |
| `branch`, `tag`, `data_provenance` | Existing source branch/tag and the scientific provenance of the selected data |
| `metadata.title`, `metadata.description` | Protein, study purpose, actual file coverage, methods and reuse limitations |
| `metadata.publication_date` | Explicit publication date in `YYYY-MM-DD` format |
| `metadata.access_right`, `metadata.license` | Reviewed access and license values consistent with all included material |
| `creator_profile`, `metadata.creators`, `metadata.contributors` | Verified author order, identifiers, affiliations and applicable roles |
| `metadata.communities`, `metadata.grants`, `metadata.related_identifiers`, `metadata.references` | Supported identifiers and relationships; leave inapplicable lists empty |
| `assets` | Explicit relative paths, unique portable archive names, roles and descriptions |

Preserve separate rights notices for third-party material, experimental references and AlphaFold 3 outputs. Do not infer study dates from file modification times or treat an inventory as a redistribution license. The planner currently couples the dataset version to the source tag; account for that behavior when preparing a configuration.

## Offline commands

Run these from the repository root, replacing uppercase placeholders with the selected paths. No token is required for offline commands.

```bash
python3 tools/zenodo_sandbox.py plan --config CONFIG_JSON --data-root DATA_ROOT
python3 tools/zenodo_sandbox.py prepare --config CONFIG_JSON --data-root DATA_ROOT --out NEW_PACKAGE
python3 tools/zenodo_sandbox.py verify --package NEW_PACKAGE
```

`prepare` needs a new output directory and adequate free storage. It hashes explicit selections without moving the scientific sources. Symlinks, path traversal, overlapping selections, credential-shaped paths and changing files stop packaging. Review file contents and rights as well as filenames.

The production wrapper supports the same offline commands and additionally provides manifest-backed asset selection described in the [deposition guide](../zenodo/README.md).

## Package contents

- `README.md` and `index.html`: resource descriptions and file navigation.
- `inputs.tar.gz`, `outputs.tar.gz` and optional report/provenance archives: selected files with stable paths and deterministic timestamps.
- `source.tar.gz`: an allowlisted source snapshot at the pinned release commit.
- `files.tsv` and `manifest.json`: selected file paths, sizes, hashes and source provenance.
- `zenodo-metadata.json`, `CITATION.cff`, `citation.csl.json` and `CITATION.txt`: metadata and portable citations.
- `package.json`: checksums for each upload file.

When a draft reserves a version DOI, citation files and the package seal are updated together. Keep the final package seal with the upload receipt.

## Draft previews and uploads

The following command previews the draft operation without writing remotely:

```bash
python3 tools/zenodo_sandbox.py draft --package NEW_PACKAGE --receipt local/zenodo/draft.json
```

A reviewed Sandbox upload uses `--apply --environment sandbox` and `ZENODO_SANDBOX_TOKEN`. The production wrapper uses `--apply --environment production` and `ZENODO_ACCESS_TOKEN`. Supply tokens through a protected environment; never commit them or include them in a package. The Sandbox wrapper rejects production credentials.

Applied drafts verify the exact source release and require a matching published GitHub release. Review the target, complete metadata, file selection, rights, checksums and remote operation before an upload. Neither wrapper publishes a record.

## Recovery and limitations

Completed draft files are skipped only when size and checksum match. Conflicting or unexpected remote files stop the upload. If draft creation has an uncertain outcome, inspect the account and reconcile the draft ID before retrying; do not create another deposit blindly. Preserve the package and receipt together.

These tools do not implement editing published records or creating a new version within an existing DOI family. The [completed Adk correction](https://doi.org/10.5281/zenodo.23607500) used a new version rather than resuming the original v1 upload. The [metadata roadmap](../zenodo/metadata-rework-plan.md) distinguishes that completed correction from proposed tooling changes; it does not establish additional wrapper capabilities.
