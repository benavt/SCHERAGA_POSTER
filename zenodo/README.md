# Research datasets and deposition tools

The poster compares 11,000 original AI-sampled structures per protein, with matched Boltz2 refolds, confidence measurements and structural comparisons. Bulk data are distributed through two Zenodo records:

| Dataset | All-versions DOI | Availability checked 23 October 2026 |
| --- | --- | --- |
| Adenylate kinase (Adk) | [10.5281/zenodo.23601146](https://doi.org/10.5281/zenodo.23601146) | v1 incomplete: 9 of 14 expected files |
| Mad2 | [10.5281/zenodo.23601144](https://doi.org/10.5281/zenodo.23601144) | v1 complete: 14 of 14 expected files |

For downloads, limitations and citation guidance, start with the [dataset guide](../data/README.md) and [resource availability](../docs/distribution-status.md).

## Directory contents

- [`manifests/`](manifests/README.md): portable inventories of model, refold, confidence and reference files, with hashes.
- [`configs/`](configs/README.md): historical configuration templates, with unresolved fields.
- [`creators.json`](creators.json): creator names, identifiers and affiliations.
- [Metadata roadmap](metadata-rework-plan.md): proposed improvements to descriptions and archive organization.

The inventory and templates document provenance. They are not substitutes for the file list and rights information of a published dataset version.

## Tooling for maintainers

The Python tools use the standard library and support offline planning, package preparation and verification. The two entry points provide separate environments:

| Entry point | Scope |
| --- | --- |
| `tools/zenodo_sandbox.py` | Sandbox planning, preparation, verification and unpublished drafts |
| `tools/zenodo_production_draft.py` | Production planning, preparation, verification and unpublished drafts |

Both wrappers accept `plan`, `prepare`, `verify` and `draft`; neither exposes publication. Remote draft writes require `--apply`, the appropriate token and a reviewed configuration/package. Keep credentials and receipts in ignored storage, outside public packages. Publication is a separate manual step after review.

See the [package and command reference](../docs/zenodo-deposition.md) before preparing a deposit. The original `tools/zenodo_deposition.py` is the shared implementation; use the wrappers as the documented entry points.

## Existing records and versioning

These tools create and resume editable drafts. They do not implement the new-version operation needed to correct the published Adk record. Repeating an original draft-upload command cannot repair a published version. Preserve the existing version and use a reviewed new-version workflow within the same all-versions DOI.

A version DOI identifies a particular dataset release; a concept DOI identifies its version family. The production wrapper records a returned concept DOI separately from the reserved version DOI. It does not infer DOI strings from numeric record IDs. Sandbox identifiers are not production citations.

## Manifest-backed files

The production wrapper can select assets through a TSV `manifest`, its pinned `manifest_sha256`, a role/name/description and, for mixed-target tables, an explicit `dataset`. Manifest paths must remain inside this repository's `zenodo` tree.

`SCHERAGA_ASSET_ROOTS_FILE` selects an external mode-0600 JSON file whose `roots` object maps logical asset-root IDs to actual source directories. Local directory bindings are used only while reading and are not serialized into the package. The adapter checks membership, file identities, bytes, hashes and archive members without creating another unpacked model tree. See the [inventory guide](manifests/README.md) for role definitions.
