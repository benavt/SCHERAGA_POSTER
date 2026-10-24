# Reading guide

Start with the [conference poster](../poster/README.md) for the visual overview, then choose the level of detail you need below.

## Understand the science

- [Study guide](SCHERAGA-study.md): the question, proteins, comparisons and limitations.
- [Adk results](SCHERAGA-Adk-eleven-methods.md) and [Mad2 results](SCHERAGA-Mad2-eleven-methods.md): method comparisons and selected structures.
- [Original-versus-refold comparison](SCHERAGA-original-refold-TM.md): how much each sampled structure changes in its matched refold.
- [Methods and references](SCHERAGA-references.md): papers, software and experimental structures.

## Key terms

| Term | Meaning in this study |
| --- | --- |
| Conformation | A three-dimensional shape adopted by a protein. |
| Conformational landscape | The range of protein shapes being explored. Sampling does not by itself measure their experimental populations. |
| AIS | Artificial intelligence sampling; AIS models are the original predicted structures in this study. |
| Experimental reference | A structure measured experimentally, used here as an open or closed comparison. |
| Refold | A matched Boltz2 template-only prediction used to assess the original model. It does not replace the original coordinates. |
| TM similarity | A coordinate-based measure of structural similarity; higher values indicate a closer match. The comparison protocol is specified in the methods. |
| pTM / pLDDT | Model confidence estimates for overall structure / individual residues. These differ from measured coordinate similarity. |
| MSA | Multiple sequence alignment: aligned related sequences that can inform structure prediction. |
| Projection | A simplified view of structural relationships, such as PCA, UMAP or t-SNE. Distances in a projection need interpretation in the context of its method. |

## Download and reuse

- [Poster downloads and printing](../poster/README.md)
- [Dataset links and reuse guidance](../data/README.md)
- [Dated distribution status](distribution-status.md)
- [Source provenance and scope](source-provenance.md)
- [Citation metadata](../CITATION.cff) and [licenses](../LICENSE-CONTENT.md)

## Technical reference

- [Figure style](SCHERAGA-physical-figure-style.md) and [typography](SCHERAGA-physical-typography.md)
- [Artifact inventory](SCHERAGA-downloads.json) and [reference catalog](SCHERAGA-reference-catalog.json)
- [Dataset inventories and deposition tooling](../zenodo/README.md)
- [Contributing and local checks](../CONTRIBUTING.md)

The [`archive/`](archive/README.md) directory preserves superseded bibliography and download metadata for provenance. Use the current guides above for citations and availability.
