import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


class ManifestAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name); self.repo = self.base / 'repo'
        self.config = self.repo / 'zenodo/configs/config.json'; self.config.parent.mkdir(parents=True)
        self.config.write_text('{}')
        self.manifests = self.repo / 'zenodo/manifests'; self.manifests.mkdir()
        self.source = self.base / 'private-canonical'; self.source.mkdir()
        self.files = {'one.pdb': b'ATOM fixture one\n', 'two.cif': b'data_fixture_two\n', 'confidence.json': b'{"ptm":0.8}\n'}
        for name, data in self.files.items(): (self.source / name).write_bytes(data)
        self.binding = self.base / 'private-roots.json'
        self.binding.write_text(json.dumps({'roots': {'fixture-root': str(self.source)}})); self.binding.chmod(0o600)
        self.env = patch.dict(os.environ, {'SCHERAGA_ASSET_ROOTS_FILE': str(self.binding)}); self.env.start(); self.addCleanup(self.env.stop)
        self.up = load('zenodo_deposition'); self.up.ROOT = self.repo
        self.module = load('zenodo_manifest_assets')
        self.rows = [dict(dataset='Adk', role='fixture', model_id='model_' + str(i), method='fixture', scope='target',
                          asset_root='fixture-root', relative_path=name, bytes=str(len(data)), sha256=hashlib.sha256(data).hexdigest())
                     for i, (name, data) in enumerate(self.files.items(), 1)]
        self.config_value = {'assets': [self.asset('inputs', self.rows[:1]), self.asset('outputs', self.rows[1:])]}
        self.adapter = self.module.ManifestAssets(self.up, self.config)

    def asset(self, role, rows):
        p = self.manifests / (role + '.tsv')
        stream = io.StringIO(); w = csv.DictWriter(stream, list(self.rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(rows); p.write_text(stream.getvalue())
        return {'role': role, 'name': role, 'path': 'unused/not-present', 'description': 'Fixture asset',
                'manifest': '../manifests/' + p.name, 'manifest_sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

    def test_three_rows_stream_exact_bytes_and_never_serialize_private_roots(self):
        entries = self.adapter.inventory(self.config_value, self.repo)
        self.assertEqual(len(entries), 3)
        public = json.dumps(entries)
        self.assertNotIn(str(self.source), public); self.assertNotIn(str(self.binding), public)
        self.assertTrue(all(e['source'].startswith('fixture-root/') for e in entries))
        archive = self.repo / 'fixture.tar.gz'
        self.adapter.data_archive(archive, entries, self.repo)
        with tarfile.open(archive, 'r:gz') as tf:
            self.assertEqual(len(tf.getmembers()), 3)
            for e in entries:
                data = tf.extractfile(e['path']).read()
                self.assertEqual(data, self.files[e['original_relative_path']])
                self.assertNotIn(str(self.source).encode(), data)
                self.assertIn(e['model_id'] + '/', e['path'])
                self.assertTrue(e['path'].endswith(e['original_relative_path']))

    def test_manifest_pin_is_checked_before_any_payload_hash(self):
        self.config_value['assets'][1]['manifest_sha256'] = '0' * 64
        with patch.object(self.up, 'digest') as digest, self.assertRaises(self.up.DepositError):
            self.adapter.inventory(self.config_value, self.repo)
        digest.assert_not_called()

    def test_hash_and_traversal_and_symlink_mismatches_stop(self):
        for change in ['hash', 'traversal', 'symlink']:
            with self.subTest(change=change):
                row = dict(self.rows[0])
                if change == 'hash': row['sha256'] = '0' * 64
                elif change == 'traversal': row['relative_path'] = '../outside.pdb'
                else:
                    (self.source / 'one.pdb').unlink(); (self.source / 'one.pdb').symlink_to(self.source / 'two.cif')
                config = {'assets': [self.asset('inputs', [row]), self.asset('outputs', self.rows[1:])]}
                with self.assertRaises(self.up.DepositError): self.adapter.inventory(config, self.repo)

    def test_duplicate_physical_file_and_wrong_private_mode_stop(self):
        duplicate = {'assets': [self.asset('inputs', self.rows[:1]), self.asset('outputs', self.rows[:1])]}
        with self.assertRaises(self.up.DepositError): self.adapter.inventory(duplicate, self.repo)
        self.binding.chmod(0o644)
        with self.assertRaises(self.up.DepositError): self.adapter.inventory(self.config_value, self.repo)

    def test_mixed_dataset_needs_explicit_filter(self):
        row = dict(self.rows[2], dataset='Mad2')
        config = {'assets': [self.asset('inputs', self.rows[:1]), self.asset('outputs', [self.rows[1], row])]}
        with self.assertRaises(self.up.DepositError): self.adapter.inventory(config, self.repo)
        config['assets'][1]['dataset'] = 'Adk'
        self.assertEqual(len(self.adapter.inventory(config, self.repo)), 2)

    def test_invalid_size_and_partial_manifest_mode_stop(self):
        row = dict(self.rows[0], bytes='not-a-size')
        config = {'assets': [self.asset('inputs', [row]), self.asset('outputs', self.rows[1:])]}
        with self.assertRaises(self.up.DepositError): self.adapter.inventory(config, self.repo)
        config['assets'][1].pop('manifest')
        with self.assertRaises(self.up.DepositError): self.adapter.inventory(config, self.repo)
        with self.assertRaises(self.up.DepositError):
            self.adapter.inventory({'assets': [None]}, self.repo)

    def test_source_mutation_before_streaming_stops(self):
        entries = self.adapter.inventory(self.config_value, self.repo)
        (self.source / 'one.pdb').write_bytes(b'x' * len(self.files['one.pdb']))
        with self.assertRaises(self.up.DepositError):
            self.adapter.data_archive(self.repo / 'changed.tar.gz', entries, self.repo)

    def test_manifest_locator_outside_zenodo_and_symlink_stop(self):
        self.config_value['assets'][0]['manifest'] = '../../../outside.tsv'
        with self.assertRaises(self.up.DepositError): self.adapter.inventory(self.config_value, self.repo)
        link = self.manifests / 'link.tsv'; link.symlink_to(self.manifests / 'inputs.tsv')
        self.config_value['assets'][0]['manifest'] = '../manifests/link.tsv'
        with self.assertRaises(self.up.DepositError): self.adapter.inventory(self.config_value, self.repo)


if __name__ == '__main__': unittest.main()
