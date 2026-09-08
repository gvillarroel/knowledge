"""Interrupted native evidence must remain unavailable, never become a winning profile."""
import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def reporter(monkeypatch):
    source = Path(__file__).resolve().parents[1] / 'evaluations/skill-evolution'
    monkeypatch.syspath_prepend(str(source))
    spec = importlib.util.spec_from_file_location('tested_interruption_reporting', source / 'aggregate_interruption.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


@pytest.fixture
def evidence(reporter, tmp_path):
    metadata, count = {}, 0
    directory = tmp_path / 'native-job'
    for dataset in sorted(reporter.DATASETS):
        for family in reporter.PRIMARY:
            identity = f'opaque-{len(metadata)}'
            metadata[identity] = {'source_cohort': dataset, 'family': family, 'question': 'PRIVATE SENTINEL'}
            if (dataset, family) == ('data-science', 'ensemble'):
                continue
            count += 1
            metrics = {'ndcg_at_10': .9, 'recall_at_10': .8, 'mrr_at_10': .7, 'full_qrel_coverage_at_10': .6, 'p95_ms': 2}
            put(directory / identity / 'result.json', {'task_name': identity, 'exception_info': None,
                'verifier_result': {'rewards': {'reward': .9, 'evidence_integrity': 1}},
                'started_at': '2026-09-07T01:00:00', 'finished_at': '2026-09-07T01:00:04',
                'agent_execution': {'started_at': '2026-09-07T01:00:01', 'finished_at': '2026-09-07T01:00:03'}})
            put(directory / identity / 'verifier/diagnostics.json', {'status': 'pass', 'question_count': 40,
                'routes': {route: metrics for route in reporter.ROUTES[family]}, 'build_seconds': 1, 'knowledge_bytes': 128,
                'private_note': 'PRIVATE SENTINEL'})
    put(directory / 'result.json', {'n_total_trials': 32, 'finished_at': None,
        'stats': {'n_completed_trials': count, 'n_errored_trials': 0, 'evals': {'native': {'metrics': [{'reward': .9}]}}}})
    put(directory / 'lock.json', {'fixture': True})
    job = {'label': 'knowledge-retrieval-e5-g001-development-expand-titles', 'jobDirectory': str(directory),
           'jobId': 'synthetic-job', 'complete': False, 'completenessProblems': ['one unavailable trial'],
           'skillProvenance': [{'digest': 'fixture-skill'}], 'summary': {'requestedTrials': 32, 'completedTrials': count,
           'erroredTrials': 0, 'reward': {'average': .9}}}
    return job, metadata


def test_missing_result_preserves_denominator_and_suppresses_partial_mean(reporter, evidence):
    candidate, routes, failures = reporter.project_job(*evidence)
    assert (candidate['expected_trials'], candidate['completed_trials'], candidate['scored_trials']) == (32, 31, 31)
    assert candidate['qualified'] is False
    assert candidate['mean_ndcg_at_10'] is None
    assert candidate['native_diagnostic_mean_reward'] == .9
    assert len(routes) == 69
    assert failures == [{'candidate': 'expand-titles', 'dataset': 'data-science', 'family': 'ensemble',
                         'status': 'interrupted-no-native-result', 'error_type': 'unavailable'}]
    assert 'PRIVATE SENTINEL' not in json.dumps((candidate, routes, failures))
    assert 'opaque-' not in json.dumps((candidate, routes, failures))
    assert reporter.best_by_dataset({'candidates': [candidate], 'routes': routes, 'failures': failures})[0]['winners'] == []


@pytest.mark.parametrize('corruption', ['complete', 'count', 'taxonomy', 'duplicate', 'reward', 'unknown-route', 'nan', 'resource'])
def test_rejects_misleading_or_unsafe_projection(reporter, evidence, corruption):
    job, metadata = evidence
    directory = Path(job['jobDirectory'])
    trial = next(directory.glob('*/result.json'))
    if corruption == 'complete':
        job['complete'] = True
    elif corruption == 'count':
        job['summary']['completedTrials'] = 32
    elif corruption == 'taxonomy':
        next(iter(metadata.values()))['source_cohort'] = '../private'
    elif corruption == 'duplicate':
        another = list(directory.glob('*/result.json'))[1]
        put(another, json.loads(trial.read_text()))
    elif corruption == 'reward':
        data = json.loads(trial.read_text())
        data['verifier_result']['rewards']['reward'] = .1
        put(trial, data)
    else:
        path = trial.parent / 'verifier/diagnostics.json'
        data = json.loads(path.read_text())
        if corruption == 'unknown-route':
            data['routes']['../../private'] = next(iter(data['routes'].values()))
        elif corruption == 'nan':
            next(iter(data['routes'].values()))['recall_at_10'] = float('nan')
        else:
            data['build_seconds'] = -1
        put(path, data)
    with pytest.raises(ValueError):
        reporter.project_job(job, metadata)


def test_failed_integrity_keeps_measurement_out_of_routes(reporter, evidence):
    job, metadata = evidence
    path = next(Path(job['jobDirectory']).glob('*/result.json'))
    data = json.loads(path.read_text())
    data['verifier_result']['rewards']['evidence_integrity'] = 0
    put(path, data)
    candidate, routes, failures = reporter.project_job(job, metadata)
    assert candidate['scored_trials'] == 30 and len(failures) == 2
    assert all(row['dataset'] != metadata[data['task_name']]['source_cohort'] or row['family'] != metadata[data['task_name']]['family'] for row in routes)


def test_projection_requires_every_planned_profile(reporter):
    with pytest.raises(ValueError, match='Every planned profile'):
        reporter.combine({'candidates': []}, {'candidates': []})


def test_render_preserves_unavailable_profile_and_refuses_overwrite(reporter, evidence, tmp_path):
    candidate, routes, failures = reporter.project_job(*evidence)
    candidate.update(mean_gain=None, improved_cells=None, unchanged_cells=None, regressed_cells=None)
    data = {'candidates': [candidate], 'routes': routes, 'failures': failures,
            'primary_changes': [], 'completed_native_trials': 31, 'expected_native_trials': 32,
            'unavailable_native_trials': 1, 'best_default_by_dataset': [], 'best_all_routes_by_dataset': []}
    output = tmp_path / 'report'
    reporter.render(output, data)
    assert len(list((output / 'by-skill').glob('*.md'))) == 8
    assert (output / 'failures.csv').exists()
    assert 'unavailable' in (output / 'README.md').read_text()
    assert 'interrupted-no-native-result' in (output / 'by-profile/expand-titles.md').read_text()
    with pytest.raises(FileExistsError):
        reporter.render(output, data)
