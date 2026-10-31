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
import shutil
import subprocess
import sys
import tempfile

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
# Private hostnames: case-insensitive match for whole words and embedded forms.
# PDFs are inspected via extracted text rather than raw bytes. Truly opaque media is skipped.
# Build pattern from fragments to avoid literal occurrence
# Use custom boundaries (?<![a-z0-9]) / (?![a-z0-9]) so underscore and hyphen act as separators.
# This matches X_<name>_Y, <Name>_Folding_Skills, <name>-x but not 'paxos' or 'compax'.
_h1 = 'p' + 'ax'
_h2 = 'm' + 'imas'
PRIVATE_HOSTNAME = re.compile(rb'(?<![a-z0-9])(?:' + _h1.encode() + rb'|' + _h2.encode() + rb')(?:[_-][a-z0-9]+)*(?![a-z0-9])', re.I)


def check_poppler_utils():
    """Verify poppler-utils (pdftotext, pdfdetach) is available. Fail loudly if missing."""
    if not shutil.which('pdftotext') or not shutil.which('pdfdetach'):
        raise RuntimeError(
            'poppler-utils (pdftotext, pdfdetach) is required for PDF inspection but not found. '
            'Install it in CI or locally: apt-get install poppler-utils'
        )


def extract_pdf_text(pdf_path):
    """Extract visible text from a PDF using pdftotext. Returns bytes."""
    try:
        result = subprocess.run(
            ['pdftotext', '-enc', 'UTF-8', str(pdf_path), '-'],
            capture_output=True,
            check=True,
            timeout=10
        )
        return result.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        # If extraction fails, treat as suspicious rather than passing blindly
        raise ValueError(f'PDF text extraction failed for {pdf_path}: {e}')


def extract_pdf_attachments(pdf_path):
    """Extract and return content of all embedded attachments from a PDF. Returns list of (name, bytes)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        # List attachments first
        try:
            list_result = subprocess.run(
                ['pdfdetach', '-list', str(pdf_path)],
                capture_output=True,
                check=False,
                timeout=5
            )
            # If no attachments, pdfdetach returns non-zero but that's fine
            if b'file' not in list_result.stdout.lower():
                return []
        except subprocess.TimeoutExpired:
            raise ValueError(f'PDF attachment listing timed out for {pdf_path}')
        
        # Extract all attachments
        try:
            subprocess.run(
                ['pdfdetach', '-saveall', '-o', str(tmpdir_path), str(pdf_path)],
                capture_output=True,
                check=False,  # Non-zero exit if no attachments is normal
                timeout=10
            )
        except subprocess.TimeoutExpired:
            raise ValueError(f'PDF attachment extraction timed out for {pdf_path}')
        
        # Read all extracted files
        attachments = []
        for attachment_file in tmpdir_path.iterdir():
            if attachment_file.is_file():
                attachments.append((attachment_file.name, attachment_file.read_bytes()))
        return attachments


def inspect_pdf(content, name):
    """Inspect a PDF by extracting and scanning visible text and embedded attachments."""
    # Write content to temporary file for pdftotext/pdfdetach
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    
    try:
        errors = []
        
        # Extract and scan visible text
        try:
            text = extract_pdf_text(tmp_path)
            if PRIVATE_LOCATION.search(text):
                errors.append('local filesystem or tailnet location')
            if PRIVATE_ADDRESS.search(text):
                errors.append('private network address')
            if PRIVATE_HOSTNAME.search(text):
                errors.append('private hostname')
        except ValueError as e:
            # Extraction failure is suspicious
            errors.append(f'PDF inspection failed: {e}')
        
        # Extract and scan embedded attachments
        try:
            attachments = extract_pdf_attachments(tmp_path)
            for att_name, att_content in attachments:
                if PRIVATE_LOCATION.search(att_content):
                    errors.append(f'local filesystem or tailnet location in attachment {att_name}')
                if PRIVATE_ADDRESS.search(att_content):
                    errors.append(f'private network address in attachment {att_name}')
                if PRIVATE_HOSTNAME.search(att_content):
                    errors.append(f'private hostname in attachment {att_name}')
        except ValueError as e:
            errors.append(f'PDF attachment inspection failed: {e}')
        
        return errors
    finally:
        tmp_path.unlink(missing_ok=True)


def extract_archive_members(content, name):
    """Extract and return members of zip/tar/gz archives for scanning. Returns list of (member_name, bytes)."""
    path = Path(name)
    members = []
    
    # Archive extraction failures should be reported as violations, not silently passed
    try:
        if path.suffix.lower() == '.zip':
            import zipfile
            import io
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    for member in zf.namelist():
                        if not member.endswith('/'):  # Skip directories
                            try:
                                members.append((member, zf.read(member)))
                            except Exception as e:
                                raise ValueError(f'Cannot read archive member {member}: {e}')
            except zipfile.BadZipFile as e:
                raise ValueError(f'Corrupt or invalid zip archive: {e}')
        elif path.suffix.lower() in {'.tar', '.gz', '.tgz'}:
            import tarfile
            import io
            # Handle both .tar and .tar.gz/.tgz
            mode = 'r:gz' if path.suffix.lower() in {'.gz', '.tgz'} or name.endswith('.tar.gz') else 'r'
            try:
                with tarfile.open(fileobj=io.BytesIO(content), mode=mode) as tf:
                    for member in tf.getmembers():
                        if member.isfile():
                            try:
                                extracted = tf.extractfile(member)
                                if extracted:
                                    members.append((member.name, extracted.read()))
                                else:
                                    raise ValueError(f'Cannot extract archive member {member.name}')
                            except Exception as e:
                                raise ValueError(f'Cannot read archive member {member.name}: {e}')
            except tarfile.TarError as e:
                raise ValueError(f'Corrupt or invalid tar archive: {e}')
    except ValueError:
        # Re-raise ValueError (our explicit errors)
        raise
    except Exception as e:
        # Any other unexpected error should also be reported
        raise ValueError(f'Archive extraction failed: {e}')
    
    return members


def extract_printable_ascii_runs(content, min_length=4):
    """Extract printable ASCII runs of at least min_length from binary content.
    Similar to 'strings' command - extracts text from binary data like PNG metadata.
    Returns bytes containing only the extracted runs separated by newlines."""
    import string
    # Create a set of printable ASCII byte values (integers)
    printable_bytes = set(string.printable.encode('ascii'))
    runs = []
    current_run = bytearray()
    
    for byte in content:
        if byte in printable_bytes:
            current_run.append(byte)
        else:
            if len(current_run) >= min_length:
                runs.append(bytes(current_run))
            current_run = bytearray()
    
    # Don't forget the last run
    if len(current_run) >= min_length:
        runs.append(bytes(current_run))
    
    return b'\n'.join(runs)


def scan_content_safely(content, name):
    """Scan content for violations, handling binary data gracefully. Returns list of errors."""
    errors = []
    
    path = Path(name)
    
    # For genuinely opaque binary formats (images, video), extract printable ASCII runs
    # like 'strings' to scan metadata (PNG tEXt/EXIF/XMP, etc.) without false positives
    if path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico', 
                                '.mp4', '.webm', '.avi', '.mov', '.mkv'}:
        # Extract printable ASCII strings of length >=4 from binary content
        printable_content = extract_printable_ascii_runs(content, min_length=4)
        
        # Scan the extracted strings for violations
        if PRIVATE_LOCATION.search(printable_content):
            errors.append('local filesystem or tailnet location')
        if PRIVATE_ADDRESS.search(printable_content):
            errors.append('private network address')
        if PRIVATE_HOSTNAME.search(printable_content):
            errors.append('private hostname')
        
        return errors
    
    # For text files and other content, scan directly
    if PRIVATE_LOCATION.search(content):
        errors.append('local filesystem or tailnet location')
    if PRIVATE_ADDRESS.search(content):
        errors.append('private network address')
    if PRIVATE_HOSTNAME.search(content):
        errors.append('private hostname')
    
    return errors


def extra_violations(content, name):
    errors = []
    
    path = Path(name)
    
    # PDFs are inspected via extracted text and attachments rather than raw bytes
    if path.suffix.lower() == '.pdf':
        try:
            check_poppler_utils()
            return inspect_pdf(content, name)
        except RuntimeError as e:
            # Missing tools - fail loudly rather than silently passing
            raise
    
    # Exclude specific test files that contain intentional fake fixtures and the checker itself
    # from location/address/hostname checks
    if name in {'tests/test_privacy.py', 'tools/check_privacy.py'}:
        return errors
    
    # Extract and scan archive members (zip, tar, gz)
    if path.suffix.lower() in {'.zip', '.tar', '.gz', '.tgz'} or name.endswith('.tar.gz'):
        try:
            members = extract_archive_members(content, name)
            for member_name, member_content in members:
                member_errors = scan_content_safely(member_content, member_name)
                for error in member_errors:
                    errors.append(f'{error} in archive member {member_name}')
            # Also scan the archive itself (in case of embedded metadata)
            # but only if extraction succeeded
            if members:
                return errors
        except ValueError as e:
            # Archive corruption or unreadable members are violations
            errors.append(f'archive inspection failed: {e}')
            return errors
    
    # Standard scanning for all other files (including .pdb, .cif, .mmcif which are plain text)
    errors.extend(scan_content_safely(content, name))
    
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
