"""Protect native historical lineage and interruption boundaries in E8."""
from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parents[1] / 'evaluations/enterprise-continuation'


def load(name):
    before = sys.modules.copy()
    keys = ('prepare', 'native', 'run', 'study_guard')
    sys.path.insert(0, str(HERE))
    try:
        for key in keys:
            sys.modules.pop(key, None)
        spec = importlib.util.spec_from_file_location('e8_test_' + name, HERE / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(HERE))
        for key in keys:
            sys.modules.pop(key, None)
            if key in before:
                sys.modules[key] = before[key]


RUN, PREPARE, INITIALIZE, FINAL = (load(name) for name in ('run', 'prepare', 'initialize', 'finalize'))
GUARD = load('study_guard')


def history_fixture():
    profile = RUN.PROFILES.baseline_profile()
    strategies = [{'id': 'saturation', 'variants': [{'engine': 'bm25', 'k1': 1.2},
        {'engine': 'bm25', 'k1': 0.6}, {'engine': 'bm25', 'k1': 2.0}]}]
    changed = RUN.PROFILES.mutate(profile, 'legacy', strategies[0]['variants'][0])
    protocol = {'strategies': {'legacy': strategies}, 'budget': {'maximum_outer_rounds': 5}}
    records = [
        {'candidateId': 'baseline', 'evaluable': True, 'qualification': {'passed': True},
         'summary': {'meanReward': .5}, 'jobDirectory': '/original/baseline'},
        {'candidateId': 'candidate-001', 'evaluable': True, 'qualification': {'passed': True},
         'summary': {'meanReward': .6}, 'jobDirectory': '/original/one'}]
    history = [
        {'candidate': {'id': 'baseline'}, 'profile': profile, 'generation': 0},
        {'candidate': {'id': 'candidate-001'}, 'profile': changed, 'generation': 1,
         'outcome': {'candidate': 'candidate-001', 'strategy': 'saturation',
            'variant': strategies[0]['variants'][0], 'score': .6, 'qualified': True,
            'improved': True, 'consecutive_failures': 0, 'best_candidate': 'candidate-001', 'best_score': .6}}]
    return history, records, protocol


def test_history_keeps_original_incumbent_counter_and_seen_profiles():
    history, records, protocol = history_fixture()
    schedule, outcomes = RUN.replay_history('legacy', history, records, protocol)
    assert schedule.best_id == 'candidate-001' and schedule.best_score == .6
    assert schedule.failures == 0 and schedule.round == 1
    assert all(row['historical'] for row in outcomes)
    assert len(schedule.seen) == 2
    assert RUN.next_unique(schedule, 'legacy')[1]['k1'] == .6


@pytest.mark.parametrize('tamper', ['missing', 'duplicate', 'score', 'qualification', 'profile', 'variant', 'counter', 'incumbent', 'baseline'])
def test_historical_import_cannot_rewrite_native_fitness_or_stopping(tamper):
    history, records, protocol = history_fixture()
    if tamper == 'missing':
        records.pop()
    elif tamper == 'duplicate':
        records.append(copy.deepcopy(records[-1]))
    elif tamper == 'score':
        records[1]['summary']['meanReward'] = .61
    elif tamper == 'qualification':
        records[1]['qualification']['passed'] = False
    elif tamper == 'profile':
        history[1]['profile']['legacy']['search']['k1'] = 3
    elif tamper == 'variant':
        history[1]['outcome']['variant'] = {'engine': 'bm25', 'k1': 3}
    elif tamper == 'counter':
        history[1]['outcome']['consecutive_failures'] = 2
    elif tamper == 'incumbent':
        history[1]['outcome']['best_candidate'] = 'baseline'
    else:
        records[0]['qualification']['passed'] = False
    with pytest.raises(ValueError):
        RUN.replay_history('legacy', history, records, protocol)


def test_interrupted_profile_is_reserved_without_score_miss_or_reset():
    history, records, protocol = history_fixture()
    schedule, _ = RUN.replay_history('legacy', history, records, protocol)
    schedule.failures = 2
    interrupted = RUN.PROFILES.mutate(schedule.profile, 'legacy', {'engine': 'bm25', 'k1': .6})
    binding = {'candidate': 'unavailable', 'profile': interrupted,
        'profile_sha256': RUN.SCHEDULER.digest(interrupted)}
    RUN.exclude_interrupted(schedule, 'legacy', binding)
    assert schedule.failures == 2 and schedule.best_score == .6
    assert schedule.best_id == 'candidate-001'
    assert not schedule.claim(interrupted)
    assert RUN.next_unique(schedule, 'legacy')[1]['k1'] == 2
    event = next(e for e in schedule.events if e['event'] == 'historical-unavailable-excluded')
    assert event['score'] is None and not event['reissue_permitted']


@pytest.mark.parametrize('tamper', ['digest', 'profile'])
def test_interrupted_exclusion_requires_exact_next_hypothesis(tamper):
    history, records, protocol = history_fixture()
    schedule, _ = RUN.replay_history('legacy', history, records, protocol)
    profile = RUN.PROFILES.mutate(schedule.profile, 'legacy', {'engine': 'bm25', 'k1': .6})
    binding = {'candidate': 'unavailable', 'profile': profile, 'profile_sha256': RUN.SCHEDULER.digest(profile)}
    if tamper == 'digest':
        binding['profile_sha256'] = '0' * 64
    else:
        binding['profile']['legacy']['search']['k1'] = 99
    with pytest.raises(ValueError):
        RUN.exclude_interrupted(schedule, 'legacy', binding)


def test_one_unavailable_lane_does_not_cancel_other_baselines(monkeypatch, tmp_path):
    monkeypatch.setattr(RUN, 'WORK', tmp_path)
    seen, errors = [], []
    def action(family):
        seen.append(family)
        if family == 'broken':
            raise RuntimeError('Infrastructure is unavailable')
        return 'measured-' + family
    result = RUN.parallel_lanes(action, ['broken', 'second', 'third', 'fourth'], errors, 'baseline')
    assert set(seen) == {'broken', 'second', 'third', 'fourth'}
    assert set(result) == {'second', 'third', 'fourth'}
    assert len(errors) == 1 and errors[0]['family'] == 'broken'
    assert (tmp_path / 'errors/baseline-broken.json').is_file()


def test_historical_job_tree_drift_rejects_before_owner_analysis(monkeypatch):
    monkeypatch.setattr(RUN, 'verify_frozen', lambda: None)
    monkeypatch.setattr(RUN, 'load', lambda *args: object())
    monkeypatch.setattr(RUN, 'tree', lambda *args: {'result.json': 'changed'})
    with pytest.raises(ValueError, match='Historical native evidence drift'):
        RUN.import_family('legacy', [{'candidate': {'jobDirectory': '/original', 'skill': '/skill'},
                                      'job_files': {'result.json': 'original'}, 'skill_files': {}}])


def test_append_only_artifacts_do_not_erase_existing_failure(tmp_path):
    path = tmp_path / 'observed.json'
    PREPARE.write(path, {'unavailable': True})
    with pytest.raises(FileExistsError):
        PREPARE.write(path, {'unavailable': False})
    assert PREPARE.read(path) == {'unavailable': True}


def test_final_timeout_versions_only_the_paired_recalculation_jobs(monkeypatch, tmp_path):
    old, new = tmp_path / 'e7', tmp_path / 'e8'
    new.mkdir()
    monkeypatch.setattr(INITIALIZE, 'HISTORY', old)
    monkeypatch.setattr(INITIALIZE, 'WORK', new)
    original = {'job_name': 'e7-original', 'jobs_dir': '/history', 'n_attempts': 1,
        'retry': {'max_retries': 0}, 'tasks': [{'path': '/exact/original/task'}],
        'agents': [{'name': 'enterprise-stratified-retrieval', 'model_name': 'original-model',
                    'import_path': 'enterprise_agent:SkillRetrievalAgent', 'skills': ['/old/skill']}]}
    for phase in ('development', 'validation', 'recalculation'):
        PREPARE.write(old / 'jobs' / ('joint-' + phase + '.json'), original)
    (old / 'enterprise_agent.py').write_text('return "enterprise-stratified-retrieval"\nreturn "3.0.0"\nexec(timeout_sec=3600)\n')
    (new / 'enterprise_agent.py').write_bytes((old / 'enterprise_agent.py').read_bytes())
    INITIALIZE.prepare_jobs()
    for phase in ('development', 'validation', 'recalculation'):
        job = PREPARE.read(new / 'jobs' / ('joint-' + phase + '.json'))
        assert job['tasks'] == original['tasks']
        assert job['retry'] == {'max_retries': 0} and job['n_attempts'] == 1
        assert job['agents'][0]['model_name'] == 'original-model'
        if phase == 'recalculation':
            assert job['agents'][0]['override_timeout_sec'] == 10800
            assert job['agents'][0]['import_path'] == 'enterprise_final_agent:SkillRetrievalAgent'
        else:
            assert 'override_timeout_sec' not in job['agents'][0]
            assert job['agents'][0]['import_path'] == original['agents'][0]['import_path']
    assert 'timeout_sec=10800' in (new / 'enterprise_final_agent.py').read_text()
    assert 'timeout_sec=3600' in (old / 'enterprise_agent.py').read_text()


def test_terminal_output_discloses_unavailable_hypothesis_coverage(monkeypatch, tmp_path):
    monkeypatch.setattr(RUN, 'WORK', tmp_path)
    PREPARE.write(tmp_path / 'protocol.json', {'treatments': {'legacy': 'consultation'}})
    history, records, protocol = history_fixture()
    schedule, outcomes = RUN.replay_history('legacy', history, records, protocol)
    schedule.stop_reason = 'full-round-without-improvement'
    result = RUN.finish_family('legacy', schedule, [{'id': 'candidate-001'}],
        {'bestAggregateCandidate': 'candidate-001'}, 0, outcomes, 1, [{'profile_sha256': 'reserved'}])
    assert result['status'] == 'round-without-improvement-with-unavailable-hypothesis'
    assert result['new_variants'] == 0 and result['historical_variants'] == 1
    assert not result['complete_hypothesis_coverage']


@pytest.mark.parametrize('phase', ['development', 'recalculation', 'validation'])
def test_reservation_receives_actual_execution_phase(monkeypatch, phase):
    calls = []
    manifest = {'source_files': {}, 'workspace_files': {}, 'historical_files': {}, 'external_read_only_files': {}}
    state = {'designSeal': True, 'validationRelease': phase == 'validation', 'holdoutRelease': False,
        'stages': {'evolve': {'status': 'running' if phase == 'development' else 'completed'},
                   'recalculate': {'status': 'running'}, 'validate': {'status': 'running'}}}
    reservation = SimpleNamespace(verify=lambda requested: calls.append(requested))
    organizer = SimpleNamespace(build_state=lambda *args, **kwargs: state)
    def spec(name, path):
        return SimpleNamespace(name=name, loader=SimpleNamespace(exec_module=lambda module: None))
    monkeypatch.setattr(GUARD, 'read', lambda path: manifest)
    monkeypatch.setattr(GUARD.importlib.util, 'spec_from_file_location', spec)
    monkeypatch.setattr(GUARD.importlib.util, 'module_from_spec',
        lambda source: reservation if 'reserved_portfolio' in source.name else organizer)
    result = GUARD.verify(phase)
    assert calls == [phase]
    assert result['phase'] == phase and result['source_verification']
