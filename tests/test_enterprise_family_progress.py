"""Keep intermediate Enterprise reports tied to complete native observations."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('family_progress_test', ROOT / 'evaluations/publish_enterprise_family_progress.py')
REPORT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(REPORT)
CONTROLLER = REPORT.load_controller()


def report_integrity_fixture(tmp_path, monkeypatch):
    roots = {'source_files': tmp_path / 'repo', 'workspace_files': tmp_path / 'work',
             'historical_files': tmp_path / 'history'}
    for key, attribute in (('source_files', 'REPO'), ('workspace_files', 'WORK'), ('historical_files', 'HISTORY')):
        monkeypatch.setattr(REPORT, attribute, roots[key])
    contract = {}
    paths = []
    for key, root in roots.items():
        path = root / 'input.txt'
        path.parent.mkdir()
        path.write_text('frozen', encoding='utf-8')
        contract[key] = {'input.txt': REPORT.CORE.sha(path)}
        paths.append(path)
    external = tmp_path / 'external.txt'
    external.write_text('frozen external', encoding='utf-8')
    monkeypatch.setattr(REPORT.CORE, 'host', lambda path: external)
    contract['external_read_only_files'] = {'/mnt/c/external.txt': REPORT.CORE.sha(external)}
    return contract, paths + [external]


def test_offline_reporting_verifies_every_frozen_source_group(tmp_path, monkeypatch):
    contract, _ = report_integrity_fixture(tmp_path, monkeypatch)
    assert REPORT.verify_report_files(contract) == 4


@pytest.mark.parametrize('index', range(4))
def test_offline_reporting_rejects_drift_in_every_frozen_source_group(tmp_path, monkeypatch, index):
    contract, paths = report_integrity_fixture(tmp_path, monkeypatch)
    paths[index].write_text('changed', encoding='utf-8')
    with pytest.raises(ValueError, match='integrity mismatch'):
        REPORT.verify_report_files(contract)


@pytest.mark.parametrize('path', ['../escape', '/absolute', 'C:/absolute'])
def test_report_contract_cannot_escape_its_declared_source_base(tmp_path, monkeypatch, path):
    contract, _ = report_integrity_fixture(tmp_path, monkeypatch)
    contract['source_files'] = {path: '0' * 64}
    with pytest.raises(ValueError, match='source path'):
        REPORT.verify_report_files(contract)


@pytest.mark.parametrize('tamper', ['unsealed', 'validation', 'holdout', 'stopped', 'completed', 'planned'])
def test_intermediate_report_never_opens_or_follows_a_private_gate(tamper):
    state = {'designSeal': {'digest': 'fixture'}, 'validationRelease': None, 'holdoutRelease': None,
             'stages': {'evolve': {'status': 'running'}}}
    REPORT.verify_report_state(state)
    if tamper == 'unsealed':
        state['designSeal'] = None
    elif tamper in ('validation', 'holdout'):
        state[tamper + 'Release'] = {'digest': 'fixture'}
    else:
        state['stages']['evolve']['status'] = tamper
    with pytest.raises(ValueError, match='unopened'):
        REPORT.verify_report_state(state)


def metrics(value):
    """Return fixture-only verifier metrics, not empirical Harbor results."""
    return {key: value for key in REPORT.CORE.METRICS}


def write(path, value):
    """Write a synthetic artifact for isolated contract validation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(REPORT.json.dumps(value), encoding='utf-8')


def questions():
    """Keep the fixed eligible denominator and weight without real benchmark data."""
    return [{'question_id': f'fixture-{i:03d}', 'expected_doc_ids': ['fixture'] if i < 112 else [],
        'population_to_sample_weight': 4 if i < 110 else 15 if i < 112 else 0,
        'question_type': 'fixture', 'source_types': ['fixture']} for i in range(120)]


def test_weighted_metrics_and_unweighted_pairs_keep_distinct_denominators():
    metadata = questions()
    left = [metrics(.5)] * 112 + [None] * 8
    right = [metrics(.5)] * 110 + [metrics(1)] * 2 + [None] * 8
    result = REPORT.weighted_group(metadata, right, list(range(120)))
    assert result['population_weight'] == 470 and result['retrieval_eligible'] == 112
    assert result['ndcg_at_10'] == pytest.approx(250 / 470)
    assert REPORT.paired_cases(metadata, left, right, list(range(120))) == {
        'improved': 2, 'regressed': 0, 'tied': 110, 'without_references': 8}
    empty = REPORT.weighted_group(metadata, right, list(range(112, 120)))
    assert empty['ndcg_at_10'] is None and empty['population_weight'] == 0


@pytest.mark.parametrize('tamper', ['missing-case', 'lost-reference', 'invented-reference', 'zero-weight',
    'negative-weight', 'boolean', 'nan', 'infinite', 'out-of-range'])
def test_invalid_case_evidence_cannot_enter_a_progress_average(tamper):
    metadata, cases = questions(), [metrics(.5) for _ in range(112)] + [None] * 8
    if tamper == 'missing-case':
        cases.pop()
    elif tamper == 'lost-reference':
        cases[0] = None
    elif tamper == 'invented-reference':
        cases[-1] = metrics(.5)
    elif tamper.endswith('weight'):
        metadata[0]['population_to_sample_weight'] = 0 if tamper == 'zero-weight' else -1
    else:
        cases[0]['ndcg_at_10'] = {'boolean': True, 'nan': float('nan'), 'infinite': float('inf'), 'out-of-range': 1.1}[tamper]
    with pytest.raises(ValueError):
        REPORT.weighted_group(metadata, cases, list(range(120)))


def normalized_fixture(tmp_path):
    directories = [tmp_path / name for name in ('baseline', 'previous', 'candidate')]
    value = {'source': 'harbor', 'harborVersion': '0.18.0', 'rewardKey': 'reward', 'passThreshold': .8,
        'jobs': [{'jobDirectory': str(path), 'complete': True, 'completenessProblems': [], 'label': path.name} for path in directories],
        'comparison': {'enabled': True, 'fairnessBasis': 'lock-and-trial-results', 'warning': None, 'baseline': 'baseline'}}
    return value, directories


def test_locked_native_comparison_requires_the_exact_ordered_original_jobs(tmp_path):
    value, directories = normalized_fixture(tmp_path)
    REPORT.verify_normalized(value, directories)
    value['jobs'].reverse()
    with pytest.raises(ValueError, match='reordered'):
        REPORT.verify_normalized(value, directories)


@pytest.mark.parametrize('tamper', ['missing', 'duplicate', 'incomplete', 'unlocked', 'warning', 'not-compared', 'threshold'])
def test_partial_or_unfair_normalization_does_not_authorize_publication(tmp_path, tamper):
    value, directories = normalized_fixture(tmp_path)
    if tamper == 'missing':
        value['jobs'].pop()
    elif tamper == 'duplicate':
        value['jobs'][1] = copy.deepcopy(value['jobs'][0])
    elif tamper == 'incomplete':
        value['jobs'][1]['complete'] = False
    elif tamper == 'unlocked':
        value['comparison']['fairnessBasis'] = 'trial-results'
    elif tamper == 'warning':
        value['comparison']['warning'] = 'unmatched-lock'
    elif tamper == 'not-compared':
        value['comparison']['enabled'] = False
    else:
        value['passThreshold'] = 1.0
    with pytest.raises(ValueError, match='Native comparison'):
        REPORT.verify_normalized(value, directories)


def measurement_fixture(tmp_path):
    directory = tmp_path / 'original'
    dates = {'started_at': '2026-01-01T00:00:00', 'finished_at': '2026-01-01T00:00:01'}
    write(directory / 'result.json', {**dates, 'n_total_trials': 1, 'stats': {'n_completed_trials': 1,
        **{k: 0 for k in ('n_running_trials', 'n_pending_trials', 'n_errored_trials', 'n_cancelled_trials', 'n_retries')}}})
    write(directory / 'lock.json', {'fixture_only': True})
    write(directory / 'trial/result.json', {**dates, 'exception_info': None, 'agent_execution': dates,
        'verifier_result': {'rewards': {'reward': .6, 'evidence_integrity': 1}}})
    write(directory / 'trial/verifier/diagnostics.json', {'status': 'pass', 'question_count': 120,
        'routes': {'lexical-sql': {**metrics(.6), 'p95_ms': 5}},
        'cases': {'lexical-sql': [metrics(.6)] * 112 + [None] * 8}, 'build_seconds': .5, 'knowledge_bytes': 1024})
    native = {'candidateId': 'fixture', 'jobDirectory': str(directory), 'evaluable': True,
        'promotionEligibleProvenance': True, 'qualification': {'passed': True}, 'skillDigest': 'fixture-only',
        'summary': {'errorCount': 0, 'meanReward': .6, 'observedMeanReward': .6}}
    return directory, native


def test_measurement_uses_existing_cases_and_preserves_runtime_and_hashes(tmp_path):
    directory, native = measurement_fixture(tmp_path)
    actual, row, cases = REPORT.inspect_measurement('turso', native, questions())
    assert actual == directory and row['score'] == .6 and len(cases) == 120
    assert row['native_job_seconds'] == 1 and row['evidence_integrity'] == 1
    assert row['diagnostics_sha256'] == REPORT.CORE.sha(directory / 'trial/verifier/diagnostics.json')


@pytest.mark.parametrize('tamper', ['retry', 'unfinished', 'trial-error', 'integrity', 'denominator',
    'aggregate', 'primary', 'substituted-route', 'unqualified'])
def test_missing_or_changed_native_measurements_fail_before_report_creation(tmp_path, tamper):
    directory, native = measurement_fixture(tmp_path)
    if tamper == 'unqualified':
        native['qualification']['passed'] = False
    elif tamper in ('retry', 'unfinished'):
        path = directory / 'result.json'
        value = REPORT.CORE.read(path)
        if tamper == 'retry':
            value['stats']['n_retries'] = 1
        else:
            value['finished_at'] = None
        write(path, value)
    elif tamper in ('trial-error', 'integrity', 'primary'):
        path = directory / 'trial/result.json'
        value = REPORT.CORE.read(path)
        if tamper == 'trial-error':
            value['exception_info'] = {'fixture_only': True}
        else:
            value['verifier_result']['rewards']['reward' if tamper == 'primary' else 'evidence_integrity'] = .7
        write(path, value)
    else:
        path = directory / 'trial/verifier/diagnostics.json'
        value = REPORT.CORE.read(path)
        if tamper == 'denominator':
            value['question_count'] = 119
        elif tamper == 'aggregate':
            value['routes']['lexical-sql']['ndcg_at_10'] = .7
        else:
            for key in ('routes', 'cases'):
                value[key]['invented'] = value[key].pop('lexical-sql')
        write(path, value)
    with pytest.raises(ValueError):
        REPORT.inspect_measurement('turso', native, questions())


def prefix_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(REPORT, 'WORK', tmp_path)
    variants = [{'engine': 'bm25', 'k1': 1.2}, {'engine': 'bm25', 'k1': .6}]
    protocol = {'strategies': {'turso': [{'id': 'saturation', 'variants': variants}]},
                'budget': {'maximum_outer_rounds': 5}}
    baseline = {'candidateId': 'baseline', 'evaluable': True, 'qualification': {'passed': True},
                'summary': {'meanReward': .5}}
    write(tmp_path / 'search/turso/development/generation-000/pareto-archive.json', {'candidateResults': [baseline]})
    state = CONTROLLER.SCHEDULER.Sweep(protocol['strategies']['turso'], 'baseline', .5, CONTROLLER.PROFILES.baseline_profile())
    for index, score in ((1, .6), (2, .55)):
        strategy, variant, profile = CONTROLLER.next_unique(state, 'turso')
        candidate = f'continuation-{index:03d}'
        improved = state.observe(candidate, profile, score)
        path = tmp_path / 'search/turso/development' / f'generation-{index:03d}/pareto-archive.json'
        native = {'candidateId': candidate, 'evaluable': True, 'promotionEligibleProvenance': True,
            'qualification': {'passed': True}, 'summary': {'meanReward': score}}
        write(path, {'candidateResults': [native], 'promotionEligibleProfile': True, 'bestAggregateCandidate': state.best_id})
        write(tmp_path / 'progress/turso' / f'{index:03d}.json', {'outcome': {'candidate': candidate, 'historical': False,
            'strategy': strategy['id'], 'variant': variant, 'score': score, 'qualified': True, 'improved': improved,
            'best_candidate': state.best_id, 'best_score': state.best_score, 'consecutive_failures': state.failures,
            'archive': str(path)}, 'events': state.events})
    return protocol, {'families': {}, 'unavailable': {}}


def test_candidate_above_baseline_does_not_become_an_incremental_gain(tmp_path, monkeypatch):
    protocol, history = prefix_fixture(tmp_path, monkeypatch)
    outcome, previous, _, _, bindings = REPORT.replay_prefix(CONTROLLER, 'turso', 2, protocol, history)
    assert outcome['score'] == .55 and previous == {'candidate': 'continuation-001', 'score': .6}
    assert not outcome['improved'] and outcome['consecutive_failures'] == 1 and len(bindings) == 2


@pytest.mark.parametrize('tamper', ['counter', 'retention', 'variant', 'archive', 'native-fitness', 'event', 'historical'])
def test_cumulative_prefix_replay_rejects_edited_decisions(tmp_path, monkeypatch, tamper):
    protocol, history = prefix_fixture(tmp_path, monkeypatch)
    path = tmp_path / 'progress/turso/002.json'
    value = REPORT.CORE.read(path)
    if tamper == 'counter':
        value['outcome']['consecutive_failures'] = 0
    elif tamper == 'retention':
        value['outcome']['improved'] = True
    elif tamper == 'variant':
        value['outcome']['variant']['k1'] = 3
    elif tamper == 'archive':
        value['outcome']['archive'] = str(tmp_path / 'unrelated.json')
    elif tamper == 'native-fitness':
        value['outcome']['score'] = .61
    elif tamper == 'historical':
        value['outcome']['historical'] = True
    else:
        value['events'].pop()
    write(path, value)
    with pytest.raises(ValueError):
        REPORT.replay_prefix(CONTROLLER, 'turso', 2, protocol, history)


def test_rendering_labels_a_miss_against_the_actual_previous_incumbent(tmp_path):
    _, native = measurement_fixture(tmp_path)
    _, template, cases = REPORT.inspect_measurement('turso', native, questions())
    rows = []
    for candidate, score in (('baseline', .5), ('continuation-001', .6), ('continuation-002', .55)):
        row = copy.deepcopy(template)
        row.update(candidate=candidate, score=score, historical_job=False)
        row['routes']['lexical-sql'].update(metrics(score))
        rows.append(row)
    value = {'family': 'turso', 'snapshot_utc': 'fixture-only', 'rows': rows, 'groups': [],
        'candidate': 'continuation-002', 'previous_incumbent': {'candidate': 'continuation-001', 'score': .6},
        'retained_candidate': 'continuation-001', 'consecutive_misses': 1, 'primary_route': 'lexical-sql',
        'mechanism': 'saturation', 'treatment': 'consultation', 'variant': {'k1': .6}}
    files = REPORT.render(value)
    assert '+5.00 percentage points versus baseline and -5.00 versus the previous incumbent' in files['README.md']
    assert 'Recorded retention: `continuation-001`' in files['README.md']
    assert 'first gain therefore includes an algorithm and token-matching change' in files['README.md']
    assert 'does not prove automatic inheritance by generated experts' in files['README.md']
    assert 'Historical job' in files['README.md'] and 'not the total campaign workload' in files['cta.md']
    assert set(files) == {'README.md', 'groups.md', 'routes.md', 'cta.md'}


def test_unverified_prefix_does_not_create_a_report_directory(tmp_path, monkeypatch):
    output = tmp_path / 'unpublished'

    def reject(*args):
        raise ValueError('fixture missing native comparison')

    monkeypatch.setattr(REPORT, 'collect', reject)
    monkeypatch.setattr(REPORT.sys, 'argv', ['publish_enterprise_family_progress.py', '--family', 'turso',
        '--generation', '1', '--normalized-report', str(tmp_path / 'absent.json'), '--output', str(output)])
    with pytest.raises(ValueError, match='missing native comparison'):
        REPORT.main()
    assert not output.exists()
