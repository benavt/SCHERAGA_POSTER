import importlib.util
import os
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
    def test_locations_and_public_owner(self):
        m=load("check_privacy")
        for value in [b"/"+b"home"+b"/private-user/data", b"192"+b".168.1.23", b"private-node"+b".ts.net"]:
            self.assertTrue(m.extra_violations(value))
        self.assertEqual(b"https://github.com/PUBLIC-OWNER/SCHERAGA_POSTER",m.public_normalized(b"https://github.com/benavt/SCHERAGA_POSTER"))
        self.assertIn(b"private-user",m.public_normalized(b"private-user"))

if __name__=="__main__": unittest.main()
