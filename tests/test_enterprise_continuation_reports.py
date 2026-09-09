"""Reject false continuation histories before publishing Enterprise scores."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    """Load only the local report and deterministic scheduler implementations."""
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPORT = load('e8_report_test', 'evaluations/publish_enterprise_continuation.py')
SCHEDULER = load('e8_report_sweep', 'evaluations/enterprise-stratified-evolution/sweep.py')
PROFILES = load('e8_report_profiles', 'evaluations/enterprise-stratified-evolution/profiles.py')


def continuation_fixture(monkeypatch):
    """Model a gain, one unavailable hypothesis, and a non-improving child."""
    monkeypatch.setitem(REPORT.HISTORICAL_VARIANTS, 'classical', 1)
    baseline = PROFILES.baseline_profile()
    strategies = [{'id': 'saturation', 'variants': [
        {'bm25.k1': 1.2}, {'bm25.k1': .6}, {'bm25.k1': 2.0}]}]
    state = SCHEDULER.Sweep(strategies, 'baseline', .5, baseline)
    outcomes = [{'candidate': 'baseline', 'score': .5, 'historical': True}]
    unavailable = []
    while proposed := state.next():
        mechanism, variant = proposed
        profile = PROFILES.mutate(state.profile, 'classical', variant)
        if not state.claim(profile):
            continue
        if variant['bm25.k1'] == .6:
            binding = {'candidate': 'candidate-002', 'profile_sha256': REPORT.profile_digest(profile),
                'fitness': None, 'counts_as_evaluable_miss': False, 'reissue_permitted': False}
            unavailable.append(binding)
            state.events.append({'event': 'historical-unavailable-excluded', 'candidate': 'candidate-002',
                'profile_sha256': binding['profile_sha256'], 'score': None,
                'consecutive_failures': 0, 'incumbent': 'candidate-001', 'reissue_permitted': False})
            continue
        historical = len(outcomes) == 1
        candidate = 'candidate-001' if historical else 'continuation-001'
        score = .6 if historical else .55
        improved = state.observe(candidate, profile, score)
        outcomes.append({'candidate': candidate, 'strategy': mechanism['id'], 'variant': variant,
            'score': score, 'qualified': True, 'historical': historical, 'improved': improved,
            'best_candidate': state.best_id, 'best_score': state.best_score,
            'consecutive_failures': state.failures})
    assert len(outcomes) == 3 and len(unavailable) == 1 and state.round == 2
    result = {'family': 'classical', 'historical_variants': 1, 'new_variants': 1, 'generation': 1,
        'unavailable_hypotheses': unavailable, 'complete_hypothesis_coverage': False,
        'baseline_score': .5, 'outcomes': outcomes, 'events': state.events,
        'profile': state.profile, 'winner': {'id': state.best_id}, 'rounds': state.round,
        'status': 'round-without-improvement-with-unavailable-hypothesis',
        'stopping_rule': state.stop_reason}
    return result, (strategies, baseline, PROFILES, SCHEDULER, 5)


def test_complete_continuation_replay_preserves_original_exposure_and_missing_hypothesis(monkeypatch):
    result, args = continuation_fixture(monkeypatch)
    REPORT.replay_continuation(result, *args)


@pytest.mark.parametrize('tamper', ['baseline-exposure', 'historical-exposure', 'new-exposure',
    'retry', 'zero-fitness', 'miss', 'missing-outcome', 'reordered', 'winner', 'gain',
    'counter', 'hidden-exclusion', 'claimed-plateau', 'changed-budget', 'missing-event'])
def test_unsupported_continuation_claims_fail_closed(monkeypatch, tamper):
    result, args = continuation_fixture(monkeypatch)
    result = copy.deepcopy(result)
    if tamper == 'baseline-exposure':
        result['outcomes'][0]['historical'] = False
    elif tamper == 'historical-exposure':
        result['outcomes'][1]['historical'] = False
    elif tamper == 'new-exposure':
        result['outcomes'][2]['historical'] = True
    elif tamper == 'retry':
        result['unavailable_hypotheses'][0]['reissue_permitted'] = True
    elif tamper == 'zero-fitness':
        result['unavailable_hypotheses'][0]['fitness'] = 0
    elif tamper == 'miss':
        result['unavailable_hypotheses'][0]['counts_as_evaluable_miss'] = True
    elif tamper == 'missing-outcome':
        result['outcomes'].pop()
    elif tamper == 'reordered':
        result['outcomes'][2]['variant'] = {'bm25.k1': .6}
    elif tamper == 'winner':
        result['winner']['id'] = 'continuation-001'
    elif tamper == 'gain':
        result['outcomes'][2]['improved'] = True
    elif tamper == 'counter':
        result['outcomes'][2]['consecutive_failures'] = 2
    elif tamper == 'hidden-exclusion':
        result['unavailable_hypotheses'] = []
    elif tamper == 'claimed-plateau':
        result['status'] = 'full-round-without-improvement'
    elif tamper == 'changed-budget':
        result['new_variants'] = 2
    else:
        result['events'].pop()
    with pytest.raises(ValueError):
        REPORT.replay_continuation(result, *args)


def test_changed_historical_manifest_is_rejected_before_reading_private_selection(tmp_path, monkeypatch):
    monkeypatch.setattr(REPORT, 'WORK', tmp_path)
    (tmp_path / 'historical-inputs.json').write_text('{}', encoding='utf-8')
    for name, value in {
        'execution-contract-v2.json': {'workspace_files': {'historical-inputs.json': '0' * 64}},
        'protocol.json': {'historical_inputs_sha256': '0' * 64},
    }.items():
        (tmp_path / name).write_text(REPORT.json.dumps(value), encoding='utf-8')
    with pytest.raises(ValueError, match='Historical evidence commitment changed'):
        REPORT.collect()
