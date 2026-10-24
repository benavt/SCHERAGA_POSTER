# Legacy poster QR-code redirect

The existing `scheraga-poster.netlify.app` landing pages redirect permanently to
`https://benavt.github.io/SCHERAGA_POSTER/`. `_redirects` covers the root,
`index.html`, and the earlier `/poster` entry points. It leaves `/files/`
downloads available at their existing addresses.

Deploy these configuration files **alongside the existing Netlify files**,
not as a replacement containing only this folder. Before the redirect update,
the current deployment archive was preserved. Published content and download
bytes remain unchanged. `netlify.toml` replaces an obsolete absolute publish path
with the ZIP root; `_headers` retains the existing security and cache headers.

Netlify's [redirect syntax](https://docs.netlify.com/manage/routing/redirects/overview/)
and [forced redirect options](https://docs.netlify.com/manage/routing/redirects/redirect-options/)
describe the `301!` rules. The prior deployment remains available for rollback
in Netlify's deploy history. Large deployment archives and verification receipts
remain in the dated, ignored local snapshot.

Verified on 2026-10-24: production deploy `6adc99f2082b70673838fef8`
processed four redirect rules and two header rules. The root, `index.html`,
`/poster`, and `/poster/` return HTTP 301; query parameters are retained.
Following the root reaches the published GitHub Pages poster with HTTP 200.
The existing PDF and PyMOL downloads retain their original SHA-256 checksums.
