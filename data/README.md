# Research datasets

Current analysis: 11,000 E. coli adenylate kinase predictions and 11,000 Mad2 monomer predictions, from 11 sampling methods. Each original has a matched Boltz2 no-MSA template-only refold. Bulk coordinates, per-residue arrays, score tables and immutable run evidence are distributed outside Git.

The selected [PyMOL comparison session and quick guide](pymol/README.md) are available in the dedicated `data/pymol/` folder. They match the virtual poster's embedded downloads byte-for-byte. This compact v008 session preserves its earlier comparison states; it is separate from the full-cohort datasets below.

- [Adk resources — all versions](https://doi.org/10.5281/zenodo.23601146). **Published v1 is incomplete:** 9 of 14 expected files are present. Missing: `outputs.tar.gz`, `provenance.tar.gz`, `reports.tar.gz`, `source.tar.gz` and `zenodo-metadata.json`. A corrected dataset version is required for the complete file collection.
- [Mad2 resources — all versions](https://doi.org/10.5281/zenodo.23601144). Published v1 contains all 14 expected upload files, with matching sizes and MD5 checksums against the verified local package.

Status checked against the public record APIs on 2026-10-23. Concept DOIs above identify all versions; use the exact version DOI of the files used in an analysis. Reference PDB models remain separate from AIS counts and unscored for confidence. See [distribution status](../docs/distribution-status.md), [Zenodo handling](../zenodo/README.md), [study guide](../docs/SCHERAGA-study.md), and [reference catalog](../docs/SCHERAGA-references.md).
