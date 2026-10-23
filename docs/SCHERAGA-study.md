# SCHERAGA study guide

This branch supports the Adk / Mad2 study introduced in the [landing README](../README.md). It contains the reusable workflow code underlying the poster analyses. Exact figure reproduction also requires the selected input structures, model metadata, residue masks and frozen run settings.

## Cohort and conditioning

The current cohort contains 12,000 monomer predictions: 6,000 E. coli Adk models using the exact 1AKE sequence, and 6,000 Mad2 models from the separate Mad2-alone campaign. The earlier Mad2–peptide campaign and human AK1 / 7X7S campaign are historical analyses.

Each target contributes 1,000 models per sampling method. AF2 / AFSample2, AF3 / AFSample3, OpenDDE Exact and Boltz2 Exact use stochastic 40% MSA column masking. BioEmu and BioEmu2-preview use native unmasked conditioning. Native physicality-filter failures are retained in the current cohort and identified under Model type coloring in the virtual poster. Sampling counts are not equilibrium populations.

## Sampling papers and code

The [machine-readable reference catalog](SCHERAGA-references.json) records the verified publications, official repositories and poster citation numbers. AlphaFold foundation papers and the corresponding Kalakoti–Wallner sampling methods are cited separately.

| Sampling method | Sampling implementation | Foundation paper or method paper |
| --- | --- | --- |
| AF2 / AFsample2 | [Wallner lab AFsample2](https://github.com/wallnerlab/AFsample2) | [Kalakoti & Wallner, 2025](https://doi.org/10.1038/s42003-025-07791-9); [Jumper et al., 2021](https://doi.org/10.1038/s41586-021-03819-2) |
| AF3 / AFsample3 | [Wallner lab AFsample3](https://github.com/wallnerlab/afsample3) | [Kalakoti & Wallner, 2026, bioRxiv](https://doi.org/10.64898/2026.01.16.699904); [Abramson et al., 2024](https://doi.org/10.1038/s41586-024-07487-w) |
| OpenDDE | [Aureka Research OpenDDE](https://github.com/aurekaresearch/OpenDDE) | [OpenDDE project, 2026, arXiv](https://doi.org/10.48550/arXiv.2607.03787) |
| Boltz2 | [Boltz](https://github.com/jwohlwend/boltz) | [Passaro et al., 2025, bioRxiv](https://doi.org/10.1101/2025.06.14.659707) |
| BioEmu | [Microsoft BioEmu](https://github.com/microsoft/bioemu) | [Lewis et al., 2025](https://doi.org/10.1126/science.adv9817) |
| BioEmu2-preview | [Microsoft BioEmu2](https://github.com/microsoft/bioemu2) | [BioEmu2-preview v0.1.0rc0, released October 20, 2026](https://github.com/microsoft/bioemu2/releases/tag/v0.1.0rc0); distinct software reference |

BioEmu2 refers specifically to the October 20, 2026 preview release, package `0.1.0rc0`, rather than an unspecified current version. The inference checkout was official commit [`621fbe4d4338548ec8d0c74f4f16ea9e1d779232`](https://github.com/microsoft/bioemu2/commit/621fbe4d4338548ec8d0c74f4f16ea9e1d779232), four maintenance commits beyond the release tag; the differences are restricted to CI, Dependabot and pre-commit configuration. The `bioemu2-preview` checkpoint is pinned to Hugging Face revision `dd4b0c1b69984b68edcb6200a544213be4d75242`, with SHA256 `3b4ba9236b7b458f47b40b694847b6bb4110c744becd6d2c53de7b1d04c07a81`. The workflow records preserve these exact code and checkpoint identities.

## Experimental references and residue inputs

| Target | Open control | Closed control | Cα sites used in shared distance features |
| --- | --- | --- | --- |
| Adk | [4AKE](https://www.rcsb.org/structure/4AKE) | [1AKE](https://www.rcsb.org/structure/1AKE) | 214 |
| Mad2 | [1DUJ](https://www.rcsb.org/structure/1DUJ) | [1S2H](https://www.rcsb.org/structure/1S2H) | 175: target residues 3–101 and 112–187 |

Mad2 structures retain their full available coordinates; the shared-residue mask defines the distance-feature inputs and is not a coordinate trimming operation. 1DUJ is a C-terminally truncated open control. 1S2H is the closed R133A experimental mutant; its author-numbered residue 133 maps to target residue 125. The PyMOL comparison marks the corresponding AIS Arg125 and PDB Ala133 in magenta, including the sequences. Ligands are omitted from the monomer comparisons.

## Analysis and displays

Shared Cα pair distances feed the existing PCA, UMAP, t-SNE and Bonsai workflows. Experimental controls appear as labeled foreground stars in the projections and as reference entries in TM grids and Bonsai. PCA axes include explained-variance percentages.

Full bidirectional [US-align searches](https://doi.org/10.1038/s41592-022-01585-1) select the highest-TM prediction for each open and closed reference. Scores below are rounded to two decimal places; the saved analysis retains full precision. TM similarity and ranking confidence are separate quantities.

| Target | State | Sampling method | Model ID | Reference | TM similarity |
| --- | --- | --- | --- | --- | --- |
| Adk | S1, open match | AF2 / AFSample2 | 0348 | 4AKE | 0.96 |
| Adk | S2, closed match | OpenDDE Exact | 0572 | 1AKE | 0.99 |
| Mad2 | S1, open match | OpenDDE Exact | 0787 | 1DUJ | 0.79 |
| Mad2 | S2, closed match | Boltz2 Exact | 0852 | 1S2H | 0.83 |

Both target movies display the open-to-closed direction. The Mad2 display reverses the same 100-model sequence; coordinates, camera and timing are retained. The interactive poster shows 100 observed models per movie over 10 seconds, with model correspondence maintained across the structure view, projections and animation-inclusive Bonsai tree. Playback time is a display choice. Its default target-page view is t-SNE, colored by Boltz2 template-only refold pTM for both targets, with optional native pTM, cluster, model-type and reference-TM coloring. BioEmu methods have no native pTM values; these are not imputed. All 6,000 models per target have validated Boltz2 template-only refold confidence. Both physical t-SNE panels use refold pTM; matched Viridis and Plasma versions use the same 0–1 scale. The virtual poster maps per-residue refold pLDDT onto the same AIS movie structures using [AlphaFold confidence colors](https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/plddt-understanding-local-confidence/). Refold coordinates do not replace AIS coordinates. Each frame reports literal refold pTM beside both reference TM similarities. The independent pTM scalar and per-residue pLDDT arrays are taken from their respective verified Boltz2 outputs.

These movies show one heuristic ordering of 100 existing AIS predictions per target, rather than a proposed physical transition pathway or kinetics. They omit many of the 6,000 predictions in each target’s full landscape. The projections retain all 6,000 predictions; animation-inclusive Bonsai trees include the movie models, selected cluster representatives and experimental controls.

The downloadable PyMOL session contains four AIS/PDB open/closed comparisons, matching chainbow coloring, region coloring and an optional AlphaFold-style pLDDT palette. Experimental B factors are not interpreted as pLDDT.

## Code entry points

- [scripts/run_structure_workflow.py](../scripts/run_structure_workflow.py): reusable workflow driver for a supplied model directory.
- [src/analysis/](../src/analysis/): structure features, metrics and analysis implementation.
- [scripts/run_bonsai_scout.py](../scripts/run_bonsai_scout.py): Bonsai exploration launcher.
- [docs/experimental-references.md](experimental-references.md): experimental-control conventions.
- [docs/presentation-deliverables.md](presentation-deliverables.md): plot and presentation exports.
- [docs/molecular-visualization-sizing.md](molecular-visualization-sizing.md): molecular display guidance.

See the installation and CLI examples in the expandable documentation in the [landing README](../README.md). Frozen scientific settings and selected input manifests are needed to reproduce an existing poster figure; running default settings alone does not establish exact reproduction. Historical `7X7S` adapters address earlier cohorts and should not be treated as the current 1AKE campaign configuration.

## Data and access

The public poster URL and Zenodo links for models and template-only refold scores will be added to the landing page when their final addresses are supplied. No placeholder DOI is presented as a completed deposition. This repository currently requires GitHub access; repository visibility has not been changed as part of the landing-page update.
