# Source provenance and reproducibility

This companion includes selected code and documentation from [Structure_Clustering](https://github.com/benavt/Structure_Clustering), branch `SCHERAGA`, at commit `c75f30ff9524fe11ba76ddd73a96fb80b3004ecf`. The included source can be inspected independently in this repository.

## Included components

- Study documentation, method references and figure conventions.
- Two poster-panel image exports.
- Four original-versus-refold TM scoring and display adapters.
- A helper for printed figure styling and two eleven-method model-label configurations.
- The US-align average-length TM parser, with unrelated medoid dependencies omitted.

The original scoring implementation is retained for historical comparison. Use `score_pairs_v002.py` for the corrected input-format handling, with the required run plan, input files, US-align executable and Python dependencies. This repository does not provide a complete end-to-end reproduction environment or the full interactive analysis application.

## Deposition tools

`tools/zenodo_deposition.py` derives from MIT-licensed source commit `6aee527d69d53f71f9e481b28e3f75efb2974704`. The companion adds wrappers for Sandbox and production drafts, manifest-backed asset selection and local validation. See the [deposition guide](../zenodo/README.md) for supported operations and limitations.

## Scientific assets and attribution

Bulk coordinates, score arrays and model outputs are distributed separately from source code. Portable inventories record identities and hashes; the [distribution status](distribution-status.md) describes which files are publicly available. Source revision identifiers document code provenance and do not establish dataset completeness.

The original source copyright is preserved in [LICENSE](../LICENSE) and [NOTICE.md](../NOTICE.md). Authored content has separate [CC BY 4.0 terms](../LICENSE-CONTENT.md); third-party material retains its own rights and citations.
