#!/usr/bin/env python3
"""Match four reference display colors to the physical poster, preserving data."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    palette = json.loads((HERE / 'reference-colors.json').read_text())
    original = args.input.read_bytes()
    if sha(original) != palette['predecessor_sha256']:
        raise ValueError('Input differs from the reviewed v036 predecessor')
    physical = HERE.parents[1] / palette['physical_poster']['preview']
    if sha(physical.read_bytes()) != palette['physical_poster']['sha256']:
        raise ValueError('Physical poster preview differs from final v014')
    report_path = args.output.with_suffix('.validation.json')
    if args.output.exists() or report_path.exists():
        raise FileExistsError('Immutable output or validation already exists')
    text = original.decode('utf-8')
    block = re.search(r'(<script\b[^>]*\bid="poster-data"[^>]*>)(.*?)(</script>)', text, re.S)
    if block is None:
        raise ValueError('Missing poster-data block')
    before = json.loads(block[2])
    expected = copy.deepcopy(before)
    updated = block[2]
    changes = []
    for target, data in expected['targets'].items():
        for reference in data['references']:
            pdb = reference['pdb_id']
            entry = palette['references'][pdb]
            old, new = reference['color'], entry['color']
            if old != entry['previous_color']:
                raise ValueError('Unexpected predecessor color for ' + pdb)
            pattern = r'("pdb_id"\s*:\s*"' + pdb + r'"[^{}]*?"color"\s*:\s*)"' + re.escape(old) + r'"'
            updated, count = re.subn(pattern, lambda m: m[1] + '"' + new + '"', updated)
            if count != 1:
                raise ValueError('Expected exactly one reference color for ' + pdb)
            reference['color'] = new
            changes.append({'target': target, 'pdb_id': pdb, 'before': old, 'after': new})
    svg_changes = []
    for target, data in expected['targets'].items():
        uri = data['trees']['animation']['image']
        prefix, encoded = uri.split(',', 1)
        if prefix != 'data:image/svg+xml;base64':
            raise ValueError('Expected an embedded SVG tree')
        raw = base64.b64decode(encoded, validate=True)
        recolored = raw
        for old, new in [('#D6001C', '#1f77b4'), ('#008A3B', '#ff7f0e')]:
            old_fill = ('fill="' + old + '"').encode()
            if recolored.count(old_fill) != 1:
                raise ValueError('Expected one SVG reference fill for ' + target)
            recolored = recolored.replace(old_fill, ('fill="' + new + '"').encode())
        new_uri = prefix + ',' + base64.b64encode(recolored).decode('ascii')
        occurrences = text.count(uri)
        if occurrences != 2:
            raise ValueError('Expected dashboard and supporting figure SVG copies')
        svg_changes.append({'target': target, 'before_uri': uri, 'after_uri': new_uri,
                            'before_sha256': sha(raw), 'after_sha256': sha(recolored),
                            'occurrences': occurrences})
        data['trees']['animation']['image'] = new_uri
        updated = updated.replace(uri, new_uri)
    if len(changes) != 4 or json.loads(updated) != expected:
        raise ValueError('Changes exceed the approved reference colors and tree SVGs')
    result = text[:block.start(2)] + updated + text[block.end(2):]
    for svg in svg_changes:
        result = result.replace(svg['before_uri'], svg['after_uri'])
    restored = result
    for svg in svg_changes:
        restored = restored.replace(svg['after_uri'], svg['before_uri'])
    for change in changes:
        pattern = r'("pdb_id"\s*:\s*"' + change['pdb_id'] + r'"[^{}]*?"color"\s*:\s*)"' + change['after'] + r'"'
        restored, count = re.subn(pattern, lambda m: m[1] + '"' + change['before'] + '"', restored)
        if count != 1:
            raise ValueError('Reference-color round trip failed')
    if restored != text:
        raise ValueError('Unrelated source bytes changed')
    output = result.encode('utf-8')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    report = {
        'status': 'PASS_REFERENCE_COLOR_FIELDS_AND_SVG_FILLS_ONLY',
        'predecessor_sha256': sha(original), 'output_sha256': sha(output),
        'output_bytes': len(output), 'reference_color_changes': changes,
        'all_other_source_bytes_unchanged': True,
        'scientific_coordinates_and_scores_unchanged': True,
        'all_executable_scripts_and_other_media_unchanged': True,
        'bonsai_svg_changes': [{k: v for k, v in svg.items() if not k.endswith('_uri')}
                              for svg in svg_changes],
        'physical_poster': palette['physical_poster'],
        'poster_data_sha256': sha(updated.encode('utf-8')),
    }
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
