import importlib.util
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    s=importlib.util.spec_from_file_location(name, ROOT/"tools"/(name+".py"))
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

class Safety(unittest.TestCase):
    def test_remote_gates_precede_upstream(self):
        m=load("zenodo_sandbox")
        for args,env in [(["publish"],{}),(["draft","--environment","production"],{}),(["draft","--environment=production"],{}),(["draft","--apply"],{}),(["draft","--ap"],{}),(["verify"],{"ZENODO_ACCESS_TOKEN":"test-only"})]:
            with self.subTest(args=args),patch.dict(os.environ,env,clear=True):
                calls=[]
                u=SimpleNamespace(SOURCE_PATHS=[],main=lambda a:calls.append(a))
                self.assertEqual(m.main(args,u),2); self.assertEqual(calls,[])
    def test_offline_requires_no_token(self):
        m=load("zenodo_sandbox"); calls=[]
        u=SimpleNamespace(SOURCE_PATHS=[],main=lambda a:calls.append(a) or 0)
        with patch.dict(os.environ,{},clear=True): self.assertEqual(m.main(["verify"],u),0)
        self.assertEqual(calls,[["verify"]]); self.assertEqual(set(u.HOSTS),{"sandbox"})
    def test_private_project_credentials_are_available_to_exact_match_gate(self):
        m=load("check_privacy")
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/"local"/"zenodo";root.mkdir(parents=True)
            (root/"production.env").write_text("export ZENODO_ACCESS_TOKEN='private-canary-value'\n")
            self.assertEqual(m.credential_values(root),["private-canary-value"])
            (root/"production.env").write_text("export ZENODO_ACCESS_TOKEN=private-canary-value\n")
            with self.assertRaises(ValueError) as error:m.credential_values(root)
            self.assertNotIn("private-canary-value",str(error.exception))
            (root/"sandbox.env").symlink_to(root/"production.env")
            with self.assertRaises(ValueError):m.credential_values(root)

    def test_locations_and_public_attribution(self):
        m=load("check_privacy")
        for value in [b"/"+b"home"+b"/private-user/data", b"192"+b".168.1.23", b"private-node"+b".ts.net"]:
            self.assertTrue(m.extra_violations(value, "docs/test.md"))
        self.assertEqual([],m.violations("README.md",b"https://github.com/example/poster"))

if __name__=="__main__": unittest.main()
