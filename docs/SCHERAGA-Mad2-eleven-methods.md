# Mad2 eleven-method update

The current Mad2 analysis contains **11,000 original AIS monomer predictions**, 1,000 from each of eleven methods, plus the unscored experimental controls [1DUJ open](https://www.rcsb.org/structure/1DUJ) and [1S2H closed](https://www.rcsb.org/structure/1S2H). Adk remains at 6,000 models. All former native physicality-filter failures are retained.

The new 5,000-model collection adds SPEACH_AF, AF-Cluster, AlphaFlow-PDB, AlphaFlow-MD and ESMFlow-PDB to the original six methods. Each has a hash-bound Boltz2 exact no-MSA template-only refold, with literal `/ptm` scores and sequence-validated residue pLDDT. Confidence is mapped to the original AIS structures; refold coordinates do not replace the sampled coordinates.

## Reference similarity and two-state score

The highest mean bidirectional US-align TM similarity is **0.80** to open 1DUJ (AF-Cluster model 0675) and **0.83** to closed 1S2H (Boltz2 model 0852). Comparisons use the same 175 shared Cα positions, target residues 3–101 and 112–187. Full 197-residue prediction structures remain intact. The R133A mutation in 1S2H and unresolved residues in 1DUJ remain documented in the reference catalog.

Each method’s two-state score is its best open-reference TM plus its best closed-reference TM. The two best matches may be different models. Rank uses unrounded values; displayed values use two decimal places.

| Rank | Method | Open TM | Closed TM | Two-state score |
| --- | --- | --- | --- | --- |
| 1 | AF-Cluster | 0.80 | 0.83 | 1.63 |
| 2 | OpenDDE | 0.79 | 0.83 | 1.61 |
| 3 | AF3 | 0.79 | 0.83 | 1.61 |
| 4 | Boltz2 | 0.78 | 0.83 | 1.60 |
| 5 | AF2 | 0.75 | 0.83 | 1.58 |
| 6 | BioEmu2-preview | 0.67 | 0.83 | 1.49 |
| 7 | BioEmu | 0.67 | 0.82 | 1.49 |
| 8 | ESMFlow-PDB | 0.67 | 0.81 | 1.48 |
| 9 | SPEACH_AF | 0.68 | 0.80 | 1.47 |
| 10 | AlphaFlow-PDB | 0.67 | 0.81 | 1.47 |
| 11 | AlphaFlow-MD | 0.66 | 0.80 | 1.47 |

## Analysis and movie scope

PCA, UMAP, t-SNE and component-preserving geometric clustering have been refitted for all 11,000 predictions and both controls. The current fit has **15 groups**. The physical t-SNE plot and virtual projection controls use Boltz2 template-only refold pTM with full-cohort observed minimum/maximum color limits. PCA axes report explained variance. The native physicality-failure category appears only under virtual Model type coloring.

The new movie search screened all 11,000 predictions; 8,853 passed the unchanged geometry gates. A 100-model candidate using the new highest-TM open endpoint had the same largest adjacent C-terminal jump as the prior route, **11.55 Å**. Under the strict-improvement gate, the current open-to-closed movie is retained and rejoined to the new projections and Bonsai. Its opening model remains OpenDDE 0787; the physical poster’s new highest-TM S1 is AF-Cluster 0675. The sequence of observed models is one heuristic structural ordering, with no morphing or physical kinetics claim.

The virtual all-medoid TM grid contains 15 prediction representatives and both PDB controls. The animation-inclusive Bonsai additionally contains all 100 displayed movie models.

**The abstract is deliberately unchanged at the author’s request.** Its previous counts and method list will be revised separately; current figure captions and this page describe the expanded cohort.

The reusable model-label configuration is [`SCHERAGA_Mad2_eleven_methods`](../src/app/templates/model_type_configs/SCHERAGA_Mad2_eleven_methods.json). Select this schema when reusing the analysis; it preserves the original six-method rules and adds specific model-name/source-path rules for the five new methods.

## Preservation and delivery

Earlier analyses, poster versions, raw coordinates, movie media, Adk figures and reference structures are preserved. The downloadable PyMOL session retains the prior comparison states; it does not yet include the new physical-poster S1, AF-Cluster 0675. The update uses local CPU analysis only, with no new folding/refolding jobs or paid calls. Both the print PDF and smaller phone PDF are linked from the [branch README](../README.md#downloads-and-links). Website and Zenodo links remain unpublished placeholders.
