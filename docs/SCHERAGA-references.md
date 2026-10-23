# Study references

The [machine-readable catalog](SCHERAGA-reference-catalog.json) contains the verified public bibliography and method coverage used by the virtual poster. Numbers follow first appearance in its Abstract page and figure/method notes. Superscript citations on either target page navigate to the corresponding entry in the Abstract page’s References section. PDB identifiers link to RCSB entries; publication and software links remain separate.

## AI sampling methods

| Sampling implementation | Virtual reference numbers |
| --- | --- |
| AFSample2/AF2 | [5](#reference-5), [6](#reference-6) |
| AFSample3/AF3 | [7](#reference-7), [8](#reference-8) |
| OpenDDE | [9](#reference-9) |
| Boltz2 | [10](#reference-10) |
| BioEmu | [11](#reference-11) |
| BioEmu2-preview | [12](#reference-12) |
| SPEACH_AF | [19](#reference-19) |
| AF-Cluster | [20](#reference-20) |
| AlphaFlow-PDB | [21](#reference-21) |
| AlphaFlow-MD | [21](#reference-21) |
| ESMFlow-PDB | [21](#reference-21) |

AlphaFlow-PDB, AlphaFlow-MD and ESMFlow-PDB share the AlphaFlow paper and repository (21); they are distinct sampling configurations, rather than three separately claimed publications. BioEmu2-preview cites its explicit software release (12), separately from the BioEmu paper (11).

## Analysis and scoring

| Method | Virtual reference numbers |
| --- | --- |
| UMAP | [13](#reference-13) |
| PCA | [14](#reference-14) |
| t-SNE | [15](#reference-15) |
| native Bonsai/Bonsai-scout | [16](#reference-16) |
| US-align | [17](#reference-17) |
| AFRank | [18](#reference-18) |

US-align describes the alignment and TM-score methodology. AFRank motivates template-only refold confidence scoring; it does not describe our movie ordering. The movie route is custom study code: stable-region alignment, moving-region Cα RMSD graph search, fixed open/closed endpoints, insertion and ordering of observed predictions. Its code provenance is this repository ([full branch URL](https://github.com/benavt/Structure_Clustering/tree/SCHERAGA)), with frozen run receipts retained locally. This heuristic display order is not an inferred physical transition pathway. The virtual movie-method dropdown documents the current algorithm and links to this code; no external paper is presented as its source.

## Physical-poster numbering

The compact physical bibliography has an independent six-reference sequence: 1–4 are the four PDB structure publications below, 5 is Kalakoti and Wallner (virtual 5), and 6 is Roney and Ovchinnikov (virtual 18). The physical poster directs readers to the virtual poster for the complete method bibliography. Never transfer virtual superscript numbers directly into the physical six-entry list.

## Complete virtual bibliography

<a id="reference-1"></a>
1. Müller CW, Schlauderer GJ, Reinstein J, Schulz GE. (PDB 4AKE). (1996). Adenylate kinase motions during catalysis: an energetic counterweight balancing substrate binding. <i>Structure</i> 4, 147–156. <a href="https://doi.org/10.1016/S0969-2126(96)00018-4" target="_blank" rel="noopener">doi:10.1016/S0969-2126(96)00018-4</a>.

<a id="reference-2"></a>
2. Müller CW, Schulz GE. (PDB 1AKE). (1992). Structure of the complex between adenylate kinase from Escherichia coli and the inhibitor Ap5A refined at 1.9 Å resolution. A model for a catalytic transition state. <i>Journal of Molecular Biology</i> 224, 159–177. <a href="https://doi.org/10.1016/0022-2836(92)90582-5" target="_blank" rel="noopener">doi:10.1016/0022-2836(92)90582-5</a>.

<a id="reference-3"></a>
3. Luo X, Fang G, Coldiron M, Lin Y, Yu H, Kirschner MW, Wagner G. (PDB 1DUJ). (2000). Structure of the Mad2 spindle assembly checkpoint protein and its interaction with Cdc20. <i>Nature Structural Biology</i> 7, 224–229. <a href="https://doi.org/10.1038/73338" target="_blank" rel="noopener">doi:10.1038/73338</a>.

<a id="reference-4"></a>
4. Luo X, Tang Z, Xia G, Wassmann K, Matsumoto T, Rizo J, Yu H. (PDB 1S2H). (2004). The Mad2 spindle checkpoint protein has two distinct natively folded states. <i>Nature Structural &amp; Molecular Biology</i> 11, 338–345. <a href="https://doi.org/10.1038/nsmb748" target="_blank" rel="noopener">doi:10.1038/nsmb748</a>.

<a id="reference-5"></a>
5. Kalakoti Y, Wallner B. (2025). AFsample2 predicts multiple conformations and ensembles with AlphaFold2. <i>Communications Biology</i> 8, 373. <a href="https://doi.org/10.1038/s42003-025-07791-9" target="_blank" rel="noopener">doi:10.1038/s42003-025-07791-9</a>. <a href="https://github.com/wallnerlab/AFsample2" target="_blank" rel="noopener">https://github.com/wallnerlab/AFsample2</a>.

<a id="reference-6"></a>
6. Jumper J, Evans R, Pritzel A, Green T, Figurnov M, Ronneberger O, Tunyasuvunakool K, Bates R, Žídek A, Potapenko A, Bridgland A, Meyer C, Kohl SAA, Ballard AJ, Cowie A, Romera-Paredes B, Nikolov S, Jain R, Adler J, Back T, Petersen S, Reiman D, Clancy E, Zielinski M, Steinegger M, Pacholska M, Berghammer T, Bodenstein S, Silver D, Vinyals O, Senior AW, Kavukcuoglu K, Kohli P, Hassabis D. (2021). Highly accurate protein structure prediction with AlphaFold. <i>Nature</i> 596, 583–589. <a href="https://doi.org/10.1038/s41586-021-03819-2" target="_blank" rel="noopener">doi:10.1038/s41586-021-03819-2</a>. <a href="https://github.com/google-deepmind/alphafold" target="_blank" rel="noopener">https://github.com/google-deepmind/alphafold</a>.

<a id="reference-7"></a>
7. Kalakoti Y, Wallner B. (2026). AFsample3: generating and selecting multiple conformational states with AlphaFold3. <i>bioRxiv</i>. <a href="https://doi.org/10.64898/2026.01.16.699904" target="_blank" rel="noopener">doi:10.64898/2026.01.16.699904</a>. <a href="https://github.com/wallnerlab/afsample3" target="_blank" rel="noopener">https://github.com/wallnerlab/afsample3</a>.

<a id="reference-8"></a>
8. Abramson J, Adler J, Dunger J, Evans R, Green T, Pritzel A, Ronneberger O, Willmore L, Ballard AJ, Bambrick J, Bodenstein SW, Evans DA, Hung CC, O’Neill M, Reiman D, Tunyasuvunakool K, Wu Z, Žemgulytė A, Arvaniti E, Beattie C, Bertolli O, Bridgland A, Cherepanov A, Congreve M, Cowen-Rivers AI, Cowie A, Figurnov M, Fuchs FB, Gladman H, Jain R, Khan YA, Low CMR, Perlin K, Potapenko A, Savy P, Singh S, Stecula A, Thillaisundaram A, Tong C, Yakneen S, Zhong ED, Zielinski M, Žídek A, Bapst V, Kohli P, Jaderberg M, Hassabis D, Jumper JM. (2024). Accurate structure prediction of biomolecular interactions with AlphaFold 3. <i>Nature</i> 630, 493–500. <a href="https://doi.org/10.1038/s41586-024-07487-w" target="_blank" rel="noopener">doi:10.1038/s41586-024-07487-w</a>. <a href="https://github.com/google-deepmind/alphafold3" target="_blank" rel="noopener">https://github.com/google-deepmind/alphafold3</a>.

<a id="reference-9"></a>
9. Aureka AI OpenDDE project. (2026). Folding, reasoning, and scaling with open-source drug discovery engine. <i>arXiv</i>, 2607.03787. <a href="https://doi.org/10.48550/arXiv.2607.03787" target="_blank" rel="noopener">doi:10.48550/arXiv.2607.03787</a>. <a href="https://github.com/aurekaresearch/OpenDDE" target="_blank" rel="noopener">https://github.com/aurekaresearch/OpenDDE</a>.

<a id="reference-10"></a>
10. Passaro S, Corso G, Wohlwend J, Reveiz M, Thaler S, Somnath VR, Getz N, Portnoi T, Roy J, Stark H, Kwabi-Addo D, Beaini D, Jaakkola T, Barzilay R. (2025). Boltz-2: towards accurate and efficient binding affinity prediction. <i>bioRxiv</i>. <a href="https://doi.org/10.1101/2025.06.14.659707" target="_blank" rel="noopener">doi:10.1101/2025.06.14.659707</a>. <a href="https://github.com/jwohlwend/boltz" target="_blank" rel="noopener">https://github.com/jwohlwend/boltz</a>.

<a id="reference-11"></a>
11. Lewis S, Hempel T, Jiménez-Luna J, Gastegger M, Xie Y, Foong AYK, Satorras VG, Abdin O, Veeling BS, Zaporozhets I, Chen Y, Yang S, Foster AE, Schneuing A, Nigam J, Barbero F, Stimper V, Campbell A, Yim J, Lienen M, Shi Y, Zheng S, Schulz H, Munir U, Sordillo R, Tomioka R, Clementi C, Noé F. (2025). Scalable emulation of protein equilibrium ensembles with generative deep learning. <i>Science</i> 389, eadv9817. <a href="https://doi.org/10.1126/science.adv9817" target="_blank" rel="noopener">doi:10.1126/science.adv9817</a>. <a href="https://github.com/microsoft/bioemu" target="_blank" rel="noopener">https://github.com/microsoft/bioemu</a>.

<a id="reference-12"></a>
12. Microsoft Research AI for Science. (2026). BioEmu2: a foundation model for biomolecular structure and dynamics. <i>Software, BioEmu2-preview v0.1.0rc0</i>. <a href="https://github.com/microsoft/bioemu2" target="_blank" rel="noopener">https://github.com/microsoft/bioemu2</a>. <a href="https://github.com/microsoft/bioemu2/releases/tag/v0.1.0rc0" target="_blank" rel="noopener">v0.1.0rc0 release, 20 October 2026</a>.

<a id="reference-13"></a>
13. McInnes L, Healy J, Melville J. (2018; revised 2020). UMAP: uniform manifold approximation and projection for dimension reduction. <i>arXiv</i>, 1802.03426. <a href="https://doi.org/10.48550/arXiv.1802.03426" target="_blank" rel="noopener">doi:10.48550/arXiv.1802.03426</a>. <a href="https://github.com/lmcinnes/umap" target="_blank" rel="noopener">https://github.com/lmcinnes/umap</a>.

<a id="reference-14"></a>
14. Jolliffe IT, Cadima J. (2016). Principal component analysis: a review and recent developments. <i>Philosophical Transactions of the Royal Society A</i> 374, 20150202. <a href="https://doi.org/10.1098/rsta.2015.0202" target="_blank" rel="noopener">doi:10.1098/rsta.2015.0202</a>.

<a id="reference-15"></a>
15. van der Maaten L, Hinton G. (2008). Visualizing data using t-SNE. <i>Journal of Machine Learning Research</i> 9, 2579–2605. <a href="https://www.jmlr.org/papers/v9/vandermaaten08a.html" target="_blank" rel="noopener">JMLR article</a>. <a href="https://lvdmaaten.github.io/tsne/" target="_blank" rel="noopener">https://lvdmaaten.github.io/tsne/</a>.

<a id="reference-16"></a>
16. de Groot DH, Morillo Leonardo SX, Pachkov M, van Nimwegen E. (2026). Bonsai reconstructs tree representations for distortion-free visualization and exploration of high-dimensional data. <i>Nature Biotechnology</i>, advance online publication. <a href="https://doi.org/10.1038/s41587-026-03220-2" target="_blank" rel="noopener">doi:10.1038/s41587-026-03220-2</a>. <a href="https://doi.org/10.5281/zenodo.20370956" target="_blank" rel="noopener">software doi:10.5281/zenodo.20370956</a>. <a href="https://github.com/dhdegroot/Bonsai-data-representation" target="_blank" rel="noopener">https://github.com/dhdegroot/Bonsai-data-representation</a>.

<a id="reference-17"></a>
17. Zhang C, Shine M, Pyle AM, Zhang Y. (2022). US-align: universal structure alignments of proteins, nucleic acids, and macromolecular complexes. <i>Nature Methods</i> 19, 1109–1115. <a href="https://doi.org/10.1038/s41592-022-01585-1" target="_blank" rel="noopener">doi:10.1038/s41592-022-01585-1</a>. <a href="https://github.com/pylelab/USalign" target="_blank" rel="noopener">https://github.com/pylelab/USalign</a>.

<a id="reference-18"></a>
18. Roney JP, Ovchinnikov S. (2022). State-of-the-art estimation of protein model accuracy using AlphaFold. <i>Physical Review Letters</i> 129, 238101. <a href="https://doi.org/10.1103/PhysRevLett.129.238101" target="_blank" rel="noopener">doi:10.1103/PhysRevLett.129.238101</a>. <a href="https://github.com/jproney/AF2Rank" target="_blank" rel="noopener">https://github.com/jproney/AF2Rank</a>.

<a id="reference-19"></a>
19. Stein RA, Mchaourab HS. (2022). SPEACH_AF: sampling protein ensembles and conformational heterogeneity with AlphaFold2. <i>PLOS Computational Biology</i> 18, e1010483. <a href="https://doi.org/10.1371/journal.pcbi.1010483" target="_blank" rel="noopener">doi:10.1371/journal.pcbi.1010483</a>. <a href="https://github.com/RSvan/SPEACH_AF" target="_blank" rel="noopener">https://github.com/RSvan/SPEACH_AF</a>.

<a id="reference-20"></a>
20. Wayment-Steele HK, Ojoawo A, Otten R, Apitz JM, Pitsawong W, Hömberger M, Ovchinnikov S, Colwell L, Kern D. (2024). Predicting multiple conformations via sequence clustering and AlphaFold2. <i>Nature</i> 625, 832–839. <a href="https://doi.org/10.1038/s41586-023-06832-9" target="_blank" rel="noopener">doi:10.1038/s41586-023-06832-9</a>. <a href="https://github.com/HWaymentSteele/AF_Cluster" target="_blank" rel="noopener">https://github.com/HWaymentSteele/AF_Cluster</a>.

<a id="reference-21"></a>
21. Jing B, Berger B, Jaakkola T. (2024). AlphaFold meets flow matching for generating protein ensembles. <i>Proceedings of Machine Learning Research</i> 235, 22277–22303. <a href="https://proceedings.mlr.press/v235/jing24a.html" target="_blank" rel="noopener">ICML 2024 proceedings</a>. <a href="https://doi.org/10.48550/arXiv.2402.04845" target="_blank" rel="noopener">doi:10.48550/arXiv.2402.04845</a>. <a href="https://github.com/bjing2016/alphaflow" target="_blank" rel="noopener">https://github.com/bjing2016/alphaflow</a>.
