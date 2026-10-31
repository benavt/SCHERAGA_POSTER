# Reproducible virtual-poster source

The current offline export is indexed in `latest-preview.json`. Large generated
HTML files remain in ignored `local/`; the repository contains the small source,
font files, exact matrix figures and their provenance manifests. The builder
never publishes, makes network requests or overwrites an existing output.

The presentation puts research first: black and white, a restrained RPI red
(`#D6001C`) rule and active navigation, and original scientific plot colors.
A compact 34px navigation row and 36px playback toolbar serve phones and tablets. At widths of 700px or
more, the movie structure and featured projection appear side by side. A rotated
phone uses the remaining viewport for that pair; legends, thumbnails and model
metadata follow below. Native selectors call the original metric/palette handlers.

This treatment follows the official RPI [color](https://brand.rpi.edu/d/pfJS6BKVKBeq/brand-guidelines#/-/color),
[typography](https://brand.rpi.edu/d/pfJS6BKVKBeq/brand-guidelines#/-/typography)
and [design principles](https://brand.rpi.edu/d/pfJS6BKVKBeq/brand-guidelines#/-/design-principles):
academic content leads, branding provides a quiet frame, and hierarchy supports
navigation. The original open-source Geist fonts are used with the documented
letterform alternates; they are not represented as the custom RPI font files.
Two variable WOFF2 files from official
[Geist commit 75d6470](https://github.com/vercel/geist-font/tree/75d647056bcbd9eaba3a14b1b58290d0692685d6)
are embedded for offline use. `fonts/manifest.json` pins source URLs, hashes and
OpenType settings. `fonts/OFL.txt` is also embedded in the HTML license template.
Geist is used for prose and controls; Geist Mono is used for technical data.

Each protein has exactly two TM figures: its original full cluster/reference
matrix and the verified four-state matrix. The four-state source PNGs are byte
identical to the final v014 poster assets; this provenance is recorded in
`assets/2026-10-23_poster-tm/manifest.json`. Their visible title is **Selected
states and references**. S1/S2 were selected by reference similarity and are not
necessarily medoids, so the four-state figure is not described as a mathematical
subset of the full matrix. Four older Mad2 display crops are removed. No metric
is recomputed. Clicking either matrix opens the existing image viewer with a
1100px image surface that can pan horizontally on a phone.

## Reproduce the v036 design predecessor

Run from the repository root. `PSE_V010` and `GUIDE_V010` below should point to the
validated immutable v010 files, named respectively
`2026-10-23_Scheraga_four_comparisons_poster_Adk_v010.pse` and
`2026-10-23_PyMOL-quick-guide_v010.txt`. This keeps host-specific locations outside
tracked source. The Mac working-copy snapshots use `local/` directly; canonical
local exports use `local/site-exports/`.

```sh
python3 site/virtual-poster/build_preview.py \
  --source local/site-exports/doi-update_001/SCHERAGA_virtual_poster_published_DOIs_v025.html \
  --design-predecessor local/site-exports/2026-10-23_tm-comparison_001/SCHERAGA_virtual_poster_design_polish_v035.html \
  --poster-figures site/virtual-poster/assets/2026-10-23_poster-tm/manifest.json \
  --pymol-session "$PSE_V010" \
  --pymol-guide "$GUIDE_V010" \
  --pymol-sha256 67dfb349c61b24403a33a98a66f10df39fe9ed6fa67db03e9e4d094c9093a107 \
  --guide-sha256 90022331e3c24286d8bff6e3da7c536650fd653e42701d9766b0c1585d3c2e84 \
  --output local/site-exports/2026-10-23_tm-comparison_001/SCHERAGA_virtual_poster_design_polish_v036.html
```

The final export requires the v010 session and guide. Omitting them is supported
only for interim design QA and retains the older payload and mismatch note.
The output's `.sources/` directory preserves exact source inputs, and its
`.validation.json` records hashes, the predecessor relationship and source checks.
All sixteen original script blocks and all four scientific JSON blocks remain
byte identical to the pinned v025 source. Every retained pre-existing data URI
is checked in order; only the verified session/guide substitutions, four display
crop removals, two exact matrix additions and two font additions are allowed.
The embedded PDF and all other images and scientific payloads remain unchanged.

Source checks do not establish rendered quality. Browser QA additionally checks
portrait phone, landscape phone, tablet and desktop layouts, playback/frame
seeking, all metric and palette choices, matrix zoom and downloads. Create a new
date-first immutable run when inputs or scientific settings change.

## Match physical-poster reference colors (v037)

`reference-colors.json` records the final v014 palette: **open blue
`#1f77b4`** (4AKE and 1DUJ), **closed orange `#ff7f0e`** (1AKE and 1S2H).
The renderer uses these colors for projection stars, labels, legends and Bonsai
reference overlays regardless of the selected prediction-color metric.

After reproducing v036 above, create the current export:

```sh
python3 site/virtual-poster/match_reference_colors.py \
  --input local/site-exports/2026-10-23_tm-comparison_001/SCHERAGA_virtual_poster_design_polish_v036.html \
  --output local/site-exports/2026-10-24_reference-colors_002/SCHERAGA_virtual_poster_reference_colors_v037.html
```

The transformer verifies the v036 and physical-poster hashes, changes exactly
four reference display-color fields and the two reference fills in each Bonsai
SVG (both dashboard and supporting-figure copies). Restoring those colors
reproduces the original HTML byte for byte. Executable scripts, other media,
coordinates, scores, prediction colors and red navigation styling stay identical.
Prior versioned exports and releases remain available.

## Package a smaller static website

`package_web.py` converts the frozen v037 offline HTML to a buildless static
bundle. It replaces only literal base64 data URIs with relative, content-addressed
asset paths. Every asset's decoded bytes remain identical; replacing those paths
with the original URIs must reproduce the offline file byte for byte. The offline
release remains unchanged.

```sh
python3 site/virtual-poster/package_web.py \
  --input local/site-exports/2026-10-24_reference-colors_002/SCHERAGA_virtual_poster_reference_colors_v037.html \
  --expected-sha256 ac1df9d5dd3851f4100a91fd70e8bbef6165b54a51299234eb615ab97d9081c2 \
  --version web-v002 --release-date 2026-10-24 \
  --output-dir local/site-exports/2026-10-24_static-web_002
```

Use a new output directory for a new run; the packager refuses to overwrite an
existing directory. The output contains `site/index.html`, `.nojekyll`,
`assets/`, and `asset-manifest.json`, plus an immutable release ZIP. The manifest's
`files` array lists the path, byte count and SHA256 of every served file except
the manifest itself; the ZIP hash authenticates that manifest. ZIP members are
regular files only. Provenance, the URI map, source snapshot and validation stay
outside the public ZIP.

The first web bundle has a 10.56 MB index (1.96 MB gzipped), 423 deduplicated
assets, and a 53.49 MB ZIP. It externalizes 425 URI occurrences. The existing
runtime accepts ordinary URLs through `Image.src` and anchor `href`, and contains
no data-URI-only decoder. Frame images still use the original preload behavior;
GIF/MP4/PDF/PyMOL downloads no longer travel inside the initial HTML response.
This packaging step changes no scientific calculations, model order, metrics,
coordinates, text or event handlers. Browser QA remains necessary to verify
network loading, playback, palette changes, figure enlargement and downloads.
