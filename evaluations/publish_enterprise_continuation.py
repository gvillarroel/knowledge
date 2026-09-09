"""Publish E8 only after exact continuation replay and complete native gates."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WORK = REPO / 'tmp/e8'
spec = importlib.util.spec_from_file_location('e8_report_core', REPO / 'evaluations/publish_enterprise_stratified.py')
CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CORE)
HISTORICAL_VARIANTS = {'legacy': 16, 'embeddings': 6, 'classical': 22, 'adaptive': 18,
                       'turso': 0, 'graphify': 0, 'entity-graph': 0, 'ensemble': 0}


def profile_digest(profile):
    """Bind a complete proposal independently of whitespace or member order."""
    return hashlib.sha256(json.dumps(profile, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def replay_continuation(result, strategies, baseline_profile, profiles, scheduler, max_rounds):
    """Verify cumulative decisions, explicit exclusions and terminal coverage."""
    family = result['family']
    historical = HISTORICAL_VARIANTS[family]
    if result['historical_variants'] != historical or result['new_variants'] != result['generation']:
        raise ValueError('Historical or native generation accounting changed')
    unavailable = result['unavailable_hypotheses']
    expected_unavailable = int(family in ('classical', 'adaptive'))
    if len(unavailable) != expected_unavailable or result['complete_hypothesis_coverage'] != (not expected_unavailable):
        raise ValueError('Unavailable hypothesis coverage was hidden')
    bindings = {row['profile_sha256']: row for row in unavailable}
    if len(bindings) != expected_unavailable:
        raise ValueError('Duplicate unavailable binding')
    outcomes = result['outcomes']
    if not outcomes or outcomes[0]['candidate'] != 'baseline' or outcomes[0]['score'] != result['baseline_score']:
        raise ValueError('Missing original baseline')
    if outcomes[0].get('historical') is not (historical > 0):
        raise ValueError('Original baseline exposure was relabeled')
    schedule = scheduler.Sweep(strategies, 'baseline', result['baseline_score'], baseline_profile, max_rounds=max_rounds)
    cursor, exclusions = 0, set()
    while proposed := schedule.next():
        mechanism, variant = proposed
        profile = profiles.mutate(schedule.profile, family, variant)
        if not schedule.claim(profile):
            continue
        key = profile_digest(profile)
        if key in bindings:
            binding = bindings[key]
            if cursor != historical or key in exclusions or binding['fitness'] is not None or binding['counts_as_evaluable_miss'] or binding['reissue_permitted']:
                raise ValueError('Unavailable original was scored, reordered or retried')
            schedule.events.append({'event': 'historical-unavailable-excluded', 'candidate': binding['candidate'],
                'profile_sha256': key, 'score': None, 'consecutive_failures': schedule.failures,
                'incumbent': schedule.best_id, 'reissue_permitted': False})
            exclusions.add(key)
            continue
        cursor += 1
        if cursor >= len(outcomes):
            raise ValueError('Missing scheduled outcome')
        observed = outcomes[cursor]
        if observed['strategy'] != mechanism['id'] or observed['variant'] != variant:
            raise ValueError('Reordered continuation outcome')
        if observed.get('historical') is not (cursor <= historical):
            raise ValueError('Historical observation relabeled as new or vice versa')
        improved = schedule.observe(observed['candidate'], profile, observed['score'], qualified=observed['qualified'])
        if (improved != observed['improved'] or schedule.best_id != observed['best_candidate']
                or schedule.best_score != observed['best_score'] or schedule.failures != observed['consecutive_failures']):
            raise ValueError('Continuation retention or stopping differs from native history')
    expected_status = schedule.stop_reason
    if unavailable and expected_status == 'full-round-without-improvement':
        expected_status = 'round-without-improvement-with-unavailable-hypothesis'
    if (cursor != len(outcomes) - 1 or cursor != historical + result['new_variants']
            or exclusions != set(bindings) or schedule.events != result['events']
            or schedule.profile != result['profile'] or schedule.best_id != result['winner']['id']
            or schedule.stop_reason != result['stopping_rule'] or expected_status != result['status']
            or schedule.round != result['rounds']):
        raise ValueError('Terminal continuation evidence differs from cumulative replay')


def collect():
    """Require exact historical input bindings before final aggregate collection."""
    contract = CORE.read(WORK / 'execution-contract-v2.json')
    protocol = CORE.read(WORK / 'protocol.json')
    historical_path = WORK / 'historical-inputs.json'
    digest = CORE.sha(historical_path)
    if digest != contract['workspace_files']['historical-inputs.json'] or digest != protocol['historical_inputs_sha256']:
        raise ValueError('Historical evidence commitment changed')
    historical = CORE.read(historical_path)
    for family in HISTORICAL_VARIANTS:
        result = CORE.read(WORK / 'family-results' / (family + '.json'))
        expected = historical['unavailable'].get(family)
        bindings = result['unavailable_hypotheses']
        if expected and bindings != [{k: v for k, v in expected.items() if k != 'profile'}]:
            raise ValueError('Terminal family does not preserve its exact unavailable original')
        if not expected and bindings:
            raise ValueError('Undeclared hypothesis exclusion')
    value = CORE.collect(work=WORK, execution_contract='execution-contract-v2.json',
        selection_source=REPO / 'tmp/e7/development-selection-v2/selected.private.json',
        replay=replay_continuation, campaign='E8')
    value['historical_development'] = {'source_study': 'enterprise-e7', 'completed_original_jobs': 66,
        'incomplete_original_jobs': 2, 'historical_inputs_sha256': digest,
        'reissued_original_profiles': 0, 'missing_fitness_imputed': False,
        'maximum_cumulative_rounds': 5, 'maximum_cumulative_variants': 585}
    return value


def main():
    """Write a new report directory only after every required native check passes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    value = collect()
    files = CORE.render(value)
    files['aggregate.json'] = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    files['comparison.json'] = json.dumps(CORE.comparison(value), indent=2, sort_keys=True, allow_nan=False) + '\n'
    args.output.mkdir(parents=True, exist_ok=False)
    for relative, text in files.items():
        path = args.output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')
    CORE.plot(value, args.output)
    print(json.dumps({'status': 'complete', 'campaign': 'E8', 'families': 8, 'routes': 36, 'native_final_trials': 16}))


if __name__ == '__main__':
    main()
