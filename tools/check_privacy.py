#!/usr/bin/env python3
"""Run the unmodified Fleet privacy checker with this project's portable allowlist.

Set FLEET_ROOT to the private Fleet checkout; no machine binding is committed.
Only the explicitly public repository-owner URL is exempt from private user matches.
"""
import importlib.util
import ast
import subprocess
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_OWNER_URL = b"https://github.com/benavt/"
PRIVATE_LOCATION = re.compile(rb"/(?:home|Users)/[^\s\"'<>]+|(?:[a-z0-9-]+[.])+ts[.]net", re.I)
PRIVATE_ADDRESS = re.compile(rb"(?<![0-9.])(?:10[.](?:[0-9]{1,3}[.]){2}[0-9]{1,3}|192[.]168[.][0-9]{1,3}[.][0-9]{1,3}|172[.](?:1[6-9]|2[0-9]|3[01])[.][0-9]{1,3}[.][0-9]{1,3}|100[.](?:6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])[.][0-9]{1,3}[.][0-9]{1,3})(?![0-9.])")

def public_normalized(content):
    return content.replace(PUBLIC_OWNER_URL, b"https://github.com/PUBLIC-OWNER/")

def extra_violations(content):
    errors=[]
    if PRIVATE_LOCATION.search(content): errors.append("private filesystem or tailnet location")
    if PRIVATE_ADDRESS.search(content): errors.append("private network address")
    return errors


def credential_values(directory):
    """Read only known ignored credential files; never expose their contents."""
    directory=Path(directory)
    if any(p.is_symlink() for p in [directory, directory.parent]):
        raise ValueError("Private credential directory must not be a symlink.")
    values=[]
    for name, variable in [("production.env", "ZENODO_ACCESS_TOKEN"), ("sandbox.env", "ZENODO_SANDBOX_TOKEN")]:
        path=directory/name
        if path.is_symlink(): raise ValueError("Private credential file must not be a symlink.")
        if not path.exists(): continue
        for line in path.read_text().splitlines():
            prefix="export "+variable+"="
            if line.startswith(prefix):
                value=ast.literal_eval(line[len(prefix):])
                if isinstance(value,str) and value: values.append(value)
    return values

def project_credentials():
    common=Path(subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=ROOT, text=True).strip())
    if not common.is_absolute(): common=(ROOT/common).resolve()
    return credential_values(common.parent/"local"/"zenodo")

def main():
    fleet_root = os.environ.get("FLEET_ROOT")
    if not fleet_root:
        print("Set FLEET_ROOT to the private Fleet checkout before the privacy gate.", file=sys.stderr)
        return 2
    source = Path(fleet_root).resolve()/"scripts/check_privacy.py"
    spec=importlib.util.spec_from_file_location("fleet_privacy", source)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    values=module.private_values(); secrets=module.notification_secrets()+project_credentials()
    module.ROOT=ROOT
    module.ALLOWED_FILES.update({"LICENSE", "LICENSE-CONTENT.md", "NOTICE.md", "CITATION.cff"})
    module.ALLOWED_DIRS.update({"tools", "src", "config", "poster", "site", "data", "zenodo"})
    module.private_values=lambda: values
    module.notification_secrets=lambda: secrets
    upstream=module.violations
    def inspect(name, content, private_values=(), credential_values=()):
        # Credentials are checked against the original bytes as well as normalized prose.
        errors=upstream(name, public_normalized(content), private_values, credential_values)
        if any(v.encode() in content for v in credential_values):
            errors.append("local notification credential")
        return sorted(set(errors+extra_violations(content)))
    module.violations=inspect
    return module.main()

if __name__ == "__main__":
    raise SystemExit(main())
