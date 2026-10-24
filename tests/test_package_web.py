#!/usr/bin/env python3
"""Test package_web.py output against deployment workflow validation rules."""
import base64
import hashlib
import importlib.util
import json
import stat
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

package_web = load_module('package_web', ROOT / 'site/virtual-poster/package_web.py')


class PackageWebOutputValidation(unittest.TestCase):
    """Verify package_web.py produces outputs accepted by deploy-pages.yml."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.temp_dir = Path(self.temp.name)
        self.script_path = ROOT / 'site/virtual-poster/package_web.py'

    def create_minimal_offline_html(self):
        """Create a minimal offline HTML with embedded assets for testing."""
        # Create a tiny test image (1x1 transparent PNG)
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        png_uri = 'data:image/png;base64,' + base64.b64encode(png_data).decode()
        
        # Create a tiny SVG
        svg_data = b'<svg xmlns="http://www.w3.org/2000/svg"/>'
        svg_uri = 'data:image/svg+xml;base64,' + base64.b64encode(svg_data).decode()
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Test Poster</title>
</head>
<body>
    <h1>Test Virtual Poster</h1>
    <img src="{png_uri}" alt="Test image">
    <img src="{svg_uri}" alt="Test SVG">
</body>
</html>'''
        return html

    def run_package_web(self, input_file, output_dir, expected_sha):
        """Run package_web.py as a subprocess."""
        result = subprocess.run(
            ['python3', str(self.script_path), 
             '--input', str(input_file),
             '--output-dir', str(output_dir),
             '--expected-sha256', expected_sha],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            self.fail(f'package_web.py failed: {result.stderr}')
        return result

    def test_required_members_present(self):
        """Verify index.html and asset-manifest.json are always present."""
        html = self.create_minimal_offline_html()
        offline = self.temp_dir / 'offline.html'
        offline.write_text(html)
        output_dir = self.temp_dir / 'output'
        expected_sha = hashlib.sha256(html.encode()).hexdigest()
        
        self.run_package_web(offline, output_dir, expected_sha)
        
        # Find the generated ZIP
        zip_files = list(output_dir.glob('*.zip'))
        self.assertEqual(len(zip_files), 1, 'Expected exactly one ZIP file')
        
        with zipfile.ZipFile(zip_files[0]) as zf:
            names = set(zf.namelist())
            self.assertIn('index.html', names, 'index.html must be present')
            self.assertIn('asset-manifest.json', names, 'asset-manifest.json must be present')

    def test_no_duplicate_members(self):
        """Verify ZIP contains no duplicate member names."""
        html = self.create_minimal_offline_html()
        offline = self.temp_dir / 'offline.html'
        offline.write_text(html)
        output_dir = self.temp_dir / 'output'
        expected_sha = hashlib.sha256(html.encode()).hexdigest()
        
        self.run_package_web(offline, output_dir, expected_sha)
        
        zip_files = list(output_dir.glob('*.zip'))
        with zipfile.ZipFile(zip_files[0]) as zf:
            members = zf.infolist()
            names = [m.filename for m in members]
            self.assertEqual(len(names), len(set(names)), 
                           'ZIP must not contain duplicate members')

    def test_only_allowed_paths(self):
        """Verify all paths are index.html, .nojekyll, asset-manifest.json, or in assets/."""
        html = self.create_minimal_offline_html()
        offline = self.temp_dir / 'offline.html'
        offline.write_text(html)
        output_dir = self.temp_dir / 'output'
        expected_sha = hashlib.sha256(html.encode()).hexdigest()
        
        self.run_package_web(offline, output_dir, expected_sha)
        
        zip_files = list(output_dir.glob('*.zip'))
        with zipfile.ZipFile(zip_files[0]) as zf:
            for member in zf.infolist():
                name = member.filename
                path = Path(name)
                allowed = (
                    name in {'index.html', '.nojekyll', 'asset-manifest.json'} or
                    (len(path.parts) > 1 and path.parts[0] == 'assets')
                )
                self.assertTrue(allowed, f'Unexpected member: {name}')

    def test_no_unsafe_paths(self):
        """Verify no absolute, parent (..), or backslash paths."""
        html = self.create_minimal_offline_html()
        offline = self.temp_dir / 'offline.html'
        offline.write_text(html)
        output_dir = self.temp_dir / 'output'
        expected_sha = hashlib.sha256(html.encode()).hexdigest()
        
        self.run_package_web(offline, output_dir, expected_sha)
        
        zip_files = list(output_dir.glob('*.zip'))
        with zipfile.ZipFile(zip_files[0]) as zf:
            for member in zf.infolist():
                name = member.filename
                path = Path(name)
                self.assertFalse(path.is_absolute(), 
                               f'Path must not be absolute: {name}')
                self.assertNotIn('..', path.parts, 
                               f'Path must not contain ..: {name}')
                self.assertNotIn('\\', name, 
                               f'Path must not contain backslash: {name}')

    def test_regular_files_only(self):
        """Verify ZIP contains only regular files, not directories or symlinks."""
        html = self.create_minimal_offline_html()
        offline = self.temp_dir / 'offline.html'
        offline.write_text(html)
        output_dir = self.temp_dir / 'output'
        expected_sha = hashlib.sha256(html.encode()).hexdigest()
        
        self.run_package_web(offline, output_dir, expected_sha)
        
        zip_files = list(output_dir.glob('*.zip'))
        with zipfile.ZipFile(zip_files[0]) as zf:
            for member in zf.infolist():
                self.assertFalse(member.is_dir(), 
                               f'Member must not be a directory: {member.filename}')
                # Check external_attr for file type
                file_type = stat.S_IFMT(member.external_attr >> 16)
                self.assertIn(file_type, {0, stat.S_IFREG}, 
                            f'Member must be a regular file: {member.filename}')

    def test_checksums_and_sizes_match(self):
        """Verify manifest checksums and byte counts match actual file contents."""
        html = self.create_minimal_offline_html()
        offline = self.temp_dir / 'offline.html'
        offline.write_text(html)
        output_dir = self.temp_dir / 'output'
        expected_sha = hashlib.sha256(html.encode()).hexdigest()
        
        self.run_package_web(offline, output_dir, expected_sha)
        
        zip_files = list(output_dir.glob('*.zip'))
        with zipfile.ZipFile(zip_files[0]) as zf:
            manifest_content = zf.read('asset-manifest.json')
            manifest = json.loads(manifest_content)
            
            # Build expected inventory from manifest
            expected = {row['path']: row for row in manifest['files']}
            
            # Verify manifest doesn't list itself
            self.assertNotIn('asset-manifest.json', expected)
            
            # Verify all members except asset-manifest.json
            for member in zf.infolist():
                if member.filename == 'asset-manifest.json':
                    continue
                    
                content = zf.read(member.filename)
                row = expected.get(member.filename)
                
                self.assertIsNotNone(row, 
                                   f'Member {member.filename} not in manifest')
                self.assertEqual(len(content), row['bytes'], 
                               f'Size mismatch for {member.filename}')
                actual_sha = hashlib.sha256(content).hexdigest()
                self.assertEqual(actual_sha, row['sha256'], 
                               f'Checksum mismatch for {member.filename}')

    def test_manifest_covers_all_members(self):
        """Verify asset-manifest.json lists all ZIP members except itself."""
        html = self.create_minimal_offline_html()
        offline = self.temp_dir / 'offline.html'
        offline.write_text(html)
        output_dir = self.temp_dir / 'output'
        expected_sha = hashlib.sha256(html.encode()).hexdigest()
        
        self.run_package_web(offline, output_dir, expected_sha)
        
        zip_files = list(output_dir.glob('*.zip'))
        with zipfile.ZipFile(zip_files[0]) as zf:
            names = set(zf.namelist())
            manifest_content = zf.read('asset-manifest.json')
            manifest = json.loads(manifest_content)
            manifest_paths = {row['path'] for row in manifest['files']}
            
            expected_in_manifest = names - {'asset-manifest.json'}
            self.assertEqual(manifest_paths, expected_in_manifest, 
                           'Manifest must list all members except itself')


if __name__ == '__main__':
    unittest.main()
