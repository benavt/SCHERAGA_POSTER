# Dataset metadata roadmap

Proposed improvements to the Adk and Mad2 dataset descriptions, metadata and archive organization, as of 23 October 2026. These proposals have not yet been implemented. Final poster exports are available in [`poster/final/`](../poster/final/README.md).

## Current records and title changes

| Target | Current title | All versions | Current file status |
| --- | --- | --- | --- |
| Adk | Adk: all models and scores | [10.5281/zenodo.23601146](https://doi.org/10.5281/zenodo.23601146) | v1 has 9 of 14 expected upload files |
| Mad2 | Mad2: all models and scores | [10.5281/zenodo.23601144](https://doi.org/10.5281/zenodo.23601144) | v1 has all 14 expected upload files |

Titles and descriptions can be revised. A new-version draft has its own editable metadata and files, with a distinct version DOI linked to the same version family. Zenodo also permits editing an already published record's title and description without changing its DOI. A metadata-only wording change does not require a new version. See [Manage records](https://help.zenodo.org/docs/deposit/manage-records/) and [Manage versions](https://help.zenodo.org/docs/deposit/manage-versions/), checked 2026-10-23.

Keep both existing concept DOIs. Use a corrected Adk version for its missing files, with a revised title and description if desired. Decide separately whether Mad2 needs only metadata edits or a new file version. Metadata edits to one published version should not be assumed to update other versions; review each intended record explicitly.

## Proposed authoring approach

Keep the human-authored metadata separate from the bulk data package and local upload state. The present `plan()` in `tools/zenodo_deposition.py` appends release provenance and archive navigation directly to `description`; package preparation then reuses that combined text in its landing documents. This mixes the scientific narrative with operational detail and makes independent editorial changes awkward.

At implementation time, add a small reviewed metadata layer under `zenodo/metadata/` with the following responsibilities. Do not fill the historical `zenodo/configs/` templates in place or treat them as current runtime configs.

| Proposed source | Responsibility |
| --- | --- |
| Shared field policy | Consistent creator order, identifiers, terminology, rights handling and relation rules |
| Per-target metadata JSON | Title, resource type, dates, keywords, funding, related identifiers and target-specific field values |
| Per-target description Markdown | Readable scientific narrative edited directly by the authors |
| Generated metadata preview and diff | Exact rendered description and field-by-field changes against the live record |
| Version manifest and release notes | File hashes, archive navigation, source pins and what changed in that version |

The future adapter should render only the reviewed description into the Zenodo description field. Put detailed inventories and long provenance blocks in the package README/manifest, linked from a short download guide. Additional descriptions for methods or technical notes can be used if the chosen API supports them; otherwise retain that information in the linked README. Zenodo supports formatted descriptions and separate description types in its deposit form. See [Descriptions](https://help.zenodo.org/docs/deposit/describe-records/descriptions/).

## Proposed description structure

Write the description as a scientific resource abstract, followed by a brief reuse guide. Agree a shared outline, then author target-specific prose:

1. **Purpose and scientific scope.** State the conformational-sampling question and the relationship to the poster. Identify E. coli adenylate kinase or Mad2 monomer unambiguously; avoid historical construct names.
2. **Contents.** State 11,000 original AIS models, 1,000 per method across eleven methods, and 11,000 matched Boltz2 template-only refolds per target. Distinguish original coordinates, analysis copies, aliases and experimental controls. Describe only the files verified in the version being released.
3. **Methods and scores.** Summarize the method families and masking distinction, native physicality flags, confidence measurements and coordinate TM comparisons. Keep confidence, experimental-reference TM and original-versus-refold TM clearly distinct.
4. **Target and reference details.** Adk uses the 214-residue 1AKE sequence and open 4AKE/closed 1AKE controls. Mad2 uses the 197-position modeled construct, open 1DUJ/closed 1S2H controls and the 175-position experimental comparison mask; retain the mutation and missing-residue caveats.
5. **Reuse and limitations.** Explain the model-ID/hash joins and file guide. State that sampling frequencies are not equilibrium populations and displayed movies are heuristic orderings. Preserve native failures and missing-confidence distinctions.
6. **Rights and citation.** Summarize authored-content terms and separate third-party/AF3 notices, link the exact source release and companion target record, and direct users to cite the dataset version actually used. Preserve verified funding and acknowledgments.

Agree the title and opening paragraph first. Possible title patterns can emphasize the protein, conformational sampling, eleven-method cohort and paired refolds; choose the actual wording with the authors rather than carrying over “all models and scores” automatically. Keep the exact version label in the version field and make the description understandable without reading internal run IDs.

## Field review checklist

| Fields | Review decision |
| --- | --- |
| Title and description | Choose target-specific titles; approve the narrative and its exact rendered appearance |
| Resource type and version | Confirm dataset classification and an explicit dataset-version scheme, separately from the source-code tag |
| Creators and contributors | Preserve verified author order, ORCIDs and affiliations; confirm contributor roles |
| Dates | Distinguish publication/version date from actual generation provenance; do not infer generation date from file modification time |
| Keywords and subjects | Use consistent protein, conformational-sampling and method terms |
| Funding and acknowledgments | Carry forward verified identifiers and exact supported statements |
| Related identifiers | Link the companion target, source release and final poster using supported relations; add a paper DOI only when one exists |
| Rights and access | Preserve authored-content licensing, third-party exceptions, AF3 notices and the intended access decision |
| Files and provenance | Confirm exact member coverage, original/refold/reference roles, aliases, checksums and any archive reorganization |

The existing planner ties dataset `version` to the source tag. Review that coupling before implementing a separate dataset-version scheme; do not bypass the frozen source-release identity.

## Implementation stages

1. **Read current state.** Fetch both public records and inspect any existing editable/new-version drafts with read-only operations. Save timestamped metadata and file inventories privately so changes since this plan are visible.
2. **Author and review offline.** Create the metadata layer, draft both titles/descriptions, map each field to its source and show the old/new diff. Preview the exact formatted description. Resolve rights, date and field choices with the authors.
3. **Choose the operation per target.** Adk needs a corrected file version under its existing concept DOI. Mad2 can use a metadata edit if files are unchanged. Decide whether smaller archives improve Adk delivery without changing scientific bytes or dropping aliases. Preserve the existing verified packages.
4. **Implement the required adapter.** Add a reviewed path for new-version recovery; the current production wrapper blocks action endpoints and cannot perform it. Keep DOI identity checks, durable intent receipts, explicit upload selections and outcome reconciliation. Support metadata-only changes without unnecessary scientific packaging or uploads. Check the current Zenodo API/schema before implementing either path.
5. **Prepare the exact draft.** Obtain approval of the concrete target, field diff and file selection before remote writes. Reconcile uncertain outcomes before retries. For a new version, use its returned version DOI in citation files and regenerate affected metadata, landing documents and package seals consistently.
6. **Verify before manual publication.** Compare every remote file's size/checksum and the exact metadata with the reviewed version. Ensure the rendered description claims only present contents. Publication follows author review and manual verification.
7. **Reconcile distribution links.** Read the resulting public record, verify its title, description and complete files, then update GitHub status/catalog entries and citations. Keep poster concept DOI links and final poster bytes unchanged.
