#!/usr/bin/env python3
"""Production drafts only; publication and action endpoints are prohibited."""
import importlib.util
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"plan", "prepare", "verify", "draft"}
FLAGS = {"--config", "--repo", "--data-root", "--out", "--package", "--receipt",
         "--environment", "--apply", "--resume-id", "--help"}
SOURCE_ADDITIONS = ["tools", "zenodo", "poster", "site", "data", "CITATION.cff", "NOTICE.md", "LICENSE-CONTENT.md"]


def validate(argv, environ):
    if not argv or argv[0] not in ALLOWED:
        raise ValueError("Only plan, prepare, verify and unpublished draft are permitted.")
    for value in argv[1:]:
        if value.startswith("-") and value.split("=", 1)[0] not in FLAGS:
            raise ValueError("Abbreviated or unknown options are not permitted.")
        if value.startswith(("--apply=", "--help=")):
            raise ValueError("Boolean flags do not accept values.")
    if environ.get("ZENODO_SANDBOX_TOKEN"):
        raise ValueError("Remove the Sandbox token from this production process environment.")
    for i, value in enumerate(argv):
        if value.startswith("--environment=") and value != "--environment=production":
            raise ValueError("Only the production environment is permitted.")
        if value == "--environment" and (i + 1 == len(argv) or argv[i + 1] != "production"):
            raise ValueError("Only the production environment is permitted.")
    if "--apply" in argv:
        if argv[0] != "draft" or not environ.get("ZENODO_ACCESS_TOKEN", "").strip():
            raise ValueError("Applied production drafts require ZENODO_ACCESS_TOKEN in a protected environment.")


def option(argv, flag):
    for i, value in enumerate(argv):
        if value == flag and i + 1 < len(argv):
            return argv[i + 1]
        if value.startswith(flag + "="):
            return value.split("=", 1)[1]
    return None


def guarded_client(upstream, sidecar=None):
    base = upstream.Zenodo

    class ProductionDraftClient(base):
        def __init__(self, environment, token=None):
            if environment != "production":
                raise upstream.DepositError("Only production drafts are permitted.")
            super().__init__(environment, token=token)

        def call(self, method, path, payload=None, file=None):
            # Guard before the base implementation constructs any HTTP request.
            url = self.url(path)
            clean = urlsplit(url).path
            for _ in range(3):
                clean = unquote(clean)
            allowed = (
                (method == "GET" and re.fullmatch(r"/api/deposit/depositions/\d+", clean))
                or (method == "POST" and clean == "/api/deposit/depositions")
                or (method == "PUT" and re.fullmatch(r"/api/deposit/depositions/\d+", clean))
                or (method == "PUT" and re.fullmatch(r"/api/files/[A-Za-z0-9-]+/[^/]+", clean))
            )
            if not allowed or "/actions/" in clean or any(p in {".", ".."} for p in clean.split("/")):
                raise upstream.DepositError("Production draft client blocks this HTTP operation.")
            result = super().call(method, path, payload=payload, file=file)
            if sidecar is not None and isinstance(result, dict) and clean.startswith("/api/deposit/depositions"):
                capture_concept(upstream, Path(sidecar), result, method, clean)
            return result

    return ProductionDraftClient


def capture_concept(upstream, path, response, method, endpoint):
    """Persist only explicit server DOI fields; record IDs never imply a DOI."""
    previous = upstream.load(path) if path.exists() else {}
    if previous and previous.get("environment") != "production":
        raise upstream.DepositError("Concept sidecar environment differs.")
    response_id = response.get("id")
    if previous.get("deposition_id") is not None and response_id is not None and previous["deposition_id"] != response_id:
        raise upstream.DepositError("Concept sidecar belongs to a different deposition.")
    concept = response.get("conceptdoi")
    if concept is not None and (not isinstance(concept, str) or not re.fullmatch(r"10\.\d{4,9}/\S+", concept)):
        raise upstream.DepositError("Invalid authoritative concept DOI field.")
    if concept and previous.get("conceptdoi") and previous["conceptdoi"] != concept:
        raise upstream.DepositError("Authoritative concept DOI changed; inspect before resuming.")
    version = response.get("metadata", {}).get("prereserve_doi", {}).get("doi") or response.get("doi")
    state = {**previous, "schema_version": 1, "environment": "production",
             "deposition_id": response_id if response_id is not None else previous.get("deposition_id"),
             "conceptdoi": concept or previous.get("conceptdoi"),
             "version_doi": version or previous.get("version_doi"),
             "status": "concept-doi-returned" if concept or previous.get("conceptdoi") else "unresolved",
             "latest_response_method": method, "latest_response_endpoint": endpoint,
             "latest_response_sha256": upstream.hashlib.sha256(upstream.canonical(response)).hexdigest()}
    if concept:
        state.update(concept_source_field="conceptdoi", concept_source_endpoint=endpoint,
                     concept_source_response_sha256=state["latest_response_sha256"])
    path.parent.mkdir(parents=True, exist_ok=True)
    upstream.save(path, state)
    path.chmod(0o600)


def main(argv=None, upstream=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        validate(argv, os.environ)
    except ValueError as exc:
        print("Production draft gate: " + str(exc), file=sys.stderr)
        return 2
    if upstream is None:
        spec = importlib.util.spec_from_file_location("zenodo_upstream_production_draft", ROOT / "tools/zenodo_deposition.py")
        upstream = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(upstream)
    upstream.HOSTS = {"production": "https://zenodo.org"}
    upstream.SOURCE_PATHS = list(dict.fromkeys(upstream.SOURCE_PATHS + SOURCE_ADDITIONS))
    config_path = option(argv, "--config")
    if argv[0] in {"plan", "prepare"} and config_path:
        try:
            config = upstream.load(config_path)
            if any(isinstance(a, dict) and "manifest" in a for a in config.get("assets", [])):
                adapter_spec = importlib.util.spec_from_file_location("zenodo_manifest_assets", ROOT / "tools/zenodo_manifest_assets.py")
                adapter_module = importlib.util.module_from_spec(adapter_spec)
                adapter_spec.loader.exec_module(adapter_module)
                adapter_module.install(upstream, config_path)
        except (OSError, ValueError, TypeError, KeyError):
            print("Production draft gate: Cannot load manifest asset configuration.", file=sys.stderr)
            return 2
    sidecar = None
    if argv[0] == "draft":
        if option(argv, "--environment") is None:
            argv += ["--environment", "production"]
        receipt = option(argv, "--receipt")
        if "--apply" in argv and receipt:
            sidecar = str(receipt) + ".concept-doi.json"
    upstream.Zenodo = guarded_client(upstream, sidecar)
    # The unmodified upstream still enforces exact package/tag/published-release gates.
    return upstream.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
