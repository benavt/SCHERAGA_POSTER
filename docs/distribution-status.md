# Resource availability

**Status checked: 23 October 2026.** This page records the available poster, datasets and companion resources. Availability can change; follow the linked records for subsequent versions.

## Research datasets

| Target | All-versions DOI | Checked version | Availability |
| --- | --- | --- | --- |
| Adk | [10.5281/zenodo.23601146](https://doi.org/10.5281/zenodo.23601146) | [v1: 23601147](https://zenodo.org/records/23601147) | **Incomplete: 9 of 14 expected files** |
| Mad2 | [10.5281/zenodo.23601144](https://doi.org/10.5281/zenodo.23601144) | [v1: 23601145](https://zenodo.org/records/23601145) | Complete: 14 of 14 expected files |

All files present in the checked public records matched the expected sizes and MD5 checksums. The complete prepared packages also passed SHA-256 and MD5 checks against their package manifests. File verification does not independently validate the scientific conclusions.

**Adk v1 does not provide the complete model distribution.** The following expected files are missing: `outputs.tar.gz`, `provenance.tar.gz`, `reports.tar.gz`, `source.tar.gz` and `zenodo-metadata.json`. A corrected dataset version is needed under the existing Adk all-versions DOI. Until it is published, use the present record only within its documented file coverage.

All-versions (concept) DOIs provide durable navigation to a dataset's version family. For reproducible work, cite the exact version used.

## Poster and companion resources

| Resource | Version | Where to find it |
| --- | --- | --- |
| Full-resolution print and screen-reading PDFs | Final v014 | [Poster downloads](../poster/final/README.md) |
| Compact print PDF | v014, 120 dpi | [2.1 MB download and printing guide](../poster/print-friendly/README.md) |
| Poster preview and abstract | Final v014 | [Poster files](../poster/final/README.md) |
| Editable presentation source | v014 | Not included in this repository |
| Interactive poster | v025 | Not yet publicly deployed; [availability guide](../site/README.md) |
| Companion source snapshot | `scheraga-poster-v1.0.0` | [GitHub source release](https://github.com/benavt/SCHERAGA_POSTER/releases/tag/scheraga-poster-v1.0.0) |
| PyMOL comparison session | v008, earlier selected states | [Session and quick guide](../data/pymol/README.md); does not include all final-poster S1/S2 selections |

The [poster landing page](https://scheraga-poster.netlify.app) showed disabled “Coming soon” links at the status check. Use the repository's poster downloads above. The [machine-readable artifact inventory](SCHERAGA-downloads.json) records filenames and checksums; superseded metadata is documented in [the archive](archive/README.md).

For dataset packaging and maintenance, see the [deposition guide](../zenodo/README.md). Planned metadata improvements are described in the [metadata roadmap](../zenodo/metadata-rework-plan.md).
