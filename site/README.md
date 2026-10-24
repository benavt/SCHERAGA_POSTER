# Interactive poster

The interactive poster presents the two proteins through linked structural views, plots and observed-model movies. It includes the study abstract, experimental reference structures, model confidence and structural-similarity comparisons.

**Available on GitHub Pages:** [open the interactive poster](https://benavt.github.io/SCHERAGA_POSTER/). The standalone v036 export includes compact phone and tablet navigation, linked structural and clustering views, and complete and selected-state TM-score matrices. Download the HTML for offline use from the [versioned release](https://github.com/benavt/SCHERAGA_POSTER/releases/tag/2026-10-23_virtual-poster-v036). The self-contained file is approximately 89 MB, including media and companion downloads.

The interactive export includes PCA, UMAP and t-SNE projections, Bonsai structural trees and synchronized molecular views. Its movies show ordered examples of observed predictions; they do not represent measured molecular motion or transition timing.

The website is static HTML/CSS/JavaScript with media served as separate files, so the initial page does not include every downloadable GIF, movie, PDF and PyMOL session. Its HTML is approximately 2 MB compressed; the original frame images still preload in the background. Small, reproducible presentation sources are in [virtual-poster](virtual-poster/README.md). The manual Pages workflow verifies the [static bundle](https://github.com/benavt/SCHERAGA_POSTER/releases/tag/2026-10-23_virtual-poster-web-v001) and every packaged file against [the publication manifest](virtual-poster/publication.json) before deployment. See [resource availability](../docs/distribution-status.md) and the [artifact inventory](../docs/SCHERAGA-downloads.json).
