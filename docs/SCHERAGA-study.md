# Study guide

This conference-poster companion describes **22,000 original artificial intelligence sampling (AIS) monomer predictions: 11,000 per target, 1,000 per sampling method**. Each original has a matched Boltz2 no-MSA template-only refold with confidence and original-versus-refold TM measurements. The canonical scientific data remain outside Git; the [verified offline inventory](../zenodo/manifests/README.md) records relative paths, byte counts and SHA-256 hashes.

## Targets and experimental controls

- E. coli adenylate kinase uses the 214-residue 1AKE sequence. References are [4AKE open](https://www.rcsb.org/structure/4AKE) and [1AKE closed](https://www.rcsb.org/structure/1AKE), compared over all 214 shared Cα positions. The current highest-reference-TM AIS states are AlphaFlow-MD 0703 (open, 0.97) and AlphaFlow-PDB 0327 (closed, 0.99).
- Mad2 uses the 197-residue monomer collection, with no peptide. References are [1DUJ open](https://www.rcsb.org/structure/1DUJ) and [1S2H closed](https://www.rcsb.org/structure/1S2H). Reference comparisons and clustering use 175 shared Cα positions, target residues 3–101 and 112–187. Full structures remain intact; the 1S2H R133A mutation and missing reference residues are explicitly documented. The current highest-reference-TM AIS states are AF-Cluster 0675 (open, 0.80) and Boltz2 0852 (closed, 0.83).

Experimental controls are unscored PDB references, excluded from AIS counts and confidence rankings. Native physicality-filter failures remain included and flagged. Reference similarity does not establish relative state populations.

## Analysis and display

The eleven methods, per-method two-state scores and current fit details are documented in the [Adk results](SCHERAGA-Adk-eleven-methods.md) and [Mad2 results](SCHERAGA-Mad2-eleven-methods.md). Shared Cα pair distances provide the features for projections and Bonsai. Reference selection uses full bidirectional US-align searches, not pTM. [Original-versus-refold TM similarity](SCHERAGA-original-refold-TM.md) is a separate matched-model measurement. Boltz2 refold pTM is a scalar confidence score; refold pLDDT is a per-residue confidence array mapped to AIS coordinates without replacing those coordinates.

Both preserved movies run open to closed through 100 observed AIS models over ten seconds. They illustrate one heuristic structural ordering, not a proposed physical pathway or kinetics. They omit many sampled states. The expanded-cohort route candidates did not pass the strict improvement gate, so movie endpoints can differ from the current highest-TM physical-poster S1/S2. Each target results page identifies that distinction. The full projections contain 11,000 AIS models per target; animation-inclusive Bonsai trees include movie models, selected group representatives and controls.

## What this repository contains

This companion includes a selected source snapshot of the interactive clustering application, with the [scoring adapters](../scripts/studies/SCHERAGA/original_refold_tm/), [printed figure conventions](SCHERAGA-physical-figure-style.md), model-label schemas and [method bibliography](SCHERAGA-references.md). Source revisions and reproduction scope are recorded in [provenance](source-provenance.md). Reproducing the analyses requires the frozen scientific inputs, run plans and analysis environment. See the reproduction scope in the provenance guide.

The [poster](../poster/README.md), [website](../site/README.md) and [data](../data/README.md) guides describe current distribution. Both Zenodo concept DOIs are published: [Adk](https://doi.org/10.5281/zenodo.23601146) and [Mad2](https://doi.org/10.5281/zenodo.23601144). Mad2 v1 and the [corrected Adk version](https://doi.org/10.5281/zenodo.23607500) each contain all 14 expected upload files. The earlier incomplete Adk v1 remains in the version history. See [distribution status](distribution-status.md) and the [Zenodo runbook](../zenodo/README.md).
