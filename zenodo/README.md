# Zenodo preparation and draft-upload runbook

Two resource records are planned: one for all Adk resources and one for all Mad2 resources. Current collections contain 11,000 native AIS models per target (1,000 from each of 11 methods), their score tables and provenance. Publication is not authorized. The user has separately authorized production drafts only; use the distinct production front door and gates below. Sandbox testing remains a separate environment.

## Stop conditions and review order

1. **Owner review is required before execution.** The owner has authorized reuse of the two earlier draft configs in `zenodo/configs/`. Unresolved placeholders and asset locations still stop offline validation: do not invent titles, descriptions, grants, dataset dates, visibility, relationships, asset selections or DOI values. The verified recurring creator profile is `creators.json`; review it together with the user config.
2. Read [the complete upstream implementation notes](../docs/zenodo-deposition.md) and `tools/zenodo_deposition.py` (upstream implementation) and `tools/zenodo_sandbox.py` (the project front door). The copied tool requires Python 3.11+, Git, and an authenticated `gh` CLI only for later approved remote-release verification. Its `plan`, `prepare`, `verify` and `draft` preview stages run offline.
3. The offline planner requires an **existing local branch and tag**, and `draft --apply` requires a matching **published GitHub release**. No project release/tag has been authorized here. If one is missing, explain this gate and ask for the user’s explicit **yes** to a concrete release plan; do not create tags or publish a release as a workaround.
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
