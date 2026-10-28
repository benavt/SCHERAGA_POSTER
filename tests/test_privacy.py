"""Verify the standalone publication check against real temporary Git indexes."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('privacy', Path(__file__).resolve().parents[1] / 'tools/check_privacy.py')
privacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(privacy)


class Privacy(unittest.TestCase):
    def test_artifact_and_secret_detection(self):
        for name in ('local/notes.md', 'docs/.env', 'tools/id_example', 'docs/key.pem', '../README.md'):
            with self.subTest(name=name):
                self.assertTrue(privacy.violations(name, b'ordinary text'))
        for secret in (b'gh' + b'p_' + b'a' * 30, b'-----BEGIN ' + b'PRIVATE KEY-----',
                       b'ZENODO_ACCESS_TOKEN=' + b'a' * 60):
            self.assertIn('credential pattern', privacy.violations('README.md', secret))
        self.assertIn('local credential value', privacy.violations('README.md', b'known-canary', ['known-canary']))
        self.assertEqual([], privacy.violations('docs/results.md', b'Public study results'))

    def test_staged_content_cannot_be_hidden_by_clean_working_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', directory], check=True)
            path = root / 'README.md'
            path.write_bytes(b'gh' + b'p_' + b'a' * 30)
            subprocess.run(['git', 'add', 'README.md'], cwd=root, check=True)
            path.write_text('Public introduction\n')
            with patch.object(privacy, 'ROOT', root), patch.object(privacy, 'project_credentials', return_value=[]):
                with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(1, privacy.main(['--tracked']))
                    self.assertEqual(0, privacy.main(['--tracked', '--working-tree']))
                    path.write_text('Public introduction\n' + ('192' + '.168.1.2'))
                    self.assertEqual(1, privacy.main(['--tracked', '--working-tree']))

    def test_symlinks_are_rejected_without_reading_their_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', directory], check=True)
            (root / 'README.md').symlink_to('missing-target')
            subprocess.run(['git', 'add', 'README.md'], cwd=root, check=True)
            with patch.object(privacy, 'ROOT', root), patch.object(privacy, 'project_credentials', return_value=[]):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(1, privacy.main(['--tracked']))
                    self.assertEqual(1, privacy.main(['--tracked', '--working-tree']))

    def test_environment_credentials_are_checked_without_external_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', directory], check=True)
            (root / 'README.md').write_text('example-local-canary\n')
            subprocess.run(['git', 'add', 'README.md'], cwd=root, check=True)
            output = io.StringIO()
            with patch.object(privacy, 'ROOT', root), patch.dict('os.environ', {'ZENODO_ACCESS_TOKEN': 'example-local-canary'}):
                with contextlib.redirect_stderr(output):
                    self.assertEqual(1, privacy.main(['--tracked']))
            self.assertNotIn('example-local-canary', output.getvalue())

    def test_private_hostname_detection_in_text_files(self):
        """Verify that private hostnames are detected case-insensitively in human-readable files."""
        # Test various capitalizations and embedded forms
        for content in (b'Pax exports', b'PAX machine', b'pax-config', 
                       b'Mimas_Folding_Skills', b'mimas system', b'MIMAS node'):
            with self.subTest(content=content):
                self.assertIn('private hostname', privacy.violations('docs/README.md', content))
        
        # Test that hostnames alone (without other violations) are caught
        self.assertEqual(['private hostname'], privacy.violations('docs/README.md', b'The Pax system.'))

    def test_private_hostname_exclusion_from_binary_assets(self):
        """Verify that encoded coincidences in binary/compressed files do not trigger false positives."""
        # These extensions should be excluded from hostname checks to avoid false positives
        # from random byte sequences that happen to match the pattern
        for extension in ('.pdf', '.zip', '.gz', '.png', '.jpg', '.mp4'):
            filename = f'poster/document{extension}'
            with self.subTest(filename=filename):
                # Even if "pax" or "mimas" appears as bytes, it should not be flagged
                self.assertEqual([], privacy.violations(filename, b'...PaX%C9...MImAs...'))
        
        # But the same content in a text file SHOULD be detected
        self.assertIn('private hostname', privacy.violations('docs/notes.md', b'PaX exports'))


if __name__ == '__main__':
    unittest.main()
