#!/usr/bin/env python3
"""Sandbox-only front door to the pinned upstream deposition implementation.

Never use this wrapper to publish. Offline stages require user-authored metadata;
remote draft writes additionally require explicit approval and a sandbox token.
"""
import importlib.util
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={"plan", "prepare", "verify", "draft"}
SOURCE_ADDITIONS=["tools", "zenodo", "poster", "site", "data", "CITATION.cff", "NOTICE.md", "LICENSE-CONTENT.md"]

def validate(argv, environ):
    if not argv or argv[0] not in ALLOWED:
        raise ValueError("Only plan, prepare, verify and unpublished draft are permitted.")
    exact_flags={"--config", "--repo", "--data-root", "--out", "--package", "--receipt", "--environment", "--apply", "--resume-id", "--help"}
    for value in argv[1:]:
        if value.startswith("--") and value.split("=",1)[0] not in exact_flags:
            raise ValueError("Abbreviated or unknown options are not permitted.")
    if environ.get("ZENODO_ACCESS_TOKEN"):
        raise ValueError("Remove the production token from this process environment.")
    for i, value in enumerate(argv):
        if value.startswith("--environment=") and value != "--environment=sandbox":
            raise ValueError("Only the sandbox environment is permitted.")
        if value == "--environment" and (i+1 == len(argv) or argv[i+1] != "sandbox"):
            raise ValueError("Only the sandbox environment is permitted.")
    if any(a.split("=",1)[0] == "--apply" for a in argv) and (argv[0] != "draft" or not environ.get("ZENODO_SANDBOX_TOKEN")):
        raise ValueError("Approved draft writes require ZENODO_SANDBOX_TOKEN in the private environment.")

def main(argv=None, upstream=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    try:
        validate(argv, os.environ)
    except ValueError as exc:
        print("Sandbox gate: "+str(exc), file=sys.stderr); return 2
    if upstream is None:
        spec=importlib.util.spec_from_file_location("zenodo_upstream", ROOT/"tools/zenodo_deposition.py")
        upstream=importlib.util.module_from_spec(spec); spec.loader.exec_module(upstream)
    upstream.HOSTS={"sandbox":"https://sandbox.zenodo.org"}
    upstream.SOURCE_PATHS=list(dict.fromkeys(upstream.SOURCE_PATHS+SOURCE_ADDITIONS))
    return upstream.main(argv)

if __name__ == "__main__":
    raise SystemExit(main())
