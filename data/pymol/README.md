# PyMOL comparison session

This folder provides the **same v008 PyMOL session and quick guide offered by the virtual poster**, copied without modification. The molecular session uses the `.pse` extension.

- [Download the PyMOL session (5.0 MB)](Scheraga_four_comparisons_robust_controls_v008.pse?raw=true)
- [Read the quick guide](PyMOL-quick-guide.txt)

Open the downloaded PSE file in PyMOL using **File → Open**. It contains four saved open/closed comparison scenes for Adk and Mad2, with eight protein objects and the preserved coloring controls. It initially opens in the Mad2 closed comparison. No companion plugin or script is required.

The selected AIS objects belong to the versioned virtual-poster session and are not all the same as the final physical poster's selected S1/S2 models. The session is not the complete 11,000-model collection for either target. See the [Adk](../../docs/SCHERAGA-Adk-eleven-methods.md) and [Mad2](../../docs/SCHERAGA-Mad2-eleven-methods.md) guides for the state distinctions and the [data guide](../README.md) for full dataset availability.

The [manifest](manifest.json) records exact byte counts, SHA-256 hashes and the source HTML identity. Both files were extracted from the v025 virtual poster's download elements and checked against the embedded bytes. The PSE also matches its earlier archived download hash. Verify files with `sha256sum -c SHA256SUMS` from this directory.

Authored content follows the [data content license](../LICENSE.md), with third-party and experimental-reference terms preserved. No coordinates, scenes or scores were regenerated for this distribution copy.
