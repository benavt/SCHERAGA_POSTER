"""Exact TSV-backed assets; private roots are resolved only while reading bytes."""
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile

FIELDS = {'dataset', 'role', 'model_id', 'method', 'scope', 'asset_root', 'relative_path', 'bytes', 'sha256'}
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]*')
SHA = re.compile(r'[0-9a-f]{64}')


class ManifestAssets:
    def __init__(self, upstream, config_path):
        self.u = upstream
        self.config_dir = Path(config_path).absolute().parent
        self.zenodo_dir = upstream.ROOT / 'zenodo'
        self.binding_pin = None

    def fail(self, message):
        raise self.u.DepositError(message)

    def no_symlinks(self, path):
        current = Path(path.anchor)
        try:
            for part in path.parts[1:]:
                current = current / part
                if current.is_symlink():
                    self.fail('Symlinks are prohibited in manifest asset paths')
        except OSError:
            self.fail('Cannot inspect manifest asset path')

    def identity(self, st):
        return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns

    def roots(self):
        value = os.environ.get('SCHERAGA_ASSET_ROOTS_FILE')
        if not value:
            self.fail('Set SCHERAGA_ASSET_ROOTS_FILE to the private root dictionary')
        p = Path(value).absolute()
        self.no_symlinks(p)
        try:
            a = p.stat()
            if not stat.S_ISREG(a.st_mode) or stat.S_IMODE(a.st_mode) != 0o600:
                self.fail('Private root dictionary must be a regular mode-0600 file')
            raw = p.read_bytes()
            if self.identity(a) != self.identity(p.stat()):
                self.fail('Private root dictionary changed while reading')
            document = json.loads(raw)
            roots = document['roots']
            if not isinstance(roots, dict) or not roots:
                self.fail('Private root dictionary has no roots')
            for key, root in roots.items():
                if not ID.fullmatch(key) or not isinstance(root, str) or not Path(root).is_absolute():
                    self.fail('Invalid private root dictionary')
            pin = hashlib.sha256(raw).hexdigest()
            if self.binding_pin is not None and pin != self.binding_pin:
                self.fail('Private root dictionary changed since inventory')
            return roots, pin
        except (OSError, ValueError, KeyError, TypeError):
            self.fail('Cannot read valid private root dictionary')

    def source(self, key, roots):
        try:
            root_id, relative = key.split('/', 1)
            if not ID.fullmatch(root_id) or root_id not in roots:
                self.fail('Unknown logical asset root')
            self.u.relative(relative)
            self.u.public_path(relative)
            p = Path(roots[root_id]) / relative
            self.no_symlinks(p)
            if not stat.S_ISREG(p.stat().st_mode):
                self.fail('Manifest payload must be a regular file')
            return p
        except (OSError, ValueError):
            self.fail('Cannot resolve regular manifest payload from its portable key')

    def manifest(self, asset):
        value = asset.get('manifest')
        expected = asset.get('manifest_sha256')
        if not isinstance(value, str) or '\\' in value or PurePosixPath(value).is_absolute() or not isinstance(expected, str) or not SHA.fullmatch(expected):
            self.fail('Supply a relative manifest locator and manifest_sha256')
        raw_path = self.config_dir / value
        self.no_symlinks(raw_path)
        try:
            p = raw_path.resolve(strict=True)
            if not p.is_relative_to(self.zenodo_dir.resolve()) or not p.is_file():
                self.fail('Manifest locator must stay inside the public zenodo tree')
            before = p.stat(); raw = p.read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected or self.identity(before) != self.identity(p.stat()):
                self.fail('Manifest SHA256 mismatch or changing manifest; no payloads read')
            reader = csv.DictReader(io.StringIO(raw.decode('utf-8')), delimiter='\t')
            if set(reader.fieldnames or []) != FIELDS:
                self.fail('Manifest TSV columns differ from the required schema')
            rows = list(reader)
            if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
                self.fail('Empty or malformed manifest TSV')
            selected = asset.get('dataset')
            datasets = {row['dataset'] for row in rows}
            if selected is not None:
                if not isinstance(selected, str) or selected not in datasets:
                    self.fail('Explicit dataset filter has no matching rows')
                rows = [row for row in rows if row['dataset'] == selected]
            elif len(datasets) != 1:
                self.fail('Mixed-dataset manifest requires an explicit dataset filter')
            return rows
        except (OSError, UnicodeError, csv.Error):
            self.fail('Cannot read stable public manifest TSV')

    def inventory(self, config, data_root):
        assets = config.get('assets')
        if not isinstance(assets, list) or not assets or not all(isinstance(a, dict) and a.get('manifest') for a in assets):
            self.fail('Manifest mode requires a manifest on every asset; no implicit path fallback')
        # Pin every TSV before accessing any payload, including later assets.
        selections = [(a, self.manifest(a)) for a in assets]
        roots, self.binding_pin = self.roots()
        entries, members, physical, directories = [], set(), set(), set()
        for asset, rows in selections:
            role, name = asset.get('role'), asset.get('name')
            if role not in self.u.ROLES or not isinstance(name, str) or not ID.fullmatch(name):
                self.fail('Invalid manifest asset role or portable name')
            description = self.u.text(asset.get('description'), 'asset description')
            for row in rows:
                if not ID.fullmatch(row['asset_root']) or not SHA.fullmatch(row['sha256']):
                    self.fail('Invalid portable root or payload SHA256')
                self.u.relative(row['relative_path'])
                self.u.public_path(row['relative_path'])
                if any(not ID.fullmatch(row[k]) for k in ['dataset', 'role', 'scope']) or (row['method'] and not ID.fullmatch(row['method'])):
                    self.fail('Manifest dataset, role, method and scope must be portable identifiers')
                if not re.fullmatch(r'0|[1-9][0-9]*', row['bytes']):
                    self.fail('Manifest bytes must be a nonnegative integer')
                model = row['model_id']
                if model and not ID.fullmatch(model):
                    self.fail('Model identifier is not a portable path component')
                key = row['asset_root'] + '/' + row['relative_path']
                source = self.source(key, roots)
                try:
                    size = int(row['bytes']); before = source.stat()
                    if size < 0 or before.st_size != size:
                        self.fail('Manifest payload size mismatch: ' + key)
                    inode = before.st_dev, before.st_ino
                    member = role + '/' + name + '/' + ((model + '/') if model else '') + row['relative_path']
                    self.u.public_path(member)
                    parents = {p.as_posix() for p in PurePosixPath(member).parents}
                    if member in members or member in directories or parents.intersection(members) or inode in physical:
                        self.fail('Duplicate or overlapping archive member or physical source')
                    actual = self.u.digest(source)
                    if actual != row['sha256'] or self.identity(before) != self.identity(source.stat()):
                        self.fail('Manifest payload SHA256 mismatch or source change: ' + key)
                except OSError:
                    self.fail('Cannot read stable manifest payload: ' + key)
                members.add(member); directories.update(parents); physical.add(inode)
                entries.append({'path': member, 'source': key, 'role': role, 'description': description,
                                'bytes': size, 'sha256': actual, 'dataset': row['dataset'],
                                'model_id': model, 'method': row['method'], 'scope': row['scope'],
                                'manifest_role': row['role'], 'original_relative_path': row['relative_path']})
        self.roots()  # Reject binding drift during a long inventory.
        if not {'inputs', 'outputs'} <= {r['role'] for r in entries}:
            self.fail('Select both input and output data')
        return sorted(entries, key=lambda row: row['path'])

    def data_archive(self, path, rows, data_root):
        roots, _ = self.roots()
        with Path(path).open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode='w|') as archive:
                for row in rows:
                    source = self.source(row['source'], roots)
                    try:
                        before = source.stat()
                        if before.st_size != row['bytes']:
                            self.fail('Source size changed before archive: ' + row['source'])
                        if Path(path).absolute().is_relative_to(source.parent):
                            self.fail('Archive destination overlaps canonical payload source')
                        info = tarfile.TarInfo(row['path']); info.size = row['bytes']; info.mode = 0o644
                        with source.open('rb') as handle:
                            reader = self.u.HashedReader(handle)
                            archive.addfile(info, reader)
                            if reader.hash.hexdigest() != row['sha256'] or handle.read(1):
                                self.fail('Source SHA256 changed while streaming: ' + row['source'])
                        if self.identity(before) != self.identity(source.stat()):
                            self.fail('Source identity changed while streaming: ' + row['source'])
                    except OSError:
                        self.fail('Cannot stream stable manifest payload: ' + row['source'])
        self.roots()


def install(upstream, config_path):
    """Patch only this in-memory upstream instance, never its source bytes."""
    adapter = ManifestAssets(upstream, config_path)
    upstream.inventory = adapter.inventory
    upstream.data_archive = adapter.data_archive
    return adapter
