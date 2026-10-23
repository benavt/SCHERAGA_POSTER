# Zenodo preparation and Sandbox-only runbook

Two resource records are planned: one for all Adk resources and one for all Mad2 resources. Current collections contain 11,000 native AIS models per target (1,000 from each of 11 methods), their score tables and provenance. Publication and production Zenodo requests are not authorized.

## Stop conditions and review order

1. **No configuration exists yet. Stop offline.** The user will write the metadata/asset config in `zenodo/configs/`. The empty folder is intentional: do not infer titles, descriptions, grants, dataset dates, visibility, relationships, asset selections or DOI values. The verified recurring creator profile is `creators.json`; review it together with the user config.
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

Use the Sandbox wrapper rather than the upstream production-capable entry point. Do not set production credentials, invoke `publish`, or create missing Git tags/releases. If a prerequisite is missing, stop and explain it to the user.
