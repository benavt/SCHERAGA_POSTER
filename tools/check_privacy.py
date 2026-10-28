#!/usr/bin/env python3
"""Check repository files for credentials, local paths and unsafe artifacts.

By default inspect staged changes. Use --tracked for all indexed files and add
--working-tree to inspect their current working copies instead of Git blobs.
Only Python's standard library and Git are required.
"""
import argparse
import ast
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FILES = {
    '.gitignore', 'README.md', 'CONTRIBUTING.md', 'AGENTS.md',
    'LICENSE', 'LICENSE-CONTENT.md', 'NOTICE.md', 'CITATION.cff',
}
ALLOWED_DIRS = {
    'scripts', 'docs', 'tests', '.githooks', '.github', 'tools', 'src',
    'config', 'poster', 'site', 'data', 'zenodo',
}
PRIVATE_PARTS = {'.git', 'local', '.ssh', '.aws', '.agents', '.codex', '.env', '__pycache__'}
PATTERNS = [
    re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----'),
    re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{20,}\b'),
    re.compile(rb'\bgithub_pat_[A-Za-z0-9_]{30,}\b'),
    re.compile(rb'\bAKIA[A-Z0-9]{16}\b'),
    re.compile(rb'''\b(?:ZENODO_(?:ACCESS|SANDBOX)_TOKEN|API_KEY|API_TOKEN|ACCESS_TOKEN|SECRET_KEY)\b["']?\s*[:=]\s*["']?[A-Za-z0-9_/-]{30,}\b''', re.I),
]
PRIVATE_LOCATION = re.compile(rb"/(?:home|Users)/[^\s\"'<>]+|(?:[a-z0-9-]+[.])+ts[.]net", re.I)
PRIVATE_ADDRESS = re.compile(rb"(?<![0-9.])(?:10[.](?:[0-9]{1,3}[.]){2}[0-9]{1,3}|192[.]168[.][0-9]{1,3}[.][0-9]{1,3}|172[.](?:1[6-9]|2[0-9]|3[01])[.][0-9]{1,3}[.][0-9]{1,3}|100[.](?:6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])[.][0-9]{1,3}[.][0-9]{1,3})(?![0-9.])")
# Private hostnames: case-insensitive match for whole words and embedded forms (e.g., Mimas_Folding_Skills).
# Excluded from binary/compressed assets and protein data files to avoid false positives in encoded data.
PRIVATE_HOSTNAME = re.compile(rb'\b(?:pax|mimas)(?:[_-][a-z0-9]+)*\b', re.I)


def extra_violations(content, name):
    errors = []
    if PRIVATE_LOCATION.search(content):
        errors.append('local filesystem or tailnet location')
    if PRIVATE_ADDRESS.search(content):
        errors.append('private network address')
    # Check for private hostnames, but exclude:
    # - Binary/compressed assets and protein data (false positives from encoded bytes)
    # - Test files and the checker itself (intentional test data and pattern definitions)
    path = Path(name)
    if (path.suffix.lower() not in {'.pdf', '.zip', '.gz', '.tar', '.pdb', '.cif', '.mmcif', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.webm'}
            and not name.startswith('tests/')
            and name != 'tools/check_privacy.py'):
        if PRIVATE_HOSTNAME.search(content):
            errors.append('private hostname')
    return errors


def violations(name, content, credential_values=()):
    path = Path(name)
    errors = extra_violations(content, name)
    if name not in ALLOWED_FILES and (len(path.parts) < 2 or path.parts[0] not in ALLOWED_DIRS):
        errors.append('path outside public-content allowlist')
    if (path.is_absolute() or '..' in path.parts
            or any(part.lower() in PRIVATE_PARTS for part in path.parts)
            or path.name.startswith(('id_', '.env'))
            or path.suffix.lower() in {'.pem', '.key', '.p12'}):
        errors.append('private artifact path')
    if any(pattern.search(content) for pattern in PATTERNS):
        errors.append('credential pattern')
    if any(value.encode() in content for value in credential_values if value):
        errors.append('local credential value')
    return sorted(set(errors))


def credential_values(directory):
    """Read only known ignored credential files; never expose their contents."""
    directory = Path(directory)
    if any(p.is_symlink() for p in [directory, directory.parent]):
        raise ValueError('Private credential directory must not be a symlink.')
    values = []
    for name, variable in [('production.env', 'ZENODO_ACCESS_TOKEN'), ('sandbox.env', 'ZENODO_SANDBOX_TOKEN')]:
        path = directory / name
        if path.is_symlink():
            raise ValueError('Private credential file must not be a symlink.')
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            prefix = 'export ' + variable + '='
            if line.startswith(prefix):
                try:
                    value = ast.literal_eval(line[len(prefix):])
                except (ValueError, SyntaxError):
                    raise ValueError('Cannot parse private credential assignment; value withheld.') from None
                if isinstance(value, str) and value:
                    values.append(value)
    return values


def project_credentials():
    common = Path(subprocess.check_output(['git', 'rev-parse', '--git-common-dir'], cwd=ROOT, text=True).strip())
    if not common.is_absolute():
        common = (ROOT / common).resolve()
    values = credential_values(common.parent / 'local' / 'zenodo')
    values.extend(os.environ[key] for key in ('ZENODO_ACCESS_TOKEN', 'ZENODO_SANDBOX_TOKEN') if os.environ.get(key))
    return values


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracked', action='store_true', help='inspect all indexed files, not just staged changes')
    parser.add_argument('--working-tree', action='store_true', help='read working copies rather than index content')
    args = parser.parse_args(argv)
    command = (['git', 'ls-files', '-z'] if args.tracked else
               ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z'])
    try:
        names = subprocess.check_output(command, cwd=ROOT).decode().split('\0')
        secrets = project_credentials()
        failed = False
        for name in filter(None, names):
            mode = subprocess.check_output(['git', 'ls-files', '-s', '--', name], cwd=ROOT).decode().split()[0]
            path = ROOT / name
            if mode in {'120000', '160000'} or (args.working_tree and path.is_symlink()):
                errors = ['symlink or external repository cannot be published']
            else:
                content = (path.read_bytes() if args.working_tree else
                           subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT))
                errors = violations(name, content, secrets)
            if errors:
                failed = True
                print(name + ': ' + ', '.join(errors), file=sys.stderr)
        if failed:
            print('Privacy check failed. Remove flagged content before publication.', file=sys.stderr)
            return 1
    except (OSError, ValueError, subprocess.CalledProcessError):
        print('Privacy check could not read repository files or local credential configuration; values withheld.', file=sys.stderr)
        return 2
    print('Privacy check passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
