#!/usr/bin/env python3
"""Tests for site/virtual-poster/match_reference_colors.py."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'site' / 'virtual-poster'))

import match_reference_colors


def sha256(data):
    """Helper to compute SHA256 hash."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


class TestMatchReferenceColors(unittest.TestCase):
    """Test match_reference_colors.py with synthetic fixtures."""

    def setUp(self):
        """Create temporary directory for each test."""
        import tempfile as _tempfile
        self.base_temp_dir = _tempfile.mkdtemp()
        # Create a structure similar to the real repo: <temp>/site/virtual-poster
        self.here_path = Path(self.base_temp_dir) / 'site' / 'virtual-poster'
        self.here_path.mkdir(parents=True, exist_ok=True)
        self.temp_path = self.here_path

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.base_temp_dir, ignore_errors=True)

    def create_minimal_html(self, data_json):
        """Create a minimal HTML file with poster data."""
        return f'''<!DOCTYPE html>
<html>
<body>
<script id="poster-data" type="application/json">{json.dumps(data_json, indent=2)}</script>
</body>
</html>'''

    def test_input_sha_mismatch_raises(self):
        """Verify that input SHA256 mismatch raises ValueError."""
        data = {
            'targets': {
                'Adk': {
                    'references': [
                        {'pdb_id': '4AKE', 'color': '#D6001C'},
                        {'pdb_id': '1AKE', 'color': '#008A3B'}
                    ],
                    'trees': {'animation': {'image': 'data:image/svg+xml;base64,PHN2ZyBmaWxsPSIjRDYwMDFDIi8+'}}
                }
            }
        }
        html = self.create_minimal_html(data)
        html_bytes = html.encode('utf-8')
        input_file = self.temp_path / 'input.html'
        input_file.write_bytes(html_bytes)
        
        # Create physical poster at HERE.parents[1] / 'poster/final/dummy.png'
        # HERE = self.temp_path = <base>/site/virtual-poster
        # HERE.parents[1] = <base>
        base_dir = Path(self.base_temp_dir)
        physical_bytes = b'dummy_physical'
        physical_preview_rel = 'poster/final/dummy.png'
        physical_file = base_dir / physical_preview_rel
        physical_file.parent.mkdir(parents=True, exist_ok=True)
        physical_file.write_bytes(physical_bytes)
        
        # Create a reference-colors.json with wrong predecessor SHA
        ref_colors = {
            'predecessor_sha256': 'wrong_hash',
            'physical_poster': {
                'preview': physical_preview_rel,
                'sha256': sha256(physical_bytes)
            },
            'references': {
                '4AKE': {'color': '#1f77b4', 'previous_color': '#D6001C'},
                '1AKE': {'color': '#ff7f0e', 'previous_color': '#008A3B'}
            }
        }
        ref_file = self.temp_path / 'reference-colors.json'
        ref_file.write_text(json.dumps(ref_colors))
        
        output_file = self.temp_path / 'output.html'
        
        # Patch HERE and sys.argv
        original_here = match_reference_colors.HERE
        original_argv = sys.argv
        try:
            match_reference_colors.HERE = self.temp_path
            sys.argv = ['match_reference_colors.py', '--input', str(input_file), '--output', str(output_file)]
            
            with self.assertRaises(ValueError) as ctx:
                match_reference_colors.main()
            
            self.assertIn('predecessor', str(ctx.exception).lower())
        finally:
            match_reference_colors.HERE = original_here
            sys.argv = original_argv

    def test_unexpected_predecessor_color_raises(self):
        """Verify that unexpected predecessor color raises ValueError."""
        data = {
            'targets': {
                'Adk': {
                    'references': [
                        {'pdb_id': '4AKE', 'color': '#WRONGCOLOR'}  # Wrong predecessor color
                    ],
                    'trees': {'animation': {'image': 'data:image/svg+xml;base64,PHN2ZyBmaWxsPSIjRDYwMDFDIi8+'}}
                }
            }
        }
        html = self.create_minimal_html(data)
        html_bytes = html.encode('utf-8')
        input_file = self.temp_path / 'input.html'
        input_file.write_bytes(html_bytes)
        
        # Create physical poster at HERE.parents[1] / preview_rel
        base_dir = Path(self.base_temp_dir)
        physical_bytes = b'dummy_physical'
        physical_preview_rel = 'poster/final/dummy.png'
        physical_file = base_dir / physical_preview_rel
        physical_file.parent.mkdir(parents=True, exist_ok=True)
        physical_file.write_bytes(physical_bytes)
        
        # Create matching reference-colors.json
        ref_colors = {
            'predecessor_sha256': sha256(html_bytes),
            'physical_poster': {
                'preview': physical_preview_rel,
                'sha256': sha256(physical_bytes)
            },
            'references': {
                '4AKE': {'color': '#1f77b4', 'previous_color': '#D6001C'}  # Expected old color
            }
        }
        ref_file = self.temp_path / 'reference-colors.json'
        ref_file.write_text(json.dumps(ref_colors))
        
        output_file = self.temp_path / 'output.html'
        
        # Patch sys.argv and HERE
        original_argv = sys.argv
        original_here = match_reference_colors.HERE
        try:
            sys.argv = ['match_reference_colors.py', '--input', str(input_file), '--output', str(output_file)]
            match_reference_colors.HERE = self.temp_path
            
            with self.assertRaises(ValueError) as ctx:
                match_reference_colors.main()
            
            self.assertIn('predecessor color', str(ctx.exception).lower())
        finally:
            sys.argv = original_argv
            match_reference_colors.HERE = original_here

    def test_existing_output_refuses_to_overwrite(self):
        """Verify that existing output or validation file raises FileExistsError."""
        data = {
            'targets': {
                'Adk': {
                    'references': [{'pdb_id': '4AKE', 'color': '#D6001C'}],
                    'trees': {'animation': {'image': 'data:image/svg+xml;base64,PHN2ZyBmaWxsPSIjRDYwMDFDIi8+'}}
                }
            }
        }
        html = self.create_minimal_html(data)
        html_bytes = html.encode('utf-8')
        input_file = self.temp_path / 'input.html'
        input_file.write_bytes(html_bytes)
        
        output_file = self.temp_path / 'output.html'
        output_file.write_text('existing')  # Create existing output
        
        # Create physical poster at HERE.parents[1] / preview_rel
        base_dir = Path(self.base_temp_dir)
        physical_bytes = b'dummy_physical'
        physical_preview_rel = 'poster/final/dummy.png'
        physical_file = base_dir / physical_preview_rel
        physical_file.parent.mkdir(parents=True, exist_ok=True)
        physical_file.write_bytes(physical_bytes)
        
        ref_colors = {
            'predecessor_sha256': sha256(html_bytes),
            'physical_poster': {
                'preview': physical_preview_rel,
                'sha256': sha256(physical_bytes)
            },
            'references': {'4AKE': {'color': '#1f77b4', 'previous_color': '#D6001C'}}
        }
        ref_file = self.temp_path / 'reference-colors.json'
        ref_file.write_text(json.dumps(ref_colors))
        
        original_argv = sys.argv
        original_here = match_reference_colors.HERE
        try:
            sys.argv = ['match_reference_colors.py', '--input', str(input_file), '--output', str(output_file)]
            match_reference_colors.HERE = self.temp_path
            
            with self.assertRaises(FileExistsError) as ctx:
                match_reference_colors.main()
            
            self.assertIn('output', str(ctx.exception).lower())
        finally:
            sys.argv = original_argv
            match_reference_colors.HERE = original_here

    def test_happy_path_changes_colors_and_writes_validation(self):
        """Test successful color replacement and validation report generation."""
        import base64
        
        # Create two different SVGs (one for each target), each with both fills
        svg_adk = '<svg id="adk" xmlns="http://www.w3.org/2000/svg"><rect fill="#D6001C"/><circle fill="#008A3B"/></svg>'
        svg_adk_b64 = base64.b64encode(svg_adk.encode()).decode('ascii')
        svg_adk_uri = f'data:image/svg+xml;base64,{svg_adk_b64}'
        
        svg_mad2 = '<svg id="mad2" xmlns="http://www.w3.org/2000/svg"><rect fill="#D6001C"/><circle fill="#008A3B"/></svg>'
        svg_mad2_b64 = base64.b64encode(svg_mad2.encode()).decode('ascii')
        svg_mad2_uri = f'data:image/svg+xml;base64,{svg_mad2_b64}'
        
        # Need 2 targets (Adk and Mad2) with 2 references each for 4 total changes
        data = {
            'targets': {
                'Adk': {
                    'references': [
                        {'pdb_id': '4AKE', 'color': '#D6001C'},
                        {'pdb_id': '1AKE', 'color': '#008A3B'}
                    ],
                    'trees': {
                        'animation': {
                            'image': svg_adk_uri
                        }
                    }
                },
                'Mad2': {
                    'references': [
                        {'pdb_id': '1DUJ', 'color': '#D6001C'},
                        {'pdb_id': '1S2H', 'color': '#008A3B'}
                    ],
                    'trees': {
                        'animation': {
                            'image': svg_mad2_uri
                        }
                    }
                }
            }
        }
        html = self.create_minimal_html(data)
        # Each SVG URI must appear exactly twice total (once in JSON, once more outside)
        # Add one copy of each SVG outside the JSON
        html = html.replace('</body>', 
                           f'<img class="adk-extra" src="{svg_adk_uri}">'
                           f'<img class="mad2-extra" src="{svg_mad2_uri}">'
                           '</body>')
        html_bytes = html.encode('utf-8')
        
        input_file = self.temp_path / 'input.html'
        input_file.write_bytes(html_bytes)
        
        # Create physical poster at HERE.parents[1] / preview_rel
        base_dir = Path(self.base_temp_dir)
        physical_bytes = b'dummy_physical_poster'
        physical_preview_rel = 'poster/final/dummy.png'
        physical_file = base_dir / physical_preview_rel
        physical_file.parent.mkdir(parents=True, exist_ok=True)
        physical_file.write_bytes(physical_bytes)
        
        # Create matching reference-colors.json
        ref_colors = {
            'predecessor_sha256': sha256(html_bytes),
            'physical_poster': {
                'preview': physical_preview_rel,
                'sha256': sha256(physical_bytes)
            },
            'references': {
                '4AKE': {'color': '#1f77b4', 'previous_color': '#D6001C'},
                '1AKE': {'color': '#ff7f0e', 'previous_color': '#008A3B'},
                '1DUJ': {'color': '#1f77b4', 'previous_color': '#D6001C'},
                '1S2H': {'color': '#ff7f0e', 'previous_color': '#008A3B'}
            }
        }
        ref_file = self.temp_path / 'reference-colors.json'
        ref_file.write_text(json.dumps(ref_colors))
        
        output_file = self.temp_path / 'output.html'
        
        # Run the script
        original_argv = sys.argv
        original_here = match_reference_colors.HERE
        try:
            sys.argv = ['match_reference_colors.py', '--input', str(input_file), '--output', str(output_file)]
            match_reference_colors.HERE = self.temp_path
            
            match_reference_colors.main()
        finally:
            sys.argv = original_argv
            match_reference_colors.HERE = original_here
        
        # Verify output file exists
        self.assertTrue(output_file.exists(), "Output file should be created")
        
        # Verify validation report exists
        validation_file = output_file.with_suffix('.validation.json')
        self.assertTrue(validation_file.exists(), "Validation report should be created")
        
        # Load and check validation report
        validation = json.loads(validation_file.read_text())
        self.assertEqual(validation['status'], 'PASS_REFERENCE_COLOR_FIELDS_AND_SVG_FILLS_ONLY')
        self.assertEqual(len(validation['reference_color_changes']), 4)
        self.assertTrue(validation['all_other_source_bytes_unchanged'])
        
        # Verify colors were changed in output
        output_text = output_file.read_text()
        self.assertIn('#1f77b4', output_text, "New color for 4AKE/1DUJ should be present")
        self.assertIn('#ff7f0e', output_text, "New color for 1AKE/1S2H should be present")
        self.assertNotIn('#D6001C', output_text, "Old color for 4AKE/1DUJ should be replaced")
        self.assertNotIn('#008A3B', output_text, "Old color for 1AKE/1S2H should be replaced")


if __name__ == '__main__':
    unittest.main()
