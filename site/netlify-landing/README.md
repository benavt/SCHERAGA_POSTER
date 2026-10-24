# Poster QR-code landing page

The poster QR code opens `https://scheraga-poster.netlify.app/`. Keep this
landing page available at the root. Its **Virtual poster** link opens
`https://benavt.github.io/SCHERAGA_POSTER/`; the PDF, Zenodo, PyMOL and source
links remain visible. Only the earlier `/poster` entry points redirect.

Deploy these files alongside the existing `files/` downloads and `poster/`
folder. The large original deployment and the corrected upload ZIP are preserved
in ignored, dated local snapshots. `netlify.toml` uses the deployment root;
`_headers` retains the existing security and cache headers.

The 2026-10-24 update enables the virtual-poster link, updates the completed Adk
record notice and corrects the two download links to match the deployed filename
case. Download bytes remain unchanged. The earlier root redirect was removed
after the user clarified that the Netlify landing page must remain visible.
