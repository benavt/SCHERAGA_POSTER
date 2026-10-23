# Adk eleven-method update

The current E. coli adenylate kinase analysis contains **11,000 original AIS monomer predictions**, 1,000 from each of eleven methods, plus the unscored experimental controls [4AKE open](https://www.rcsb.org/structure/4AKE) and [1AKE closed](https://www.rcsb.org/structure/1AKE). Together with the preserved 11,000-model Mad2 analysis, the study now contains **22,000 predictions**. All 35 former Adk native physicality-filter failures are retained.

This extension adds SPEACH_AF, AF-Cluster, AlphaFlow-PDB, AlphaFlow-MD and ESMFlow-PDB to AF2 / AFSample2, AF3 / AFSample3, OpenDDE, Boltz2, BioEmu and BioEmu2-preview. Every prediction has a matched, hash-bound Boltz2 exact no-MSA template-only refold. Literal `/ptm` scores and sequence-validated residue pLDDT describe refold confidence mapped onto the original AIS structures; refold coordinates do not replace sampled coordinates.

## Reference similarity and two-state score

The highest mean bidirectional US-align TM similarity is **0.97** to open 4AKE (AlphaFlow-MD model 0703) and **0.99** to closed 1AKE (AlphaFlow-PDB model 0327). The input is the exact 1AKE sequence; all comparisons use the same **214 shared Cα positions**, residues 1–214. Full prediction and reference structures remain intact, and displayed protein views omit ligands.

Each method’s two-state score is its best open-reference TM plus its best closed-reference TM, allowing different models for the two maxima. Ranking uses unrounded scores; displayed TM values use two decimal places. The two methods supplying the global open and closed matches do not lead the combined two-state ranking.

| Rank | Method | Open TM | Closed TM | Two-state score |
| --- | --- | --- | --- | --- |
| 1 | Boltz2 | 0.96 | 0.97 | 1.93 |
| 2 | AF2 | 0.96 | 0.94 | 1.90 |
| 3 | OpenDDE | 0.90 | 0.99 | 1.89 |
| 4 | AF3 | 0.90 | 0.98 | 1.88 |
| 5 | SPEACH_AF | 0.88 | 0.98 | 1.87 |
| 6 | BioEmu2-preview | 0.96 | 0.90 | 1.86 |
| 7 | BioEmu | 0.89 | 0.97 | 1.85 |
| 8 | AlphaFlow-MD | 0.97 | 0.85 | 1.82 |
| 9 | ESMFlow-PDB | 0.83 | 0.98 | 1.81 |
| 10 | AF-Cluster | 0.94 | 0.86 | 1.80 |
| 11 | AlphaFlow-PDB | 0.74 | 0.99 | 1.73 |

## Analysis and movie scope

PCA, UMAP, t-SNE and component-preserving geometric clustering have been refitted using all 11,000 Adk predictions and both controls. The fit has **six prediction groups**. The all-medoid TM grid contains six prediction representatives and the two PDB controls. The animation-inclusive Bonsai contains **108 leaves**, including all 100 current movie models, one representative per group and both unscored controls. The tree uses full numerical rank without whitening, preserving Euclidean distances between its input feature rows.

The new movie search screened all 11,000 predictions; 9,422 passed the unchanged geometry gates, including the approved cis-Pro exception. Both new highest-TM endpoints passed, but their 100-model candidate had a largest moving-region jump of 1.20133128 Å, compared with the prior route’s 1.19999901 Å. Under the strict-improvement gate, the **existing 100-model open-to-closed movie is retained**, with exact media, order, camera and timing. Its endpoints remain AFSample2 0348 and OpenDDE 0572; the physical poster’s new S1/S2 are AlphaFlow-MD 0703 and AlphaFlow-PDB 0327. The ordering is one heuristic description of structural similarity, not a physical transition pathway or kinetics, and omits many sampled states.

Projection coloring uses verified Boltz2 template-only refold pTM with observed full-cohort minimum/maximum limits. Confidence does not measure relative state populations in solution. Chainbow remains the movie default, with an optional AlphaFold-palette refold-pLDDT view. Native physicality-failure flags appear only under virtual Model type coloring.

The reusable model-label configuration is [`SCHERAGA_Adk_eleven_methods`](../src/app/templates/model_type_configs/SCHERAGA_Adk_eleven_methods.json). It preserves all original rules and adds specific model-name/source-path rules for the five new methods.

**The poster abstract is deliberately unchanged at the author’s request.** Its previous counts and method list will be revised separately; current figures and these results pages describe the expanded cohort. The [Mad2 extension page](SCHERAGA-Mad2-eleven-methods.md) records the preceding update; its statement that Adk then had 6,000 models is historical.

## Preservation and delivery

Mad2 coordinates, scores, projections, tree, figures and movie remain unchanged. Earlier Adk analyses, raw coordinates, movies and PDB sources are preserved. The downloadable PyMOL session retains the prior comparison states and does not yet contain the new physical Adk S1/S2. No new folding/refolding jobs, paid calls or environment installs were used. Smaller phone and full-resolution print PDFs are available from the [branch README](../README.md#downloads-and-links); website and the two target-specific Zenodo links remain unpublished placeholders.
