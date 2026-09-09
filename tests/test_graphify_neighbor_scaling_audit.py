"""Exact-output checks for the synthetic host prototype; no skill mutation."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'evaluations/audit_graphify_neighbor_scaling.py'
spec = importlib.util.spec_from_file_location('graphify_scaling_audit', SOURCE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class NeighborParityChecks(unittest.TestCase):
    def test_seeded_sparse_dense_partition_and_neighbor_variations(self):
        for neighbors in (1, 2, 4):
            original, proposed, _ = audit.load_functions(neighbors=neighbors)
            for seed in range(12):
                for partitions in (1, 2, 7):
                    for dense in (False, True):
                        records = audit.synthetic_records(seed * 3, seed, partitions=partitions, dense=dense)
                        with self.subTest(neighbors=neighbors, seed=seed, partitions=partitions, dense=dense):
                            self.assertEqual(original(records), proposed(records))
                            self.assertEqual(original(reversed(records)), proposed(reversed(records)))

    def test_empty_single_zero_norm_no_overlap_and_exact_ties(self):
        fixtures = [[], [{}], [{'concept_path': f'{i}.md'} for i in range(6)],
                    [{'concept_path': f'{i}.md', 'title': f'unique{i}'} for i in range(6)],
                    [{'concept_path': f'{i}.md', 'title': 'identical text'} for i in range(6)],
                    [{'concept_path': f'{i}.md', 'record_id': f'root/{i}', 'title': 'identical text'} for i in range(6)]]
        for neighbors in (1, 3, 10):
            original, proposed, _ = audit.load_functions(neighbors=neighbors)
            for fixture in fixtures:
                with self.subTest(neighbors=neighbors, size=len(fixture)):
                    self.assertEqual(original(fixture), proposed(fixture))

    def test_neighbor_bound_requires_positive_integer(self):
        for value in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                audit.load_functions(neighbors=value)

    def test_benchmark_declares_synthetic_scope_and_exact_bindings(self):
        result = audit.benchmark([8], 2)
        self.assertTrue(result['synthetic_only'])
        self.assertFalse(result['source_modified'])
        self.assertEqual(result['native_trials'], 0)
        self.assertEqual(result['candidate_bundles'], 0)
        self.assertFalse(result['retrieval_quality_measured'])
        self.assertTrue(all(len(digest) == 64 for digest in result['bindings'].values()))
        row = result['rows'][0]
        self.assertEqual(row['original_dense_score_slots'], 28)
        self.assertEqual(row['original_dense_endpoint_checks'], 224)
        self.assertEqual(row['prototype_retained_neighbor_bound'], 8)
        self.assertGreater(row['ratio_original_to_prototype'], 0)
