import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("production_draft", ROOT / "tools/zenodo_production_draft.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class FakeClient:
    calls = []
    response = {}
    def __init__(self, environment, token=None):
        self.environment = environment
    def url(self, path):
        return "https://zenodo.org" + path
    def call(self, method, path, payload=None, file=None):
        self.calls.append((method, path))
        return self.response


def fake_upstream():
    return SimpleNamespace(Zenodo=FakeClient, DepositError=ValueError, SOURCE_PATHS=[],
                           hashlib=hashlib, canonical=lambda x: json.dumps(x, sort_keys=True).encode(),
                           load=lambda p: json.loads(Path(p).read_text()),
                           save=lambda p, x: Path(p).write_text(json.dumps(x)), main=lambda args: 0)


class ProductionDraftSafety(unittest.TestCase):
    def test_gates_precede_upstream(self):
        for args, env in [(["publish"], {}), (["draft", "--apply"], {}),
                          (["draft", "--apply"], {"ZENODO_ACCESS_TOKEN": "  "}),
                          (["draft", "--ap"], {}), (["draft", "--apply=yes"], {}),
                          (["draft", "--environment", "sandbox"], {}),
                          (["draft", "--environment=sandbox"], {}),
                          (["verify"], {"ZENODO_SANDBOX_TOKEN": "test-only"})]:
            with self.subTest(args=args), patch.dict(os.environ, env, clear=True):
                u = fake_upstream(); calls = []; u.main = lambda a: calls.append(a)
                self.assertEqual(m.main(args, u), 2)
                self.assertEqual(calls, [])

    def test_offline_modes_need_no_token_and_preserve_upstream_entry(self):
        for command in ["plan", "prepare", "verify", "draft"]:
            with self.subTest(command=command), patch.dict(os.environ, {}, clear=True):
                u = fake_upstream(); calls = []; u.main = lambda a: calls.append(a) or 0
                self.assertEqual(m.main([command], u), 0)
                self.assertEqual(calls, [[command, "--environment", "production"]] if command == "draft" else [[command]])
                self.assertEqual(set(u.HOSTS), {"production"})

    def test_client_blocks_publish_and_other_actions_before_base_call(self):
        u = fake_upstream(); client = m.guarded_client(u)("production")
        FakeClient.calls = []
        for method, path in [("POST", "/api/deposit/depositions/1/actions/publish"),
                             ("POST", "/api/deposit/depositions/1/%61ctions/%70ublish"),
                             ("POST", "/api/deposit/depositions/1/actions/newversion"),
                             ("DELETE", "/api/deposit/depositions/1"),
                             ("PUT", "/api/files/bucket/.."),
                             ("GET", "/api/records/1")]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                client.call(method, path)
        self.assertEqual(FakeClient.calls, [])

    def test_allowed_calls_and_authoritative_concept_capture(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "private.concept-doi.json"
            u = fake_upstream(); client = m.guarded_client(u, path)("production")
            FakeClient.calls = []; FakeClient.response = {"id": 42, "conceptrecid": "99", "metadata": {"prereserve_doi": {"doi": "10.5281/example-version"}}}
            client.call("POST", "/api/deposit/depositions", {})
            state = json.loads(path.read_text())
            self.assertIsNone(state["conceptdoi"])
            self.assertEqual(state["status"], "unresolved")
            self.assertEqual(state["version_doi"], "10.5281/example-version")
            FakeClient.response = {"id": 42, "conceptdoi": "10.5281/example-concept"}
            client.call("GET", "/api/deposit/depositions/42")
            client.call("PUT", "/api/deposit/depositions/42", {})
            client.call("PUT", "/api/files/bucket/file.tar.gz", file="mock-file")
            state = json.loads(path.read_text())
            self.assertEqual(state["conceptdoi"], "10.5281/example-concept")
            self.assertEqual(state["version_doi"], "10.5281/example-version")
            self.assertEqual(state["concept_source_field"], "conceptdoi")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_conflicting_concept_or_deposition_stops(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "concept.json"; u = fake_upstream()
            m.capture_concept(u, path, {"id": 1, "conceptdoi": "10.5281/one"}, "GET", "/api/deposit/depositions/1")
            for response in [{"id": 2}, {"id": 1, "conceptdoi": "10.5281/two"}]:
                with self.assertRaises(ValueError):
                    m.capture_concept(u, path, response, "GET", "/api/deposit/depositions/1")


if __name__ == "__main__":
    unittest.main()
