# Resource availability

**Status checked: 23 October 2026.** This page records the available poster, datasets and companion resources. Availability can change; follow the linked records for subsequent versions.

## Research datasets

| Target | All-versions DOI | Checked version | Availability |
| --- | --- | --- | --- |
| Adk | [10.5281/zenodo.23601146](https://doi.org/10.5281/zenodo.23601146) | [Corrected: 23607500](https://zenodo.org/records/23607500) | Complete: 14 of 14 expected files |
| Mad2 | [10.5281/zenodo.23601144](https://doi.org/10.5281/zenodo.23601144) | [v1: 23601145](https://zenodo.org/records/23601145) | Complete: 14 of 14 expected files |

All files present in the checked public records matched the expected sizes and MD5 checksums. The complete prepared packages also passed SHA-256 and MD5 checks against their package manifests. File verification does not independently validate the scientific conclusions.

The corrected Adk version, `scheraga-poster-v1.0.0-corrected` ([10.5281/zenodo.23607500](https://doi.org/10.5281/zenodo.23607500)), restores `outputs.tar.gz`, `provenance.tar.gz`, `reports.tar.gz`, `source.tar.gz` and `zenodo-metadata.json`. Its public description and version were verified, and the all-versions DOI resolves to this corrected record. The [initial v1 record](https://zenodo.org/records/23601147) remains in the version history with 9 of 14 expected files; it does not provide the complete model distribution.

All-versions (concept) DOIs provide durable navigation to a dataset's version family. For reproducible work, cite the exact version used.

## Poster and companion resources

| Resource | Version | Where to find it |
| --- | --- | --- |
| Full-resolution print and screen-reading PDFs | Final v014 | [Poster downloads](../poster/final/README.md) |
| Compact print PDF | v014, 120 dpi | [2.1 MB download and printing guide](../poster/print-friendly/README.md) |
| Poster preview and abstract | Final v014 | [Poster files](../poster/final/README.md) |
| Editable presentation source | v014 | Not included in this repository |
| Interactive poster | Web v001 / offline v036 | [GitHub Pages](https://benavt.github.io/SCHERAGA_POSTER/); [offline HTML release](https://github.com/benavt/SCHERAGA_POSTER/releases/tag/2026-10-23_virtual-poster-v036) |
| Companion source snapshot | `scheraga-poster-v1.0.0` | [GitHub source release](https://github.com/benavt/SCHERAGA_POSTER/releases/tag/scheraga-poster-v1.0.0) |
| PyMOL comparison session | Corrected v010 | [Session and quick guide](../data/pymol/README.md); Adk S1/S2 match the final physical poster, while Mad2 comparisons remain unchanged; original v008 retained |

GitHub Pages hosts the standalone interactive poster. The earlier [Netlify landing page](https://scheraga-poster.netlify.app) is unchanged. The [machine-readable artifact inventory](SCHERAGA-downloads.json) records filenames and checksums; superseded metadata is documented in [the archive](archive/README.md).

For dataset packaging and maintenance, see the [deposition guide](../zenodo/README.md). Planned metadata improvements are described in the [metadata roadmap](../zenodo/metadata-rework-plan.md).
