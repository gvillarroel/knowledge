"""Sampling checks independent of private Enterprise question contents."""
from __future__ import annotations

import copy
import importlib.util
from collections import Counter
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1]/'evaluations/enterprise-stratified-evolution/dataset.py'
SPEC = importlib.util.spec_from_file_location('enterprise_stratified_dataset', SOURCE)
DATASET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DATASET)
SEED = '12'*32


def population():
    return [dict(question_id=f'{category}-{i}', question_type=category,
                 question=f'An independent fixture {i}', source_types=[f'app-{i%3}'],
                 expected_doc_ids=[] if category == 'none' else [f'doc-{i}'],
                 facts=['not part of sampling'])
            for category, size in [('large',20),('small',8),('none',12)] for i in range(size)]


def test_frozen_selection_is_order_independent_and_without_replacement():
    rows = population()
    before = copy.deepcopy(rows)
    selected = DATASET.stratified_sample(rows,SEED,{'large':8,'small':4,'none':4})
    assert selected == DATASET.stratified_sample(list(reversed(rows)),SEED,{'none':4,'small':4,'large':8})
    assert len({row['question_id'] for row in selected}) == 16
    assert rows == before
    assert Counter(row['question_type'] for row in selected) == {'large':8,'small':4,'none':4}


def test_blocks_balance_categories_and_design_weights_recover_populations():
    selected = DATASET.stratified_sample(population(),SEED,{'large':8,'small':4,'none':4})
    for block in range(4):
        assert Counter(row['question_type'] for row in selected if row['development_block'] == block) == {
            'large':2,'small':1,'none':1}
    for category,size in [('large',20),('small',8),('none',12)]:
        values = [r for r in selected if r['question_type'] == category]
        assert sum(r['population_to_sample_weight'] for r in values) == size
        assert all(r['population_to_sample_weight']*r['inclusion_probability'] == 1 for r in values)


def test_answers_scores_apps_and_evidence_do_not_change_selected_identities():
    original = population()
    changed = copy.deepcopy(original)
    for i,row in enumerate(changed):
        row.update(question='Changed prose', facts=['Changed answers'], observed_score=i,
                   source_types=['changed-app'], expected_doc_ids=['x','y','z'])
    keys = lambda rows: [(r['question_id'],r['development_block']) for r in
                         DATASET.stratified_sample(rows,SEED,{'large':8,'small':4,'none':4})]
    assert keys(original) == keys(changed)


@pytest.mark.parametrize('seed',['','0'*63,'F'*64,'z'*64])
def test_invalid_seed_fails_closed(seed):
    with pytest.raises(ValueError,match='seed'):
        DATASET.stratified_sample(population(),seed,{'large':8,'small':4,'none':4})


@pytest.mark.parametrize('quotas',[{'large':8,'small':4},
                                  {'large':24,'small':4,'none':4},
                                  {'large':6,'small':4,'none':4},
                                  {'large':0,'small':4,'none':4}])
def test_changed_categories_or_invalid_quotas_are_rejected(quotas):
    with pytest.raises(ValueError):
        DATASET.stratified_sample(population(),SEED,quotas)


def test_duplicate_questions_cannot_enter_selection():
    rows = population()
    with pytest.raises(ValueError,match='unique'):
        DATASET.stratified_sample(rows+[rows[0]],SEED,{'large':8,'small':4,'none':4})


def test_no_reference_questions_stay_in_query_population():
    rows = DATASET.stratified_sample(population(),SEED,{'large':8,'small':4,'none':4})
    assert sum(not row['expected_doc_ids'] for row in rows) == 4
    assert DATASET.evidence_band({'expected_doc_ids':['a','a']}) == 'one'
    assert DATASET.evidence_band({'expected_doc_ids':['a','b']}) == 'two-three'
    assert DATASET.evidence_band({'expected_doc_ids':['a','b','c','d']}) == 'four-plus'


def test_artifact_publication_never_overwrites(tmp_path):
    path = tmp_path/'artifact.json'
    DATASET.write_new(path, {'status':'frozen'})
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        DATASET.write_new(path, {'status':'changed'})
    assert path.read_bytes() == original
