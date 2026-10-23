"""Normalize completed, independently verified pair scores for the poster adapter.

No execution on import. No scoring, structure parsing, source-file mutation,
normalization of score values, or positional joins. Caller explicitly invokes
only after the root grants the completed-score/export GO.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

VIEWS = {'Adk': ('7X7S', 214), 'Mad2': ('Mad2', 197)}
PARENT_SHA256 = '5468a4c75868b6dfb20fa0f1b212f370983353d4a3ce0c643711fc8e95d1e2b0'
DEFINITION = 'mean_bidirectional_USalign_TM_average_length_normalized_full_CA'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(pairs_path, table_path, completion_path, independent_path):
    """Return guarded expected/measured objects and a small provenance receipt."""
    paths = [Path(p) for p in [pairs_path, table_path, completion_path, independent_path]]
    pairs_path, table_path, completion_path, independent_path = paths
    pairs = json.loads(pairs_path.read_text())
    completion = json.loads(completion_path.read_text())
    independent = json.loads(independent_path.read_text())
    assert pairs['status'] == 'READ_ONLY_VERIFIED' and pairs['pair_count'] == 22000
    assert completion['status'] == independent['status'] == 'PASS'
    assert completion['pairs'] == 22000 and completion['directional_calls'] == 44000
    assert completion['normalization'] == 'mean_bidirectional_average_length_usalign'
    assert completion['full_residues'] == {'Adk': 214, 'Mad2': 197}
    assert sha(table_path) == completion['score_table_sha256']
    expected = {'status': 'PASS', 'parent_html_sha256': PARENT_SHA256, 'targets': {}}
    measured = {'status': 'PASS', 'metric_definition': DEFINITION, 'targets': {}}
    expected_lookup = {}
    for target, (view, count) in VIEWS.items():
        source = pairs['targets'][target]
        assert source['view_key'] == view and source['full_residue_count'] == count
        expected['targets'][view] = {'ca_count': count, 'rows': []}
        measured['targets'][view] = {'ca_count': count, 'rows': []}
    for row in pairs['pairs']:
        view, count = VIEWS[row['target']]
        assert row['view_key'] == view and row['residue_count'] == count
        key = (view, row['model'])
        assert key not in expected_lookup
        expected_lookup[key] = row
        expected['targets'][view]['rows'].append({'model_id': row['model'],
            'ais_sha256': row['original_sha256'], 'refold_sha256': row['refold_sha256']})
    seen = set()
    with table_path.open(newline='') as stream:
        for row in csv.DictReader(stream):
            view, count = VIEWS[row['target']]
            key = (view, row['model'])
            assert key in expected_lookup and key not in seen
            pair = expected_lookup[key]
            assert row['view_key'] == view and int(row['residue_count']) == count
            for field in ['original_sha256', 'refold_sha256', 'sequence_sha256', 'method']:
                assert row[field] == pair[field], (key, field)
            forward, reverse, value = [float(row[field]) for field in
                ['original_to_refold_TM', 'refold_to_original_TM', 'mean_bidirectional_TM']]
            assert all(math.isfinite(v) and 0 <= v <= 1 for v in [forward, reverse, value])
            assert value == (forward + reverse) / 2, key
            measured['targets'][view]['rows'].append({'model_id': row['model'],
                'ais_sha256': row['original_sha256'], 'refold_sha256': row['refold_sha256'],
                'ais_refold_tm': value})
            seen.add(key)
    assert seen == set(expected_lookup) and len(seen) == 22000
    assert all(len(v['rows']) == 11000 for v in measured['targets'].values())
    receipt = {'status': 'PASS', 'pairs': 22000, 'model_id_and_both_source_hashes_exact': True,
        'score_values_unchanged': True, 'directional_mean_verified': True,
        'full_CA_counts': dict((view, count) for view, count in VIEWS.values()),
        'source_pins': {str(path): sha(path) for path in paths}}
    return expected, measured, receipt
