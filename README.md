# Beyond a Single Structure

**Exploring Multistate Protein Conformational Landscapes with AI Structure Prediction**

T.L. Benavides and G.T. Montelione

Public companion to a conference poster, with poster downloads, study explanations, analysis code and links to the research datasets. It is intended for researchers, students, conference visitors and anyone curious about how AI can help explore protein shapes.

[Read the poster](poster/final/SCHERAGA_poster_36x48_both_11methods_phone_v014.pdf?raw=true) · [Study guide](docs/SCHERAGA-study.md) · [Data downloads](data/README.md) · [Methods and references](docs/SCHERAGA-references.md)

[![Adk dataset DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23601146.svg)](https://doi.org/10.5281/zenodo.23601146)
[![Mad2 dataset DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23601144.svg)](https://doi.org/10.5281/zenodo.23601144)

## Why study more than one protein shape?

Proteins change shape as they work. A single predicted structure can therefore tell only part of the story. This study asks how well eleven AI sampling methods explore different shapes of two proteins: **adenylate kinase (Adk)**, an enzyme involved in cellular energy balance, and **Mad2**, a protein involved in controlling cell division.

We compare 1,000 predictions from each method with experimentally determined open and closed structures. The study contains **22,000 original predictions**, split equally between the two proteins. Structural comparisons and visualizations help show which shapes the methods reach and how those shapes differ.

## Start exploring

| If you want to… | Start here |
| --- | --- |
| View the conference poster | [Screen-reading PDF, 11.2 MB](poster/final/SCHERAGA_poster_36x48_both_11methods_phone_v014.pdf?raw=true) |
| Print the poster | [Full-resolution PDF, 24 MB](poster/final/SCHERAGA_poster_36x48_both_11methods_print_v014.pdf?raw=true) or [compact PDF, 2.1 MB](poster/print-friendly/SCHERAGA_poster_36x48_print_compact_v014.pdf?raw=true); 36 × 48 inches |
| Understand the study and terminology | [Study guide](docs/SCHERAGA-study.md) and [reading guide](docs/README.md) |
| Examine the results | [Adk analysis](docs/SCHERAGA-Adk-eleven-methods.md) and [Mad2 analysis](docs/SCHERAGA-Mad2-eleven-methods.md) |
| Explore selected structures in PyMOL | [Comparison session and quick guide](data/pymol/README.md) |
| Download or reuse research data | [Dataset guide and availability](data/README.md) |
| Inspect the code or contribute | [Repository guide](#repository-guide) and [contributing](CONTRIBUTING.md) |

**Availability, checked 23 October 2026:** the poster PDFs are included here. Mad2 v1 contains all 14 expected files. **Adk v1 is incomplete (9 of 14 files); its model-output archive is missing.** Read the [availability details](docs/distribution-status.md) before using that dataset. The interactive poster is not yet publicly deployed; see the [interactive-poster guide](site/README.md).

[![Conference poster preview](poster/final/SCHERAGA_poster_36x48_both_11methods_v014_preview.png)](poster/final/SCHERAGA_poster_36x48_both_11methods_phone_v014.pdf?raw=true)

## Study at a glance

| Protein | Original predictions | Experimental open / closed references |
| --- | ---: | --- |
| *E. coli* adenylate kinase (Adk) | 11,000 | [4AKE](https://www.rcsb.org/structure/4AKE) / [1AKE](https://www.rcsb.org/structure/1AKE) |
| Mad2 | 11,000 | [1DUJ](https://www.rcsb.org/structure/1DUJ) / [1S2H](https://www.rcsb.org/structure/1S2H) |

The eleven methods are AF2/AFSample2, AF3/AFSample3, OpenDDE, Boltz2, BioEmu, BioEmu2-preview, SPEACH_AF, AF-Cluster, AlphaFlow-PDB, AlphaFlow-MD and ESMFlow-PDB. The original four methods use stochastic masking of 40% of multiple-sequence-alignment columns; the additional methods retain their native protocols. Each original prediction has a matched Boltz2 template-only refold for comparison. Predictions that failed native physicality filters remain included and flagged.

Prediction confidence and structural similarity answer different questions. Neither establishes how often a protein adopts a shape in an experiment. Movies order observed models by a structural-display heuristic; they do not establish a physical transition pathway or its timing. See the [study guide](docs/SCHERAGA-study.md) for definitions and limitations.

## Repository guide

| Directory | Contents |
| --- | --- |
| [`poster/`](poster/README.md) | Final poster, preview, abstract and printing options |
| [`docs/`](docs/README.md) | Study guide, target results, references and figure conventions |
| [`data/`](data/README.md) | Dataset links, availability and reuse guidance |
| [`site/`](site/README.md) | Interactive-poster description and availability |
| [`src/`](src/) and [`scripts/`](scripts/) | Selected analysis utilities and model-label configurations |
| [`zenodo/`](zenodo/README.md) | Data inventories and deposition tooling documentation |
| [`tools/`](tools/) and [`tests/`](tests/) | Repository checks, packaging tools and automated checks |

The code is a selected source snapshot accompanying the poster. It does not include the complete interactive analysis application, model weights or bulk datasets. Analysis scripts need their documented inputs and dependencies; see [source provenance](docs/source-provenance.md). The [source release](https://github.com/benavt/SCHERAGA_POSTER/releases/tag/scheraga-poster-v1.0.0) identifies the initial code snapshot.

## Citation and reuse

Use [CITATION.cff](CITATION.cff) to cite this companion, and cite the exact dataset version and relevant [method papers](docs/SCHERAGA-references.md) when reusing results.

Code is available under the [MIT license](LICENSE). Authored poster text, documentation and data use [CC BY 4.0](LICENSE-CONTENT.md), with third-party material and logos retaining their own terms. Dataset users must also preserve the supplied AlphaFold 3 output notices. See [attribution](NOTICE.md) and the dataset-specific rights information.
