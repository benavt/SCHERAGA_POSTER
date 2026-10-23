# Distribution status — 2026-10-23

The scientific cohort and final poster exports already exist. The remaining work is distribution, deposition repair and presentation. No folding, refolding, clustering or alignment rerun is needed to recover the verified packages.

## Published datasets

| Target | All-versions DOI | Published version | Verified availability |
| --- | --- | --- | --- |
| Adk | [10.5281/zenodo.23601146](https://doi.org/10.5281/zenodo.23601146) | [v1: 23601147](https://zenodo.org/records/23601147) | 9 of 14 expected files; incomplete |
| Mad2 | [10.5281/zenodo.23601144](https://doi.org/10.5281/zenodo.23601144) | [v1: 23601145](https://zenodo.org/records/23601145) | 14 of 14 expected files; complete |

The public record APIs were read on 2026-10-23. Every present file matched the expected size and MD5 checksum. All 14 files in each complete local package also passed fresh SHA-256 and MD5 comparisons against its saved package seal. Earlier saved validation covers individual archive members and privacy review; this audit did not rerun the science.

The Adk `outputs.tar.gz` upload (1,022,694,730 bytes) returned HTTP 500 before manual publication. Five files are absent from the published record: `outputs.tar.gz`, `provenance.tar.gz`, `reports.tar.gz`, `source.tar.gz` and `zenodo-metadata.json`. The published record cannot be treated as a complete model distribution. Its local receipt still says `uploading`; the public record establishes that v1 has since been published.

Repair Adk through a corrected new version within the existing concept DOI. Preserve public v1 and the verified local packages. The current draft-upload wrapper does not implement the new-version action and deliberately blocks action endpoints; recovery needs a separately reviewed new-version workflow. Repeating its original draft command is not a repair for a published record.

## Current artifact inventory

| Artifact | Current validated version | Distribution state |
| --- | --- | --- |
| Print and phone poster PDFs | v014 | Local; public release downloads needed |
| Editable PPTX, preview and abstract text | v014 | Local; hashes recorded |
| Interactive poster HTML | v025 | Local; 14 saved browser checks; includes both concept DOIs and v014 phone PDF |
| Public website | Landing page | Five disabled “Coming soon” links; interactive poster not deployed |
| Companion source | `scheraga-poster-v1.0.0` | Public GitHub release; no attached artifact files |
| PyMOL comparison session | Historical export | Prior comparison states; new physical-poster S1/S2 selections are not all included |

The [machine-readable artifact inventory](SCHERAGA-downloads.json) records the final filenames and hashes. Historical private-source download metadata is preserved in `docs/archive/`; it is not the current public download catalog.

## Finalization order

1. Agree the Zenodo titles, descriptions and archive organization. Keep one record per target and retain both concept DOIs unless the scientific resource boundaries change. A useful organization separates native coordinates, analysis copies, matched refolds, scores, reports and provenance; method-level coordinate archives would reduce individual transfer size. Retain alias mappings and exact member hashes.
2. Prepare the corrected Adk version from verified existing data. Reconcile remote state before writing; verify every remote file and the metadata before manual publication. Preserve AF3 output notices, PDB attribution, creator order and the distinction between authored CC BY content and third-party rights.
3. Rework Mad2 metadata or files only where the agreed organization calls for it. Its present v1 package is complete.
4. Distribute the validated poster PDFs and editable source with fixed filenames and hashes; update download links only after assets exist publicly. Decide whether to update the historical PyMOL session to the final selected states or label its earlier scope.
5. Deploy the validated interactive poster and replace all five disabled landing-page entries with verified destinations. Display an accurate Adk availability notice until the corrected version is published.
6. Check GitHub README, release notes, citation metadata, website and poster links together. Use concept DOIs for durable navigation and exact version DOIs for dataset citations. Keep release history and old hashes rather than renaming old artifacts as final.

Zenodo publication remains manual. Website deployment and new release creation require their concrete reviewed scope; this status cleanup performs neither.
