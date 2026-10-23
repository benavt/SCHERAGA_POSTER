# Upstream Zenodo implementation notes

**Read [the current project runbook](../zenodo/README.md) and [distribution status](distribution-status.md) first.** This is historical upstream documentation, not authorization to execute its production or publish examples. Both production dataset records have since been published manually; Adk v1 requires correction. Completed runtime configurations and packages are private. The examples below describe initial deposition preparation and do not implement recovery of a published record through a new version. Creating new tags/releases requires a separate explicit yes.

Use `python3 tools/zenodo_deposition.py --help` from a source checkout. The
command requires only Python 3.11+, Git and, for actual uploading, an authenticated
`gh` CLI. It packages explicitly selected existing data and source from a release
tag. It never generates models, reruns analyses, creates tags/releases, or publishes
from a Git event. The default remote environment is Zenodo Sandbox.

## Set up a deposition

Tracked files under `zenodo/configs/` preserve earlier owner-review configurations. They are not the final private runtime configurations. Read the project runbook and verify the configuration and package selected for any future operation.


The project creator profile is [zenodo/creators.json](../zenodo/creators.json). Author order is T.L. Benavides, then G.T. Montelione, with the supplied ORCIDs and departmental affiliations. Metadata changes must be reviewed; do not fabricate config metadata.

Set these values deliberately:

| Field | Meaning |
| --- | --- |
| `branch`, `tag` | Existing local branch and release tag. The exact tagged commit must belong to the branch. A later branch tip is allowed; source is always taken from the tag. |
| `data_provenance` | Immutable input/run IDs, generation evidence, engine/settings identities, acceptance/exclusion criteria, and the connection between inputs and outputs. A release date or file mtime does not establish model generation date. |
| `title`, `description`, `keywords` | Scientific question, target/construct, cohort counts, methods, limitations and reuse instructions. File navigation and release provenance are appended automatically to the Zenodo description. |
| `publication_date` | Explicit `YYYY-MM-DD` date. |
| `access_right`, `license` | Actual access decision and a Zenodo license identifier, after checking rights for all files. There is no assumed data license. The software LICENSE stays with the software. |
| `creators`, `contributors` | Authors and other contributions. Contributor roles use Zenodo's controlled vocabulary. |
| `communities`, `grants`, `related_identifiers`, `references` | Supply applicable community identifiers, funder/grant IDs, paper/data DOIs, relations and references. Leave inapplicable lists empty rather than inventing values. |
| `assets` | Exact relative paths under the selected `--data-root`, a unique portable archive name, role (`inputs`, `outputs`, `reports`, `provenance`) and a useful description. Directories include all descendants. No implicit whole-branch data sweep. |

Use the [official metadata specification](https://developers.zenodo.org/#deposit-metadata)
for controlled vocabulary and optional scientific metadata. Zenodo validates
server-side vocabulary, license/community IDs and grants when saving the draft;
the local validator checks required project fields, identities and package integrity.
For restricted access, supply `access_conditions`; for embargoed access, supply
`embargo_date`. A valid dataset license is required explicitly even for a closed
package so the package README documents intended reuse conditions.

## Prepare and review offline

Resolve the data location from the scientific run's existing records. It can be
outside this source worktree. Data stay in their canonical location; a branch
stores source/configuration and a selected hash inventory, not duplicate raw data
or a new exception to the Git artifact guard. Existing source/index changes and
vendor patches are preserved and excluded from the tagged source archive.

```bash
python3 tools/zenodo_deposition.py plan \
  --config local/zenodo/deposition.json --data-root /absolute/canonical/project

# Before bulk packaging, use the registered repository's storage preflight.
# Required bytes should cover the plan's uncompressed data plus source/overhead.
python3 scripts/workspace.py storage preflight --required-bytes 123456789

python3 tools/zenodo_deposition.py prepare \
  --config local/zenodo/deposition.json --data-root /absolute/canonical/project \
  --out outputs/zenodo/my-release/package
python3 tools/zenodo_deposition.py verify --package outputs/zenodo/my-release/package
```

The plan hashes the complete explicit selection. `prepare` requires a new output
directory and enough capacity for uncompressed selected data plus an additional
reserve. The storage contract preflight remains required for bulk intake. Scientific
sources are never moved, retired or rewritten. Symlinks, path traversal, overlapping
selections, credential-shaped paths and changing files stop packaging. Review file
contents for private information too; a filename guard cannot recognize every secret.

The package contains:

- `README.md` and `index.html`: landing pages and navigable downloads/file inventory.
- `inputs.tar.gz`, `outputs.tar.gz`, and optional reports/provenance archives:
  stable folder names, original bytes, deterministic timestamps, and descriptions.
- `source.tar.gz`: an allowlisted source snapshot from the exact release commit.
  Historical tracked data and uncommitted files do not enter this archive. Submodules
  are referenced by their pinned commits in `manifest.json`, not silently vendored.
- `files.tsv` and `manifest.json`: each selected file's path, size and SHA-256,
  the branch/tag/commit, submodule pins, metadata, and scientific provenance.
- `zenodo-metadata.json`, `CITATION.cff`, `citation.csl.json`, `CITATION.txt`:
  deposit metadata and portable citations. A draft's reserved version DOI is inserted
  into the three citation files before they are uploaded.
- `package.json`: a seal over every upload file, with SHA-256 and Zenodo-compatible
  MD5 checksums. Uploads obey the standard 100-file / 50 GB record limit.

The package seal changes once when a reserved DOI is inserted. Use the final seal
from the draft receipt for publication review. The DOI is not registered/resolvable
until publication; cite that exact version DOI in work using this specific dataset.

## Save a draft

First create and publish a GitHub release for the reviewed dataset branch/tag,
under a separately approved release scope. `draft --apply` verifies the remote
tag resolves to the frozen commit and that a published GitHub release exists.
Native GitHub–Zenodo integration archives software releases; this command instead
creates an explicit dataset deposit containing the chosen input/output data and
links it to the source release. Avoid enabling a second automatic upload of this
same dataset through another release action.

Load a token on the machine performing the upload. Tokens must remain in an ignored private environment, outside this project or any data package. Sandbox
and production use separate accounts/tokens. The token needs `deposit:write`;
publishing also needs `deposit:actions`.

```bash
# Preview: no token or network requests.
python3 tools/zenodo_deposition.py draft \
  --package outputs/zenodo/my-release/package \
  --receipt local/zenodo/my-release.sandbox.json

# Set ZENODO_SANDBOX_TOKEN privately in your shell, then explicitly upload.
python3 tools/zenodo_deposition.py draft --apply --environment sandbox \
  --package outputs/zenodo/my-release/package \
  --receipt local/zenodo/my-release.sandbox.json
```

Production drafts use the separate project wrapper and reviewed operation scope described in the current runbook. Publication remains manual. Do not invoke the upstream publish subcommand.

Rerun the exact `draft --apply` command to resume. Completed remote files are
skipped only when size and checksum match. Conflicting or unexpected remote files
are preserved and stop the upload. No DELETE operation or automatic overwrite is
performed. If draft creation timed out before its ID was recorded, inspect Zenodo
and pass `--resume-id ID` for the reconciled draft; the program does not blindly
create another deposition. A pending local DOI citation update is recoverable from
its receipt. Preserve the package and receipt together during recovery.

This initial implementation creates a new record and resumes an existing editable
draft. It does not automatically call Zenodo's new-version action, replace inherited
files, alter a published record, or select a concept DOI. Later releases can link
prior datasets through `related_identifiers`; retaining a single versioned Zenodo
concept needs a separately reviewed new-version workflow.

## Publication is not authorized

The upstream tool contains a publish implementation, but this project has no approval to invoke it. The owner published the existing production records manually. Future draft operations and new-version recovery require their concrete reviewed scope; publication remains with the owner.
