#!/usr/bin/env python3
"""Tests for site/netlify-landing hub source consistency."""
import json
from pathlib import Path
import re
import unittest

REPO = Path(__file__).resolve().parents[1]
LANDING_DIR = REPO / 'site' / 'netlify-landing'


class TestNetlifyLanding(unittest.TestCase):
    """Verify hub source doesn't regress Mad2 PDB ID and maintains consistency."""

    def test_mad2_pdb_id_is_1duj_not_1klq(self):
        """Mad2 PDB ID must be 1DUJ, not 1KLQ, to match live site and owner decision."""
        index_html = (LANDING_DIR / 'index.html').read_text()
        links_json = json.loads((LANDING_DIR / 'links.json').read_text())
        
        # Check that 1KLQ is not mentioned anywhere
        self.assertNotIn('1KLQ', index_html, 
                         "index.html must not reference Mad2 as 1KLQ")
        self.assertNotIn('1KLQ', json.dumps(links_json),
                         "links.json must not reference Mad2 as 1KLQ")
        
        # Check that 1DUJ is present in the expected locations
        self.assertIn('Mad2, 1DUJ', index_html,
                      "index.html must reference Mad2 as 1DUJ")
        self.assertIn('Mad2, 1DUJ', links_json['description'],
                      "links.json description must reference Mad2 as 1DUJ")

    def test_button_hrefs_consistent_with_links_json(self):
        """Verify index.html button hrefs and labels match links.json."""
        index_html = (LANDING_DIR / 'index.html').read_text()
        links_json = json.loads((LANDING_DIR / 'links.json').read_text())
        
        for link in links_json['links']:
            # Skip coming_soon links as they may not be in HTML yet
            if link.get('status') != 'live':
                continue
            
            url = link['url']
            label = link['label']
            
            # Check that the URL appears in the HTML
            self.assertIn(url, index_html,
                          f"URL {url} from links.json must appear in index.html")
            
            # Check that the label appears in the HTML
            self.assertIn(label, index_html,
                          f"Label '{label}' from links.json must appear in index.html")
            
            # For the Mad2 Zenodo link specifically, verify the label includes (1DUJ)
            if link['id'] == 'Zenodo.Mad2_resources':
                self.assertIn('Mad2 (1DUJ)', label,
                              "Mad2 Zenodo button label must include (1DUJ)")
                # Verify the button in HTML has both the label and the URL
                button_pattern = re.search(
                    r'<a[^>]+href="' + re.escape(url) + r'"[^>]*>.*?' + 
                    re.escape('Mad2 (1DUJ)') + r'.*?</a>',
                    index_html, re.DOTALL)
                self.assertIsNotNone(button_pattern,
                                     "Mad2 button in HTML must have correct URL and (1DUJ) label")


if __name__ == '__main__':
    unittest.main()
