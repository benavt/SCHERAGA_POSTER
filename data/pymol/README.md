# PyMOL comparison session

This folder provides the **corrected v010 PyMOL comparison session and quick guide**. Its saved Adk S1/S2 models now match the final physical poster. The molecular session uses the `.pse` extension.

- [Download the corrected PyMOL session (5.0 MB)](2026-10-23_Scheraga_four_comparisons_poster_Adk_v010.pse?raw=true)
- [Read the updated quick guide](2026-10-23_PyMOL-quick-guide_v010.txt)

Open the downloaded PSE file in PyMOL using **File → Open**. It contains four saved open/closed comparison scenes for Adk and Mad2, with eight protein objects and the preserved coloring controls. It initially opens in the Mad2 closed comparison. No companion plugin or script is required.

Adk S1 is **AlphaFlow-MD model 0703**, compared with open 4AKE; S2 is **AlphaFlow-PDB model 0327**, compared with closed 1AKE. Both retain all 214 residues and their native confidence values. Experimental reference objects, Mad2 comparison objects, cameras, labels and controls are preserved. Mad2 S1 remains the earlier comparison selection and differs from the final physical poster's AF-Cluster 0675. The observed-model movies and their endpoints are unchanged.

The session is not the complete 11,000-model collection for either target. See the [Adk](../../docs/SCHERAGA-Adk-eleven-methods.md) and [Mad2](../../docs/SCHERAGA-Mad2-eleven-methods.md) guides for the state distinctions and the [data guide](../README.md) for full dataset availability.

The [current manifest](manifest.json) records exact sizes, SHA-256 hashes, model identities and validation scope. Native model hashes match the published source and analysis inventories. A fresh PyMOL process verified all four saved scenes and seven controls; the two Adk scenes were also rendered and inspected. Verify both current and historical files with `sha256sum -c SHA256SUMS` from this directory.

The original [v008 session](Scheraga_four_comparisons_robust_controls_v008.pse?raw=true) and [guide](PyMOL-quick-guide.txt) remain unchanged. Their [dated original manifest](history/2026-10-23_v008/manifest.json) and [checksum text](history/2026-10-23_v008/SHA256SUMS) preserve the v025 embedded-download provenance. Those historical files describe the earlier state selection.

Authored content follows the [data content license](../LICENSE.md), with third-party and experimental-reference terms preserved. The update reuses existing native models and saved rigid display transforms; no scientific refitting, folding or scoring was performed.
