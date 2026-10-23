# AI sampling of protein conformational landscapes

Code and documentation for **Beyond a Single Structure: Exploring Multistate Protein Conformational Landscapes with AI Structure Prediction**, by T.L. Benavides and G.T. Montelione.

We compare AI-sampled protein conformations with experimental open and closed references, then explore them through projections, structural comparisons and synchronized molecular views. This independent repository is a **snapshot**, not a fork of the private development history.

| Target | Current models | Experimental controls |
| --- | ---: | --- |
| E. coli adenylate kinase | 11,000 monomers | [4AKE open](https://www.rcsb.org/structure/4AKE), [1AKE closed](https://www.rcsb.org/structure/1AKE) |
| Mad2 mitotic spindle checkpoint protein | 11,000 monomers | [1DUJ open](https://www.rcsb.org/structure/1DUJ), [1S2H closed](https://www.rcsb.org/structure/1S2H) |

Each target has 1,000 predictions from AF2/AFSample2, AF3/AFSample3, OpenDDE, Boltz2, BioEmu, BioEmu2-preview, SPEACH_AF, AF-Cluster, AlphaFlow-PDB, AlphaFlow-MD and ESMFlow-PDB. The original four methods use stochastic 40% MSA column masking; additional methods retain their native protocols. Native physicality-filter failures remain in the analysis with flags.

## Explore

- [Study guide and selected states](docs/SCHERAGA-study.md)
- [Adk eleven-method analysis](docs/SCHERAGA-Adk-eleven-methods.md) and [Mad2 eleven-method analysis](docs/SCHERAGA-Mad2-eleven-methods.md)
- [Method papers, software and references](docs/SCHERAGA-references.md)
- [Measured original AIS versus matched refold TM similarity](docs/SCHERAGA-original-refold-TM.md)
- [Physical poster](poster/README.md), [interactive poster](site/README.md), [data availability](data/README.md) and [Zenodo Sandbox preparation](zenodo/README.md)
- Public website, poster/PSE downloads and two Zenodo deposition links: pending review; no new public links or DOIs are claimed here.

<table><tr><th>A · E. coli adenylate kinase</th><th>B · Mad2</th></tr><tr><td width="50%"><a href="docs/assets/SCHERAGA/Adk-poster-panel.png"><img src="docs/assets/SCHERAGA/Adk-poster-panel.png" width="100%" alt="Adk poster figures"></a></td><td width="50%"><a href="docs/assets/SCHERAGA/Mad2-poster-panel.png"><img src="docs/assets/SCHERAGA/Mad2-poster-panel.png" width="100%" alt="Mad2 poster figures"></a></td></tr></table>

## Scope and provenance

[Source provenance](docs/source-provenance.md) pins the imported source snapshot. This seed contains a small set of scoring/display adapters and conventions, not the complete clustering application or its environments. Scripts require externally supplied reviewed run plans, source files and dependencies; cloning this repository does not trigger analysis, folding, uploads or publication. Experimental references are controls, not AIS predictions. Confidence is not relative state population, and movie ordering is a structural-display heuristic, not a claimed physical pathway.

## Reuse

Code is MIT licensed, with the original copyright notice preserved. Authored poster text, documentation and data use [CC BY 4.0](LICENSE-CONTENT.md), excluding third-party material and logos, which retain their own terms. See [CITATION.cff](CITATION.cff), method references and future dataset-version citations.

## Contributor safeguards

Set `FLEET_ROOT` privately to the Fleet checkout, then run `python3 tools/check_privacy.py --tracked` before every push. The adapter runs Fleet's unchanged checker with this project's portable path allowlist, adds private-path/address checks, and permits only the explicit public GitHub owner URL. Install the hook with `git config core.hooksPath .githooks`. Private machine bindings and tokens belong outside tracked content.

Run offline safety checks with `python3 -m unittest discover -s tests`. The Sandbox wrapper rejects production, publication, abbreviated flags and unauthenticated remote draft writes before calling upstream. Its source-archive allowlist adds this companion's tools, manifests and content directories; ignored private state is never selected.
