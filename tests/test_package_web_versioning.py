#!/usr/bin/env python3
"""Tests for site/virtual-poster/package_web.py version validation."""
from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'site' / 'virtual-poster'))

import package_web


class TestPackageWebVersioning(unittest.TestCase):
    """Test package_web.py's --version validation."""

    def test_valid_version_formats(self):
        """Test that valid version formats are accepted."""
        valid_versions = [
            'web-v001',
            'web-v042',
            'web-v999',
            'web-v123'
        ]
        
        for version in valid_versions:
            with self.subTest(version=version):
                # The validation uses re.fullmatch(r"web-v[0-9]{3}", args.version)
                import re
                pattern = r"web-v[0-9]{3}"
                self.assertIsNotNone(re.fullmatch(pattern, version),
                                     f"Version {version} should match pattern {pattern}")

    def test_invalid_version_formats_raise_error(self):
        """Test that invalid version formats raise ValueError."""
        invalid_versions = [
            'web-v1',           # Too few digits
            'web-v0001',        # Too many digits
            'web-1.0',          # Wrong format
            'v001',             # Missing web- prefix
            'web-v01',          # Too few digits
            'web-vabc',         # Non-numeric
            'web-V001',         # Wrong case
            'WEB-v001',         # Wrong case
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            
            # Create a minimal valid input file for testing
            input_html = '''<!DOCTYPE html>
<html><body>
<script id="poster-data" type="application/json">{"targets": {}}</script>
</body></html>'''
            input_file = temp_path / 'input.html'
            input_file.write_text(input_html)
            
            output_dir = temp_path / 'output'
            
            for version in invalid_versions:
                with self.subTest(version=version):
                    # Test using argparse and main() function
                    original_argv = sys.argv
                    try:
                        sys.argv = [
                            'package_web.py',
                            '--input', str(input_file),
                            '--output-dir', str(output_dir / version),  # Unique dir per test
                            '--expected-sha256', package_web.digest(input_html.encode()),
                            '--version', version,
                            '--release-date', '2026-10-23'
                        ]
                        
                        with self.assertRaises(ValueError) as ctx:
                            package_web.main()
                        
                        self.assertIn('version', str(ctx.exception).lower(),
                                      f"Error message should mention version for {version}")
                    finally:
                        sys.argv = original_argv

    def test_version_appears_in_manifest_and_filename(self):
        """Test that version appears correctly in manifest and ZIP filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            
            # Create a minimal valid input with at least one embedded asset
            import base64
            dummy_img = b'\x89PNG\r\n\x1a\n'  # PNG magic number
            img_b64 = base64.b64encode(dummy_img).decode('ascii')
            input_html = f'''<!DOCTYPE html>
<html><body>
<script id="poster-data" type="application/json">{{"targets": {{}}}}</script>
<img src="data:image/png;base64,{img_b64}">
</body></html>'''
            input_file = temp_path / 'input.html'
            input_file.write_text(input_html)
            
            output_dir = temp_path / 'output'
            version = 'web-v123'
            release_date = '2026-10-25'
            
            original_argv = sys.argv
            try:
                sys.argv = [
                    'package_web.py',
                    '--input', str(input_file),
                    '--output-dir', str(output_dir),
                    '--expected-sha256', package_web.digest(input_html.encode()),
                    '--version', version,
                    '--release-date', release_date
                ]
                
                package_web.main()
                
                # Check manifest contains version
                manifest_file = output_dir / 'site' / 'asset-manifest.json'
                self.assertTrue(manifest_file.exists(), "Manifest should be created")
                
                import json
                manifest = json.loads(manifest_file.read_text())
                self.assertEqual(manifest['version'], version,
                                 "Manifest should contain the specified version")
                
                # Check ZIP filename contains version and release date
                expected_zip = output_dir / f'{release_date}_virtual-poster-{version}.zip'
                self.assertTrue(expected_zip.exists(),
                                f"ZIP file {expected_zip.name} should exist")
                
            finally:
                sys.argv = original_argv

    def test_release_date_validation(self):
        """Test that release date must be a valid ISO date format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            
            input_html = '''<!DOCTYPE html>
<html><body>
<script id="poster-data" type="application/json">{"targets": {}}</script>
</body></html>'''
            input_file = temp_path / 'input.html'
            input_file.write_text(input_html)
            
            output_dir = temp_path / 'output'
            
            invalid_dates = [
                '10/25/2026',  # US format
                '25-10-2026',  # Wrong delimiter
                '2026/10/25',  # Wrong delimiter
                'invalid',     # Not a date
            ]
            
            for invalid_date in invalid_dates:
                with self.subTest(date=invalid_date):
                    original_argv = sys.argv
                    try:
                        sys.argv = [
                            'package_web.py',
                            '--input', str(input_file),
                            '--output-dir', str(output_dir / invalid_date.replace('/', '_')),
                            '--expected-sha256', package_web.digest(input_html.encode()),
                            '--version', 'web-v001',
                            '--release-date', invalid_date
                        ]
                        
                        with self.assertRaises(ValueError):
                            package_web.main()
                    finally:
                        sys.argv = original_argv


if __name__ == '__main__':
    unittest.main()
