"""Require full-corpus execution to preserve the independent native scorer."""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('full_corpus_classical_test', ROOT / 'evaluations/enterprise-rag-bench/full_corpus_classical.py')
ADAPTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ADAPTER
SPEC.loader.exec_module(ADAPTER)
NATIVE = ADAPTER.native(ROOT / 'skills/consult-semantic-okf-classical')


def plan():
    """Load the unchanged canonical Classical plan factory."""
    path = ROOT / 'evaluations/private-book-strategy-comparison/scripts/prepare_strategy_bundles.py'
    factory = ADAPTER.module('full_classical_test_plans', path)
    return factory.classical_plan(['source-a'])


def records():
    """Exercise repeated terms, field weighting, ties, Unicode and empty bags."""
    for number, (title, body) in enumerate([
        ('Alpha service', 'alpha alpha beta gamma ' * 25),
        ('Beta gamma', 'alpha beta'), ('Beta gamma', 'alpha beta'),
        ('Rollback guide', 'release rollback steps red blue green'),
        ('Café Straße', 'Unicode café Straße CASEFOLD evidence'),
        ('A', 'a the and or'), ('Alpha beta', 'unrelated body'),
        *[(f'Record {i}', f'alpha beta {i} ' * (i+1)) for i in range(20)],
    ]):
        identity = f'record-{number}'
        record = {'source_id': 'source-a', 'record_id': identity,
                  'record_sha256': hashlib.sha256(identity.encode()).hexdigest(),
                  'concept_id': f'concepts/source-a/{identity}',
                  'concept_path': f'concepts/source-a/{identity}.md',
                  'concept_type': 'document', 'source_path': 'input.jsonl',
                  'title': title, 'body': body, 'attributes': {}}
        original = {'upstream_id': identity, 'upstream_path': 'input.jsonl',
                    'raw_sha256': hashlib.sha256(body.encode()).hexdigest(),
                    'raw_body': body, 'colliding_id': False}
        yield record, original


@pytest.fixture
def indexed(tmp_path):
    target = tmp_path / 'index'
    rows = list(records())
    selected_plan = plan()
    ADAPTER.build_index(iter(rows), target, selected_plan, NATIVE, batch_size=3)
    return target, rows, selected_plan


def test_exact_native_rankings_scores_and_evidence_across_blocks(indexed):
    target, rows, selected_plan = indexed
    docs = NATIVE._derive_documents([r for r, _ in rows], selected_plan)
    lexicon = NATIVE._derive_lexicon(docs, selected_plan)
    index = ADAPTER.Index(target, NATIVE)
    try:
        assert index.meta['average_field_lengths'] == lexicon['average_field_lengths']
        for query in ['alpha', 'alpha alpha beta', 'beta gamma', 'rollback release',
                      'Café STRASSE', 'unrelated body', 'and the', 'missingzzzz', 'alpha 12', 'guide']:
            weights = {k: float(v) for k, v in Counter(NATIVE.tokenize(query, selected_plan)).items()}
            scores = NATIVE._bm25_scores(docs, weights, lexicon, selected_plan)
            for count in [1, 3, 10, 27]:
                actual = index.search(query, count)
                assert [r['document_id'] for r in actual] == NATIVE._rank(scores)[:count]
                assert [r['score'] for r in actual] == [scores[r['document_id']] for r in actual]
                for hit in actual:
                    assert hashlib.sha256(hit['text'].encode()).hexdigest() == hit['text_sha256']
    finally:
        index.close()
    assert all(ADAPTER.sha(target / p) == h for p, h in index.meta['files'].items())


def test_index_rejects_overwrite_and_tampering(indexed):
    target, rows, selected_plan = indexed
    with pytest.raises(FileExistsError):
        ADAPTER.build_index(iter(rows), target, selected_plan, NATIVE)
    with (target / 'documents.sqlite').open('ab') as stream:
        stream.write(b'changed')
    with pytest.raises(ValueError, match='changed'):
        ADAPTER.Index(target, NATIVE)


def test_invalid_cutoff_and_empty_query_fail(indexed):
    target, _, _ = indexed
    index = ADAPTER.Index(target, NATIVE)
    try:
        for query, limit in [(' ', 10), ('alpha', 0), ('alpha', True), ('alpha', 1001)]:
            with pytest.raises(ValueError):
                index.search(query, limit)
    finally:
        index.close()


def test_json_output_is_append_only_and_finite(tmp_path):
    path = tmp_path / 'receipt.json'
    ADAPTER.write_json(path, {'value': 1})
    with pytest.raises(FileExistsError):
        ADAPTER.write_json(path, {'value': 2})
    assert json.loads(path.read_text()) == {'value': 1}
    with pytest.raises(ValueError):
        ADAPTER.write_json(tmp_path / 'invalid.json', {'value': float('nan')})
