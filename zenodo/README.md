# Zenodo preparation and draft-upload runbook

Two resource records have been published manually by the owner: [Adk](https://doi.org/10.5281/zenodo.23601146) and [Mad2](https://doi.org/10.5281/zenodo.23601144). Current collections contain 11,000 native AIS models per target (1,000 from each of 11 methods), matched refolds, score tables and provenance.

**Current recovery status, checked 2026-10-23:** Mad2 v1 has all 14 expected files. Adk v1 has 9 of 14; its model-output archive and four other files are missing after an upload failure. Both complete packages are preserved locally and passed fresh seal checks. See [distribution status](../docs/distribution-status.md) for the missing files and finalization plan. Preserve the two existing concept DOIs.

**Next metadata work:** resume the [metadata rework plan](metadata-rework-plan.md) to revise field handling, titles and especially the scientific descriptions. Title and description changes are supported both for existing records and future versions; metadata-only edits do not change the DOI. This plan is saved for later and performs no remote operation.

The remaining sections describe the original preparation and draft-upload workflow. Their missing-config and missing-release gates describe the earlier preparation stage: the source release now exists, and the completed runtime configs/packages are private. The tracked configs remain historical review templates, not the upload-ready configurations. New-version recovery is not implemented by these wrappers; do not resume a published record as an editable draft. Publication remains manual; this runbook authorizes no publication or unreviewed upload.

## Stop conditions and review order

1. **Owner review is required before execution.** The owner has authorized reuse of the two earlier draft configs in `zenodo/configs/`. Unresolved placeholders and asset locations still stop offline validation: do not invent titles, descriptions, grants, dataset dates, visibility, relationships, asset selections or DOI values. The verified recurring creator profile is `creators.json`; review it together with the user config.
2. Read [the complete upstream implementation notes](../docs/zenodo-deposition.md) and `tools/zenodo_deposition.py` (upstream implementation) and `tools/zenodo_sandbox.py` (the project front door). The copied tool requires Python 3.11+, Git, and an authenticated `gh` CLI only for later approved remote-release verification. Its `plan`, `prepare`, `verify` and `draft` preview stages run offline.
3. The offline planner requires an **existing local branch and tag**, and `draft --apply` requires a matching **published GitHub release**. The existing source release is [`scheraga-poster-v1.0.0`](https://github.com/benavt/SCHERAGA_POSTER/releases/tag/scheraga-poster-v1.0.0), commit `27f2b5dd98732a9596652717165e36cd0b8e4115`. Do not change that frozen tag or create another release as a workaround for an upload gate.
4. After the user supplies and approves the config, review explicit relative asset paths under the selected data root, complete counts, per-file SHA-256, provenance, rights and required storage. Never sweep the whole private project, upload credentials, rerun science, or move source models. Package to a new ignored output directory.
5. Review the offline package and its exact seal. Only after explicit approval of the particular Sandbox upload may `draft --apply --environment sandbox` create or resume an editable draft. Set **only `ZENODO_SANDBOX_TOKEN`**, in an ignored private environment on the upload machine; never commit, log, transmit through chat, or place it in a data package. This runbook does not authorize production, a production token, or the `publish` subcommand.
6. Verify every uploaded file’s checksum, metadata, creator order and reserved Sandbox DOI, then stop for review. A reserved Sandbox DOI is not a production deposition or a published citation. Inspect any uncertain request outcome before retrying; do not blindly create a second record.

## Reference and model handling

Keep original AIS coordinates distinct from matched Boltz2 template-only refold coordinates and their pTM/pLDDT scores. Experimental controls (4AKE, 1AKE, 1DUJ and 1S2H) are explicitly labeled PDB references, excluded from AIS model totals and confidence rankings, and stored in a separate reference asset if included. Preserve original PDB IDs, chain/model selection, sequence/residue mappings, original bytes/hashes, source links and citations. The 1S2H R133A mutation and incomplete 1DUJ C-terminus remain documented. Do not silently trim or repair deposited originals. Record the shared 175-position Mad2 experimental mask separately from full 197-position original/refold scoring.

## Metadata the user must verify

Title; scientific description and limitations; target/construct; method/version counts; native physicality flags; input/output relationships; authors, ORCIDs and affiliations; publication date; rights/license; keywords; communities; funding identifiers; related publications/data/code; exact release identity; explicit assets and descriptions. Use [official Zenodo metadata fields](https://developers.zenodo.org/#deposit-metadata). This list is a review aid, not a filled configuration.

Code retains MIT licensing; authored content/data use CC BY 4.0 where the authors own the rights. Third-party material retains its own terms. See [licensing](../LICENSE-CONTENT.md).

## Commands after the missing-config gate is resolved

The following are command shapes, not instructions to execute now. They require a user-authored config, approved data selection, an existing reviewed release/tag and sufficient storage. The `USER_CONFIG` and other uppercase values are deliberately not filled.

```sh
# Offline plan; stop if the user has not supplied this config.
python3 tools/zenodo_sandbox.py plan --config USER_CONFIG --data-root DATA_ROOT
# Offline packaging after review; output must be a new ignored directory.
python3 tools/zenodo_sandbox.py prepare --config USER_CONFIG --data-root DATA_ROOT --out NEW_PACKAGE
python3 tools/zenodo_sandbox.py verify --package NEW_PACKAGE
# Offline draft preview: no network or token.
python3 tools/zenodo_sandbox.py draft --package NEW_PACKAGE --receipt PRIVATE_RECEIPT
# ONLY after explicit approval of this exact Sandbox draft upload:
python3 tools/zenodo_sandbox.py draft --apply --environment sandbox --package NEW_PACKAGE --receipt PRIVATE_RECEIPT
```

Use the Sandbox wrapper for Sandbox work and the separate production-draft wrapper only for approved production drafts. Do not invoke `publish` or create missing Git tags/releases. If a prerequisite is missing, stop and explain it to the user.


## Production drafts only — separately authorized scope

The user selected **production drafts only, without publication**. Use the separate `tools/zenodo_production_draft.py` front door; preserve the Sandbox wrapper for Sandbox work. This authorization does not resolve missing/placeholder user-config fields (including date and tag), the reviewed main/release location, or canonical data-root confirmation. Stop offline while those prerequisites remain unresolved. The user-supplied configs must not be completed by an agent without further instructions.

The production wrapper supports only `plan`, `prepare`, `verify` and `draft`. It defaults draft operations to production, rejects Sandbox credentials/environment, abbreviated flags and `publish`, and additionally blocks publication/all action endpoints in its HTTP client. Applied drafts require `ZENODO_ACCESS_TOKEN` in a protected private environment **before upstream work or networking**. Keep credentials in a protected private environment; never commit, print or package them. This wrapper preserves the upstream exact package, local branch/tag and matching published GitHub release checks; it does not create or bypass missing tags/releases. An explicit yes to a concrete release/tag plan remains necessary.

After all configuration, data-root, rights/privacy/storage and release prerequisites are approved, the command shapes are:

```sh
python3 tools/zenodo_production_draft.py plan --config USER_CONFIG --data-root CONFIRMED_DATA_ROOT
python3 tools/zenodo_production_draft.py prepare --config USER_CONFIG --data-root CONFIRMED_DATA_ROOT --out NEW_PACKAGE
python3 tools/zenodo_production_draft.py verify --package NEW_PACKAGE
python3 tools/zenodo_production_draft.py draft --package NEW_PACKAGE --receipt PRIVATE_RECEIPT
# Only with protected production credentials and approval of this exact draft upload:
python3 tools/zenodo_production_draft.py draft --apply --environment production --package NEW_PACKAGE --receipt PRIVATE_RECEIPT
```

These are prerequisite-dependent command shapes, not permission to run them now. Secure credential setup alone does not resolve config, release, data-root or exact-upload approval gates. Adding this wrapper executes no production request, packaging or tag/release action.

The upstream private receipt continues to store the reserved **version DOI**. A separate owner-only `PRIVATE_RECEIPT.concept-doi.json` sidecar captures an explicit authoritative response `conceptdoi`, separately from `metadata.prereserve_doi.doi`. It makes no additional HTTP requests. If no concept DOI is returned, status stays **unresolved**; record/concept IDs are never converted into a guessed DOI. Conflicting returned concept DOI/deposition identities stop the operation. This sidecar is private operational evidence, not a deposition config.

A concept DOI denotes all versions and resolves to the latest after registration on first publication. A reserved draft DOI is not yet a registered/resolvable published citation; Sandbox test DOIs are not production identifiers. The physical poster must not claim an authoritative production all-versions link until one is actually returned and its publication/resolution state is established. Production draft approval is **not publication approval**. The production wrapper provides no publish command.

## Exact manifest-backed assets

For the independently stored canonical models, the production wrapper supports explicit manifest-backed assets. Every selected asset must name a TSV `manifest`, its pinned `manifest_sha256`, and the existing role/name/description; mixed target tables require an explicit `dataset`. Manifest locators stay inside this repository's `zenodo` tree. Payload paths are portable logical-root keys with no absolute paths or traversal. `SCHERAGA_ASSET_ROOTS_FILE` points privately to a mode-0600 root dictionary; bindings are resolved only while reading and never serialized into packages. The adapter verifies membership, bytes, hashes, identities and archive members while streaming directly from canonical files. It never creates a second unpacked model tree.

The recovered configs remain review drafts until their date/tag and exact manifest selections are completed. Their earlier generic directory paths are not evidence that a matching data tree exists. No package or upload may silently fall back from manifest mode to those paths.
