#!/usr/bin/env python3
"""Release-pinned research deposits: offline packages, resumable drafts, explicit publish.

Only the Python standard library is required. Nothing executes scientific stages.
"""
import argparse
import copy
import datetime as dt
import gzip
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {'sandbox': 'https://sandbox.zenodo.org', 'production': 'https://zenodo.org'}
ROLES = {'inputs', 'outputs', 'reports', 'provenance'}
SOURCE_PATHS = ['src', 'scripts', 'config', 'docs', 'README.md', 'LICENSE',
                'project.json', '.gitmodules', 'requirements.txt', 'requirements-linux.txt',
                'environment-portable.yml', 'patches', 'tests', 'structure', 'Sequence.py',
                'expand.py', 'paths.py', 'util.py', 'setup.py', 'workflow.lock.json',
                'pytest.ini', '.github', '.githooks', '.gitignore', '.gitattributes', 'AGENTS.md']
SECRET_PARTS = {'.git', '.ssh', '.aws', '.env', 'access_token', 'credentials',
                'credentials.json', 'token', 'secrets', '.codex', '.cursor'}


class DepositError(ValueError):
    pass


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    """Atomic private receipt writes survive interrupted network operations."""
    path = Path(path)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(canonical(value)); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def digest(path, algorithm='sha256'):
    result = hashlib.new(algorithm)
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''): result.update(block)
    return result.hexdigest()


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if result.returncode:
        raise DepositError('Git lookup failed: ' + ' '.join(args[:2]))
    return result.stdout.decode().strip()


def relative(value):
    if (not isinstance(value, str) or not value or '\\' in value
            or any(ord(c) < 32 for c in value)):
        raise DepositError('Expected a safe relative POSIX path')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value or value == '.':
        raise DepositError('Expected a normalized relative path: ' + value)
    return path


def public_path(value):
    parts = relative(value).parts
    if any(p.lower() in SECRET_PARTS or p.lower().startswith('.env')
           or p.lower().endswith(('.pem', '.key')) for p in parts):
        raise DepositError('Credential/private path cannot be deposited: ' + value)


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise DepositError('Fill in ' + field)
    if re.search(r'placeholder|replace[_ -]?me|\bTODO\b', value, re.I):
        raise DepositError('Unresolved placeholder in ' + field)
    return value.strip()


def valid_orcid(value):
    if not re.fullmatch(r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]', value): return False
    total = 0
    for c in value.replace('-', '')[:-1]: total = (total + int(c)) * 2
    check = (12 - total % 11) % 11
    return value[-1] == ('X' if check == 10 else str(check))


def metadata(config, config_dir):
    result = copy.deepcopy(config.get('metadata', {}))
    creators = []
    profile = config.get('creator_profile')
    if profile:
        profiles = load(config_dir / profile)
        if profiles.get('schema_version') != 1: raise DepositError('Unsupported creator profile schema')
        for person in profiles.get('creators', []):
            if person.get('placeholder'):
                raise DepositError('Resolve creator placeholder: ' + str(person.get('id')))
            creators.append({k: v for k, v in person.items() if k not in {'id', 'placeholder'}})
    creators.extend(result.pop('creators', []))
    if not creators: raise DepositError('At least one verified creator is required')
    seen = set()
    for person in creators:
        name = text(person.get('name'), 'creator name')
        if name in {'TL', 'B', 'GTM'}: raise DepositError('Resolve creator placeholder: ' + name)
        if name.casefold() in seen: raise DepositError('Duplicate creator: ' + name)
        seen.add(name.casefold())
        if person.get('orcid') and not valid_orcid(person['orcid']):
            raise DepositError('Invalid ORCID checksum for ' + name)
        if 'affiliation' in person: text(person['affiliation'], 'creator affiliation')
    result['creators'] = creators
    for key in ['title', 'description', 'publication_date', 'license']:
        text(result.get(key), 'metadata.' + key)
    # This entry point archives research data with accompanying code, rather than
    # silently treating every bundle as a software-only GitHub archive.
    if result.get('upload_type') != 'dataset': raise DepositError('upload_type must be dataset')
    if result.get('access_right') not in {'open', 'embargoed', 'restricted', 'closed'}:
        raise DepositError('Choose an explicit access_right')
    try:
        dt.date.fromisoformat(result['publication_date'])
        if result['access_right'] == 'embargoed': dt.date.fromisoformat(result['embargo_date'])
    except (ValueError, KeyError) as exc: raise DepositError('Invalid publication/embargo date') from exc
    if result['access_right'] == 'restricted': text(result.get('access_conditions'), 'access_conditions')
    if not isinstance(result.get('keywords'), list) or not result['keywords']:
        raise DepositError('Provide descriptive keywords')
    for keyword in result['keywords']: text(keyword, 'keyword')
    for key, field in [('communities', 'identifier'), ('grants', 'id')]:
        for row in result.get(key, []): text(row.get(field), key + '.' + field)
    for row in result.get('related_identifiers', []):
        text(row.get('identifier'), 'related identifier'); text(row.get('relation'), 'relationship')
    for person in result.get('contributors', []):
        text(person.get('name'), 'contributor name'); text(person.get('type'), 'contributor role')
        if person.get('orcid') and not valid_orcid(person['orcid']):
            raise DepositError('Invalid contributor ORCID')
    # Never reuse a DOI assigned to another upload. We reserve a new one later.
    if 'doi' in result or 'prereserve_doi' in result:
        raise DepositError('Omit DOI fields; this command reserves the deposition DOI')
    return result


def release(repo, branch, tag):
    if not branch or not tag or branch.startswith('-') or tag.startswith('-'):
        raise DepositError('Specify branch and existing release tag')
    branch_commit = git(repo, 'rev-parse', '--verify', 'refs/heads/' + branch + '^{commit}')
    commit = git(repo, 'rev-parse', '--verify', 'refs/tags/' + tag + '^{commit}')
    check = subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', commit, branch_commit])
    if check.returncode: raise DepositError('Release tag is not on the selected branch')
    origin = git(repo, 'remote', 'get-url', 'origin').removesuffix('.git')
    match = re.fullmatch(r'(?:https://github.com/|git@github.com:)([\w.-]+/[\w.-]+)', origin)
    if not match: raise DepositError('A credential-free GitHub origin is required')
    repository = 'https://github.com/' + match[1]
    pins = [row for row in git(repo, 'ls-tree', '-r', commit).splitlines() if row.startswith('160000 ')]
    return {'branch': branch, 'branch_commit': branch_commit, 'tag': tag, 'commit': commit,
            'repository': repository, 'url': repository + '/releases/tag/' + parse.quote(tag, safe=''),
            'submodules': {row.split('\t', 1)[1]: row.split()[2] for row in pins}}


def inventory(config, data_root):
    root = Path(data_root).resolve(strict=True)
    entries, seen, sources = [], set(), set()
    assets = config.get('assets')
    if not isinstance(assets, list) or not assets: raise DepositError('Select explicit assets')
    for asset in assets:
        role, name, path = asset.get('role'), asset.get('name'), asset.get('path')
        if role not in ROLES: raise DepositError('Unknown asset role')
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name):
            raise DepositError('Asset name must be a single portable filename')
        description = text(asset.get('description'), 'asset description')
        relative(path); current = root
        for part in PurePosixPath(path).parts:
            current = current / part
            if current.is_symlink(): raise DepositError('Symlink in selected asset: ' + path)
        selected = root / path
        if not selected.exists(): raise DepositError('Missing asset: ' + path)
        files = sorted(selected.rglob('*')) if selected.is_dir() else [selected]
        count = 0
        for source in files:
            if source.is_symlink(): raise DepositError('Symlink in asset: ' + str(source.relative_to(root)))
            if source.is_dir(): continue
            if not stat.S_ISREG(source.stat().st_mode): raise DepositError('Special file in asset')
            local = str(source.relative_to(root)); public_path(local)
            member = role + '/' + name
            if selected.is_dir(): member += '/' + source.relative_to(selected).as_posix()
            public_path(member)
            if (member in seen or local in sources
                    or any(parent.as_posix() in seen for parent in PurePosixPath(member).parents)
                    or any(old.startswith(member + '/') for old in seen)):
                raise DepositError('Duplicate or overlapping asset: ' + local)
            seen.add(member); sources.add(local)
            before = source.stat()
            sha = digest(source)
            after = source.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                raise DepositError('Source changed during inventory: ' + local)
            entries.append({'path': member, 'source': local, 'role': role, 'description': description,
                            'bytes': after.st_size, 'sha256': sha})
            count += 1
        if not count: raise DepositError('Empty asset: ' + path)
    if not {'inputs', 'outputs'} <= {row['role'] for row in entries}:
        raise DepositError('Select both input and output data')
    return sorted(entries, key=lambda row: row['path'])


def plan(config_path, repo, data_root):
    config_path = Path(config_path).resolve()
    config = load(config_path)
    if config.get('schema_version') != 1: raise DepositError('Unsupported config schema')
    meta = metadata(config, config_path.parent)
    provenance = text(config.get('data_provenance'), 'data_provenance')
    rel = release(repo, config.get('branch'), config.get('tag'))
    if meta.get('version', rel['tag']) != rel['tag']: raise DepositError('version must match the release tag')
    meta['version'] = rel['tag']
    relations = meta.setdefault('related_identifiers', [])
    for identifier, relation in [(rel['url'], 'isSupplementTo'),
                                  (rel['repository'] + '/tree/' + rel['commit'], 'isDerivedFrom')]:
        if not any(r.get('identifier') == identifier for r in relations):
            relations.append({'identifier': identifier, 'relation': relation})
    entries = inventory(config, data_root)
    groups = {}
    for asset in config['assets']:
        groups.setdefault(asset['role'], []).append(asset['description'])
    navigation = ''.join('<li><strong>' + role + '.tar.gz</strong>: '
                         + html.escape('; '.join(descriptions)) + '</li>' for role, descriptions in sorted(groups.items()))
    meta['description'] += ('<h2>Release and provenance</h2><p><a href="' + html.escape(rel['url'], quote=True)
                            + '">' + html.escape(rel['tag']) + '</a>; commit <code>' + rel['commit']
                            + '</code>.</p><p>' + html.escape(provenance) + '</p><h2>Browse the deposit</h2>'
                            '<p>Start with README.md or download index.html. files.tsv and manifest.json list '
                            'every selected file, byte count and SHA-256. Citation files identify this version.</p><ul>'
                            + navigation + '<li>source.tar.gz: source at the exact release; submodule pins in manifest.json.</li></ul>')
    return {'schema_version': 1, 'release': rel, 'metadata': meta,
            'data_provenance': provenance, 'files': entries,
            'data_bytes': sum(row['bytes'] for row in entries)}


class HashedReader:
    def __init__(self, handle): self.handle, self.hash = handle, hashlib.sha256()
    def read(self, size=-1):
        block = self.handle.read(size); self.hash.update(block); return block


def data_archive(path, rows, data_root):
    with path.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w|') as archive:
            for row in rows:
                source = Path(data_root) / row['source']
                if source.is_symlink() or source.stat().st_size != row['bytes']:
                    raise DepositError('Source changed before packaging: ' + row['source'])
                info = tarfile.TarInfo(row['path']); info.size = row['bytes']; info.mode = 0o644
                with source.open('rb') as handle:
                    reader = HashedReader(handle); archive.addfile(info, reader)
                    if reader.hash.hexdigest() != row['sha256'] or handle.read(1):
                        raise DepositError('Source changed while packaging: ' + row['source'])


def source_archive(path, repo, rel):
    top = set(git(repo, 'ls-tree', '--name-only', rel['commit']).splitlines())
    paths = [p for p in SOURCE_PATHS if p in top]
    names = git(repo, 'ls-tree', '-r', '--name-only', rel['commit'], '--', *paths).splitlines()
    for name in names: public_path(name)
    with path.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
        with subprocess.Popen(['git', '-C', str(repo), 'archive', '--format=tar', '--prefix=source/',
                               rel['commit'], '--', *paths], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            shutil.copyfileobj(proc.stdout, gz)
            if proc.wait(): raise DepositError('Cannot archive release source')


def citation_files(directory, meta, rel, doi=None):
    """JSON quoting is valid YAML scalar quoting, including names and Unicode."""
    q = lambda value: json.dumps(value, ensure_ascii=False)
    lines = ['cff-version: 1.2.0', 'message: "Please cite this dataset and its source release."',
             'type: dataset', 'title: ' + q(meta['title']), 'version: ' + q(meta['version']),
             'date-released: ' + q(meta['publication_date']), 'url: ' + q(rel['url']), 'authors:']
    authors = []
    for person in meta['creators']:
        if ',' in person['name']:
            family, given = [p.strip() for p in person['name'].split(',', 1)]
            lines += ['  - family-names: ' + q(family), '    given-names: ' + q(given)]
            authors.append({'family': family, 'given': given})
        else:
            lines += ['  - name: ' + q(person['name'])]; authors.append({'literal': person['name']})
        if person.get('affiliation'): lines.append('    affiliation: ' + q(person['affiliation']))
        if person.get('orcid'): lines.append('    orcid: ' + q('https://orcid.org/' + person['orcid']))
    if doi: lines.append('doi: ' + q(doi))
    (directory / 'CITATION.cff').write_text('\n'.join(lines) + '\n')
    csl = {'type': 'dataset', 'title': meta['title'], 'author': authors, 'publisher': 'Zenodo',
           'version': meta['version'], 'issued': {'date-parts': [[int(p) for p in meta['publication_date'].split('-')]]},
           'URL': 'https://doi.org/' + doi if doi else rel['url']}
    if doi: csl['DOI'] = doi
    (directory / 'citation.csl.json').write_bytes(canonical(csl))
    cite = '; '.join(p['name'] for p in meta['creators']) + '. ' + meta['title'] + '. ' + meta['version'] + '. Zenodo.'
    cite += (' https://doi.org/' + doi + ' (reserved; usable after publication).') if doi else ' DOI pending draft creation.'
    (directory / 'CITATION.txt').write_text(cite + '\n')


def seal(directory):
    names = sorted(p.name for p in directory.iterdir() if p.name not in {'package.json', 'SHA256SUMS'})
    (directory / 'SHA256SUMS').write_text(''.join(digest(directory / name) + '  ' + name + '\n' for name in names))
    names = sorted(names + ['SHA256SUMS'])
    rows = [{'name': name, 'bytes': (directory / name).stat().st_size,
             'sha256': digest(directory / name), 'md5': digest(directory / name, 'md5')} for name in names]
    if len(rows) > 100 or sum(r['bytes'] for r in rows) > 50_000_000_000:
        raise DepositError('Package exceeds the standard Zenodo 100-file / 50 GB limit')
    document = {'schema_version': 1, 'files': rows}
    document['sha256'] = hashlib.sha256(canonical(document)).hexdigest()
    (directory / 'package.json').write_bytes(canonical(document))
    return document


def verify_package(directory):
    directory = Path(directory)
    if directory.is_symlink(): raise DepositError('Package directory must not be a symlink')
    doc = load(directory / 'package.json'); unsigned = {k: v for k, v in doc.items() if k != 'sha256'}
    if hashlib.sha256(canonical(unsigned)).hexdigest() != doc.get('sha256'):
        raise DepositError('Package seal changed')
    expected = set()
    for row in doc['files']:
        name = row['name']; relative(name)
        if '/' in name or name in expected: raise DepositError('Invalid package inventory')
        expected.add(name); file = directory / name
        if (file.is_symlink() or not file.is_file() or file.stat().st_size != row['bytes']
                or digest(file) != row['sha256'] or digest(file, 'md5') != row['md5']):
            raise DepositError('Package changed: ' + name)
    if {p.name for p in directory.iterdir()} != expected | {'package.json'}:
        raise DepositError('Unexpected package files; keep receipts outside the package')
    return doc


def prepare(config_path, repo, data_root, destination):
    document = plan(config_path, repo, data_root)
    destination = Path(destination).absolute()
    if destination.exists(): raise DepositError('Destination must be new')
    for row in document['files']:
        if destination.is_relative_to((Path(data_root) / row['source']).parent):
            raise DepositError('Package destination overlaps selected data')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Conservative bound: uncompressed data + source + reserve; never retires data.
    reserve = 1024**3
    for root in [Path(repo), Path(data_root)]:
        contract = root / 'outputs/storage-contract.json'
        if contract.is_file():
            reserve = max(reserve, int(load(contract).get('automation', {}).get('reserve_bytes', reserve)))
    if shutil.disk_usage(destination.parent).free < document['data_bytes'] + reserve:
        raise DepositError('Insufficient package capacity (data size plus 1 GiB reserve)')
    temp = Path(tempfile.mkdtemp(prefix='.zenodo-', dir=destination.parent))
    try:
        for role in sorted({row['role'] for row in document['files']}):
            data_archive(temp / (role + '.tar.gz'), [r for r in document['files'] if r['role'] == role], data_root)
        source_archive(temp / 'source.tar.gz', repo, document['release'])
        (temp / 'manifest.json').write_bytes(canonical(document))
        (temp / 'zenodo-metadata.json').write_bytes(canonical(document['metadata']))
        citation_files(temp, document['metadata'], document['release'])
        rows = ['path\tbytes\tsha256'] + [f"{r['path']}\t{r['bytes']}\t{r['sha256']}" for r in document['files']]
        (temp / 'files.tsv').write_text('\n'.join(rows) + '\n')
        rel = document['release']; meta = document['metadata']
        readme = (f"# {meta['title']}\n\n{meta['description']}\n\n"
                  f"Release: {rel['url']}\n\nBranch: `{rel['branch']}`; commit: `{rel['commit']}`.\n\n"
                  f"## Data provenance\n\n{document['data_provenance']}\n\n"
                  f"## Contents\n\n{len(document['files'])} selected files, {document['data_bytes']:,} bytes.\n\n"
                  "Start with `index.html`; `files.tsv` lists every archive member and its SHA-256. "
                  "Archives use inputs/, outputs/, reports/ and provenance/ folders. "
                  "`source.tar.gz` contains release source; submodule commits are recorded in `manifest.json` "
                  "and must be obtained separately. Scientific stages were not run.\n\n"
                  f"Data license: {meta['license']}. Code retains its own LICENSE in source.tar.gz. "
                  "Confirm redistribution rights for every selected input and output before publication.\n\n"
                  "Citation: CITATION.txt, CITATION.cff and citation.csl.json. "
                  "The exact version DOI is inserted when the draft is created; it resolves after publication.\n")
        (temp / 'README.md').write_text(readme)
        links = ''.join(f'<li><a href="{parse.quote(p.name)}">{html.escape(p.name)}</a></li>'
                        for p in sorted(temp.iterdir()))
        links += '<li><a href="SHA256SUMS">SHA256SUMS</a></li>'
        table = ''.join(f"<tr><td>{html.escape(r['path'])}</td><td>{r['bytes']}</td>"
                        f"<td>{html.escape(r['description'])}</td></tr>" for r in document['files'])
        (temp / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width"><title>' + html.escape(meta['title']) + '</title>'
            '<style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:16px}'
            'td,th{text-align:left;padding:8px;border-bottom:1px solid #ddd}td:first-child{overflow-wrap:anywhere}</style>'
            '<h1>' + html.escape(meta['title']) + '</h1><p>Read README.md for provenance, license and citation.</p><ul>'
            + links + '</ul><h2>File inventory</h2><table><tr><th>Archive path</th><th>Bytes</th><th>Description</th></tr>'
            + table + '</table></html>')
        seal(temp); temp.rename(destination)
    except BaseException:
        shutil.rmtree(temp); raise
    return verify_package(destination)


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs): return None


class Zenodo:
    def __init__(self, environment, token=None):
        self.origin = HOSTS[environment]
        token_env = 'ZENODO_SANDBOX_TOKEN' if environment == 'sandbox' else 'ZENODO_ACCESS_TOKEN'
        self.token = token or os.environ.get(token_env, '').strip()
        if not self.token: raise DepositError('Set ' + token_env + ' on this machine')
        self.opener = request.build_opener(NoRedirect())

    def url(self, value):
        url = parse.urljoin(self.origin, value)
        parts = parse.urlsplit(url)
        if (parts.scheme != 'https' or parts.netloc != parse.urlsplit(self.origin).netloc
                or parts.query or parts.fragment or parts.username or not parts.path.startswith('/api/')):
            raise DepositError('Refusing an unexpected Zenodo API link')
        return url

    def call(self, method, path, payload=None, file=None):
        headers = {'Authorization': 'Bearer ' + self.token, 'Accept': 'application/json'}
        data = None
        if payload is not None: data = canonical(payload); headers['Content-Type'] = 'application/json'
        if file:
            data = Path(file).open('rb'); headers['Content-Type'] = 'application/octet-stream'
            headers['Content-Length'] = str(Path(file).stat().st_size)
        req = request.Request(self.url(path), data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=600 if file else 60) as response:
                body = response.read(); return json.loads(body) if body else {}
        except error.HTTPError as exc:
            detail = exc.read(4000).decode(errors='replace').replace(self.token, '[redacted]')
            raise DepositError(f'Zenodo HTTP {exc.code}: {detail}') from None
        except (error.URLError, TimeoutError, OSError):
            raise DepositError('Zenodo connection failed; inspect the saved receipt before resuming') from None
        finally:
            if file and data: data.close()


def verify_release_online(repo, rel):
    remote = git(repo, 'ls-remote', rel['repository'] + '.git',
                 'refs/tags/' + rel['tag'], 'refs/tags/' + rel['tag'] + '^{}')
    objects = dict(row.split('\t')[::-1] for row in remote.splitlines())
    actual = objects.get('refs/tags/' + rel['tag'] + '^{}', objects.get('refs/tags/' + rel['tag']))
    if actual != rel['commit']: raise DepositError('Remote release tag differs from frozen commit')
    result = subprocess.run(['gh', 'release', 'view', rel['tag'], '--repo',
                             rel['repository'], '--json', 'tagName,isDraft,url,publishedAt'], capture_output=True, text=True)
    if result.returncode: raise DepositError('Create the GitHub release for this tag before uploading')
    published = json.loads(result.stdout)
    if published.get('isDraft') or not published.get('publishedAt') or published['tagName'] != rel['tag']:
        raise DepositError('The GitHub release must be published and match the tag')


def draft(directory, receipt_path, environment, repo, client=None, resume_id=None):
    directory, receipt_path = Path(directory), Path(receipt_path)
    if receipt_path.resolve().is_relative_to(directory.resolve()):
        raise DepositError('Store receipt outside the immutable package')
    if receipt_path.exists():
        pending = load(receipt_path)
        if pending.get('environment') != environment: raise DepositError('Receipt environment differs')
        if pending.get('status') == 'citation-update':
            finish_citations(directory, receipt_path, pending)
    package = verify_package(directory); manifest = load(directory / 'manifest.json')
    verify_release_online(repo, manifest['release'])
    client = client or Zenodo(environment)
    if receipt_path.exists():
        state = load(receipt_path)
        if state['environment'] != environment: raise DepositError('Receipt environment differs')
        if state.get('package_sha256') != package['sha256']:
            raise DepositError('Package differs from the upload receipt')
        if not state.get('id'):
            if not resume_id: raise DepositError('Creation outcome unknown; inspect Zenodo, then supply --resume-id')
            state['id'] = int(resume_id); save(receipt_path, state)
    else:
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        state = {'schema_version': 1, 'environment': environment, 'package_sha256': package['sha256'],
                 'status': 'creating', 'id': int(resume_id) if resume_id else None}
        save(receipt_path, state)  # Intent is durable BEFORE the non-idempotent POST.
        if not state['id']:
            created = client.call('POST', '/api/deposit/depositions', {})
            state['id'] = int(created['id']); save(receipt_path, state)
    path = '/api/deposit/depositions/' + str(state['id'])
    deposit = client.call('GET', path)
    if deposit.get('submitted') or deposit.get('state') == 'done':
        raise DepositError('Deposition is already submitted/published; use a new reviewed version')
    if deposit.get('state') not in {'unsubmitted', 'inprogress'}:
        raise DepositError('Deposition is not an editable draft')
    meta = load(directory / 'zenodo-metadata.json')
    updated = client.call('PUT', path, {'metadata': {**meta, 'prereserve_doi': True}})
    doi = updated.get('metadata', {}).get('prereserve_doi', {}).get('doi')
    if not doi: raise DepositError('Zenodo did not return a reserved DOI')
    if state.get('doi') and state['doi'] != doi: raise DepositError('Reserved DOI changed')
    # Persist before rewriting local files; these operations are deterministic.
    # Generate into a separate directory, and record both old and intended new
    # citation bytes before replacing anything in the package.
    with tempfile.TemporaryDirectory() as temp:
        citation_files(Path(temp), meta, manifest['release'], doi)
        citation_updates = {p.name: p.read_text() for p in Path(temp).iterdir()}
    state.update(doi=doi, status='citation-update', citation_updates=citation_updates,
                 package_before_citation=package)
    save(receipt_path, state)
    finish_citations(directory, receipt_path, state)
    package = verify_package(directory)
    expected = {r['name']: r for r in package['files']}
    listed = {r['filename']: r for r in deposit.get('files', [])}
    if set(listed) - set(expected): raise DepositError('Draft contains unexpected files; nothing was deleted')
    bucket = client.url(deposit['links']['bucket']).rstrip('/')
    for name, row in expected.items():
        if name in listed:
            actual = listed[name]
            if actual.get('checksum', '').removeprefix('md5:') == row['md5'] and int(actual['filesize']) == row['bytes']:
                continue
            raise DepositError('Existing remote file differs: ' + name + '; inspect it before resuming')
        client.call('PUT', bucket + '/' + parse.quote(name, safe=''), file=directory / name)
        state.update(status='uploading', last_uploaded=name); save(receipt_path, state)
    verified = client.call('GET', path)
    verify_remote(verified, package)
    state.update(status='draft-ready', url=verified['links'].get('html'), package_sha256=package['sha256'])
    save(receipt_path, state)
    return state


def verify_remote(deposit, package):
    listed = {r['filename']: r for r in deposit.get('files', [])}
    if set(listed) != {r['name'] for r in package['files']}: raise DepositError('Remote inventory differs')
    for row in package['files']:
        remote = listed[row['name']]
        if (remote.get('checksum', '').removeprefix('md5:') != row['md5']
                or int(remote['filesize']) != row['bytes']):
            raise DepositError('Remote checksum/size differs: ' + row['name'])


def finish_citations(directory, receipt_path, state):
    """Recover an interrupted local DOI insertion without accepting other edits."""
    directory = Path(directory)
    updates = state['citation_updates']; original = state['package_before_citation']
    if set(updates) != {'CITATION.cff', 'citation.csl.json', 'CITATION.txt'}:
        raise DepositError('Invalid citation update receipt')
    if {p.name for p in directory.iterdir()} != {r['name'] for r in original['files']} | {'package.json'}:
        raise DepositError('Unexpected files during citation update')
    intended_checksums = ''.join(
        (hashlib.sha256(updates[row['name']].encode()).hexdigest() if row['name'] in updates else row['sha256'])
        + '  ' + row['name'] + '\n' for row in original['files'] if row['name'] != 'SHA256SUMS')
    for row in original['files']:
        p = directory / row['name']
        allowed = {row['sha256']}
        if p.name in updates: allowed.add(hashlib.sha256(updates[p.name].encode()).hexdigest())
        if p.name == 'SHA256SUMS': allowed.add(hashlib.sha256(intended_checksums.encode()).hexdigest())
        if p.is_symlink() or not p.is_file() or digest(p) not in allowed:
            raise DepositError('Package changed during citation update: ' + p.name)
    for name, content in updates.items():
        fd, temporary = tempfile.mkstemp(dir=directory, prefix='.citation-')
        with os.fdopen(fd, 'w') as handle:
            handle.write(content); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, directory / name)
    package = seal(directory)
    state.update(status='uploading', package_sha256=package['sha256'])
    state.pop('citation_updates', None); state.pop('package_before_citation', None)
    save(receipt_path, state)


def publish(directory, receipt_path, confirm, repo, client=None):
    package = verify_package(directory); state = load(receipt_path)
    if state.get('package_sha256') != package['sha256'] or confirm != package['sha256']:
        raise DepositError('Confirm the exact reviewed package SHA-256')
    if state.get('status') not in {'draft-ready', 'publishing', 'published'}:
        raise DepositError('Verify the complete draft before publishing')
    manifest = load(Path(directory) / 'manifest.json'); verify_release_online(repo, manifest['release'])
    client = client or Zenodo(state['environment']); path = '/api/deposit/depositions/' + str(state['id'])
    current = client.call('GET', path); verify_remote(current, package)
    expected = load(Path(directory) / 'zenodo-metadata.json')
    for key, value in expected.items():
        if not same_metadata(value, current.get('metadata', {}).get(key), key):
            raise DepositError('Remote metadata changed; review before publishing: ' + key)
    reserved = current.get('metadata', {}).get('prereserve_doi', {}).get('doi') or current.get('doi')
    if reserved != state.get('doi'): raise DepositError('Remote DOI differs from the citation DOI')
    if not current.get('submitted'):
        if state['status'] == 'publishing':
            raise DepositError('Prior publish outcome is uncertain; inspect Zenodo before any retry')
        state['status'] = 'publishing'; save(receipt_path, state)
        current = client.call('POST', path + '/actions/publish')
    state.update(status='published' if current.get('submitted') else 'publishing',
                 url=current.get('links', {}).get('record_html', state.get('url')))
    save(receipt_path, state); return state


def same_metadata(expected, actual, field=''):
    """Allow added server identifiers/defaults while preserving supplied metadata."""
    if field == 'license' and isinstance(actual, dict): actual = actual.get('id')
    if field == 'orcid' and isinstance(actual, str): actual = actual.removeprefix('https://orcid.org/')
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(same_metadata(v, actual.get(k), k) for k, v in expected.items())
    if isinstance(expected, list):
        if not expected and actual is None: return True
        return isinstance(actual, list) and len(expected) == len(actual) and all(
            same_metadata(a, b, field) for a, b in zip(expected, actual))
    return expected == actual


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ['plan', 'prepare']:
        sub = commands.add_parser(name); sub.add_argument('--config', required=True, type=Path)
        sub.add_argument('--repo', type=Path, default=ROOT); sub.add_argument('--data-root', required=True, type=Path)
        if name == 'prepare': sub.add_argument('--out', required=True, type=Path)
    check = commands.add_parser('verify'); check.add_argument('--package', required=True, type=Path)
    for name in ['draft', 'publish']:
        sub = commands.add_parser(name); sub.add_argument('--package', required=True, type=Path)
        sub.add_argument('--receipt', required=True, type=Path); sub.add_argument('--repo', type=Path, default=ROOT)
        if name == 'draft':
            sub.add_argument('--environment', choices=HOSTS, default='sandbox')
            sub.add_argument('--apply', action='store_true', help='Explicitly create/update remote draft')
            sub.add_argument('--resume-id', type=int, help='Manually reconciled existing draft ID')
        else: sub.add_argument('--confirm', required=True, help='Exact reviewed package SHA-256; publishes irreversibly')
    args = parser.parse_args(argv)
    try:
        if args.command == 'plan': result = plan(args.config, args.repo, args.data_root)
        elif args.command == 'prepare': result = prepare(args.config, args.repo, args.data_root, args.out)
        elif args.command == 'verify': result = verify_package(args.package)
        elif args.command == 'draft':
            if not args.apply:
                result = {'action': 'preview-only', 'environment': args.environment,
                          'package': verify_package(args.package), 'network_requests': 0}
            else: result = draft(args.package, args.receipt, args.environment, args.repo, resume_id=args.resume_id)
        else: result = publish(args.package, args.receipt, args.confirm, args.repo)
        print(json.dumps(result, indent=2, ensure_ascii=False)); return 0
    except (DepositError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print('Zenodo: ' + str(exc), file=sys.stderr); return 2


if __name__ == '__main__':
    raise SystemExit(main())
