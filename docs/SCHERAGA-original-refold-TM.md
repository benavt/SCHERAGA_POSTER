# Original AIS versus Boltz2-refold TM similarity

The virtual poster offers **AIS ↔ Boltz2 refold TM** as an additional projection-coloring option. It compares each original sampled structure with its own exact no-MSA, template-only Boltz2 refold. This is a measured coordinate similarity, distinct from the refold’s predicted confidence, pTM. The default coloring remains **Boltz2 refold pTM**.

All 22,000 predictions are covered: 11,000 Adk and 11,000 Mad2, with 1,000 predictions per method and target. Original/refold identity is joined by model ID and both structure hashes, rather than file order. Original AIS coordinates remain the structures shown in the poster.

## Definition and verified results

Each score is the mean of two full-search US-align TM scores, original→refold and refold→original, with average-length normalization (`-mol prot -ter 1 -a T`). The comparison uses the full predicted chain: **214 Adk Cα positions** or **197 Mad2 Cα positions**. Mad2’s separate comparison to experimental references uses 175 shared positions; that experimental mask is not applied here. Experimental PDB controls have no paired refold score and remain unscored stars.

Inputs are ephemeral Cα-only PDB representations at 0.001-Å precision. Input preparation does not fit, repair or edit source coordinates; US-align performs the structural superposition needed for scoring. Full sequence, chain and residue correspondence are checked before scoring. Raw BioEmu numbering differences remain bound to the existing normalized analysis copies, whose coordinates are unchanged.

| Target | Pairs | Minimum TM | Median TM | Maximum TM |
| --- | --- | --- | --- | --- |
| Adk | 11,000 | 0.30 | 0.92 | 1.00 |
| Mad2 | 11,000 | 0.41 | 0.98 | 1.00 |

Table values are rounded to hundredths; coloring uses unrounded values.

All 44,000 directional results were independently checked against raw US-align output, source hashes, complete sequences, Cα conversion, reported structure lengths and the bidirectional formula. Numeric projection colors use Plasma with each target’s observed full-cohort minimum and maximum, consistently across PCA, UMAP and t-SNE. The current-frame readout includes the paired TM value only while this coloring is active. This quantity does not describe state populations or transition kinetics.

## Reproduction source and recovery lineage

The study-specific adapters are in [`scripts/studies/SCHERAGA/original_refold_tm`](../scripts/studies/SCHERAGA/original_refold_tm):

- [`score_pairs_v002.py`](../scripts/studies/SCHERAGA/original_refold_tm/score_pairs_v002.py) is the **corrected scorer used to finish this run**. Runtime paths, engine pin, source manifest and approval receipt are supplied by an immutable run directory through `--run-dir`.
- [`score_pairs.py`](../scripts/studies/SCHERAGA/original_refold_tm/score_pairs.py) is retained **only as historical provenance**. Its initial format detector misidentified a valid AF3 mmCIF with comments before `data_` as PDB. Five pilot pairs had completed before the input gate stopped execution. Do not use this historical entry point for a new run.
- Version 002 recognizes the standard mmCIF data block after comments, preserves the failed attempt, and reuses those five independently verified pairs. It computed only the remaining 21,995 pairs: 43,990 new directional calls plus the ten reused calls, for exactly 44,000 overall. Residue masks, coordinates, sequence gates, precision, normalization and comparison options were unchanged.
- [`normalize_metric.py`](../scripts/studies/SCHERAGA/original_refold_tm/normalize_metric.py) joins the completed score table to exact source identities after completed-score and independent-validation receipts pass.
- [`apply_metric.py`](../scripts/studies/SCHERAGA/original_refold_tm/apply_metric.py) adds the scalar and controls to the hash-pinned parent poster in memory. It does not write exports or compute scores. Removing the added metric dictionaries recovers the prior scientific payload exactly.

The existing [`parse_average_length_tm`](../src/analysis/cluster_medoid_tm.py) implementation is reused. The engine was US-align version 20241108, SHA256 `cdb4ec43f97f220204425bf9c9a253f63ef40986f69767b0540baeeaa7b12990`.

These are copies of the actual run adapters, including the guarded historical recovery contract, rather than an automatic rerun launcher. Reproducing or extending the calculation requires separately prepared source/engine hashes, paired inputs, execution plan and explicit approval; version 002 also requires the preserved pilot evidence and recovery receipt. Linux CPU affinity is enforced. The source does not provision an environment, fold/refold models or call a paid service. Machine paths and access bindings belong in local runtime manifests, not in this repository. The [data guide](../data/README.md) links both published dataset concept DOIs and documents the incomplete Adk v1 upload.

Projection coordinates, cluster assignments, selected states, Bonsai trees, movie frames, cameras and timing are unchanged by adding this scalar. Both model-label configurations and the author’s working abstract are preserved. Physical-poster display revisions are tracked separately.
