"""Continue remaining development lanes through the native Pareto owner."""
from __future__ import annotations

import concurrent.futures
import copy
import json
import os
from pathlib import Path

from prepare import (WORK, NAME, OWNER, PROFILES, SCHEDULER, FAMILIES,
                     NEW_FAMILIES, PRIOR_COUNTS, EXECUTION_CONTRACT, read, write, sha, host, tree)
from native import load, verify_frozen, raw_config, archive_path, evaluate_new, realize


def next_unique(schedule, family):
    """Advance only over exact duplicates; do not invent observed fitness."""
    while item := schedule.next():
        strategy, variant = item
        profile = PROFILES.mutate(schedule.profile, family, variant)
        if schedule.claim(profile):
            return strategy, variant, profile
    return None


def replay_history(family, history, records, protocol):
    """Reconstruct an original measured prefix using revalidated native results."""
    indexed = {row['candidateId']: row for row in records}
    if len(indexed) != len(records) or set(indexed) != {r['candidate']['id'] for r in history}:
        raise ValueError('Native historical candidate coverage changed')
    baseline = indexed['baseline']
    if not baseline['evaluable'] or not baseline['qualification']['passed']:
        raise ValueError('Historical baseline is not qualified')
    schedule = SCHEDULER.Sweep(protocol['strategies'][family], 'baseline',
        baseline['summary']['meanReward'], history[0]['profile'],
        max_rounds=protocol['budget']['maximum_outer_rounds'])
    outcomes = [{'candidate': 'baseline', 'strategy': 'baseline', 'score': schedule.best_score,
        'job': baseline['jobDirectory'], 'archive': str(archive_path(family, 0)),
        'historical': True, 'original_generation': 0}]
    for original in history[1:]:
        proposed = next_unique(schedule, family)
        if proposed is None:
            raise ValueError('Historical prefix extends past the original stopping rule')
        strategy, variant, profile = proposed
        previous = original['outcome']
        if profile != original['profile'] or variant != previous['variant'] or strategy['id'] != previous['strategy']:
            raise ValueError('Historical mutation differs from its frozen scheduler')
        record = indexed[original['candidate']['id']]
        score = record['summary']['meanReward']
        if score != previous['score'] or record['qualification']['passed'] != previous['qualified']:
            raise ValueError('Native owner did not reproduce historical fitness/qualification')
        improved = schedule.observe(record['candidateId'], profile, score,
            evaluable=record['evaluable'], qualified=record['qualification']['passed'])
        if (improved != previous['improved'] or schedule.failures != previous['consecutive_failures']
                or schedule.best_id != previous['best_candidate'] or schedule.best_score != previous['best_score']):
            raise ValueError('Historical stopping/retention state changed')
        outcomes.append({**previous, 'historical': True, 'original_generation': original['generation']})
    return schedule, outcomes


def exclude_interrupted(schedule, family, unavailable):
    """Consume a reserved proposal without evaluation, a miss, or a reset."""
    proposed = next_unique(schedule, family)
    if proposed is None or proposed[2] != unavailable['profile']:
        raise ValueError('Interrupted original is not the next exact hypothesis')
    if SCHEDULER.digest(proposed[2]) != unavailable['profile_sha256']:
        raise ValueError('Unavailable profile binding changed')
    schedule.events.append({'event': 'historical-unavailable-excluded',
        'candidate': unavailable['candidate'], 'profile_sha256': unavailable['profile_sha256'],
        'score': None, 'consecutive_failures': schedule.failures,
        'incumbent': schedule.best_id, 'reissue_permitted': False})


def import_family(family, history):
    """Have the native owner revalidate completed jobs in a new generation zero."""
    verify_frozen()
    owner = load('e8_import_' + family.replace('-', '_'), OWNER)
    candidates = []
    for row in history:
        candidate = row['candidate']
        if tree(host(candidate['jobDirectory'])) != row['job_files'] or tree(host(candidate['skill'])) != row['skill_files']:
            raise ValueError('Historical native evidence drift')
        candidates.append(copy.deepcopy(candidate))
    raw = raw_config(family, 0, candidates)
    path = WORK / 'dispatch' / family / 'generation-000/analyze.json'
    write(path, raw)
    result = owner.development(owner.normalize_config(path), analyze_only=True)
    archive = read(archive_path(family, 0))
    if not archive['promotionEligibleProfile'] or not all(r['promotionEligibleProvenance'] for r in archive['candidateResults']):
        raise ValueError('Native historical import is exploratory or mismatched')
    write(path.parent / 'receipt.json', {'owner_result': result, 'historical_only': True,
        'native_trials_dispatched': 0, 'imported_jobs': len(candidates),
        'archive_sha256': sha(archive_path(family, 0))})
    return candidates, archive


def new_baseline(family):
    """Measure a previously unstarted family once, before its candidate search."""
    owner = load('e8_baseline_' + family.replace('-', '_'), OWNER)
    candidates = [{'id': 'baseline', 'skill': str(WORK / 'baseline' / NAME), 'parents': [],
        'rationale': 'Unchanged E7 native control; this family has no previous native development baseline.'}]
    candidates, record, archive = evaluate_new(owner, family, 0, candidates, 'baseline')
    if not record['evaluable'] or not record['qualification']['passed']:
        raise RuntimeError('Baseline is not evaluable and qualified: ' + family)
    print(json.dumps({'event': 'baseline', 'family': family, 'score': record['summary']['meanReward']}), flush=True)
    return candidates, archive


def finish_family(family, schedule, candidates, archive, generation, outcomes, historical_count, unavailable):
    """Record a terminal lane while preserving unavailable hypothesis coverage."""
    winner = next(c for c in candidates if c['id'] == schedule.best_id)
    if archive['bestAggregateCandidate'] != schedule.best_id:
        raise ValueError('Scheduler retention differs from native selection')
    status = schedule.stop_reason
    if unavailable and status == 'full-round-without-improvement':
        status = 'round-without-improvement-with-unavailable-hypothesis'
    result = {'family': family, 'treatment': read(WORK / 'protocol.json')['treatments'][family],
        'status': status, 'stopping_rule': schedule.stop_reason, 'rounds': schedule.round,
        'generation': generation, 'historical_variants': historical_count,
        'new_variants': generation, 'unavailable_hypotheses': unavailable,
        'complete_hypothesis_coverage': not unavailable,
        'baseline_score': outcomes[0]['score'], 'winner': winner, 'score': schedule.best_score,
        'profile': schedule.profile, 'outcomes': outcomes, 'events': schedule.events,
        'final_archive': str(archive_path(family, generation)),
        'final_config': str(WORK / 'dispatch' / family / f'generation-{generation:03d}/analyze.json')}
    write(WORK / 'family-results' / (family + '.json'), result)
    print(json.dumps({'event': 'family-complete', 'family': family, 'new_variants': generation,
        'historical_variants': historical_count, 'status': status, 'score': schedule.best_score}), flush=True)
    return result


def search_family(family, prepared, historical, protocol):
    """Run remaining exact catalog opportunities after historical reconstruction."""
    owner = load('e8_search_' + family.replace('-', '_'), OWNER)
    candidates, archive = prepared
    prior = historical['families'].get(family)
    if prior:
        schedule, outcomes = replay_history(family, prior, archive['candidateResults'], protocol)
    else:
        baseline = next(r for r in archive['candidateResults'] if r['candidateId'] == 'baseline')
        schedule = SCHEDULER.Sweep(protocol['strategies'][family], 'baseline',
            baseline['summary']['meanReward'], read(WORK / 'baseline' / NAME / 'assets/retrieval-profile.json'),
            max_rounds=protocol['budget']['maximum_outer_rounds'])
        outcomes = [{'candidate': 'baseline', 'strategy': 'baseline', 'score': schedule.best_score,
            'job': baseline['jobDirectory'], 'archive': str(archive_path(family, 0)), 'historical': False}]
    unavailable = []
    if family in historical['unavailable']:
        binding = historical['unavailable'][family]
        exclude_interrupted(schedule, family, binding)
        unavailable.append({k: v for k, v in binding.items() if k != 'profile'})
    generation = 0
    while proposed := next_unique(schedule, family):
        strategy, variant, profile = proposed
        if any(SCHEDULER.digest(profile) == row['profile_sha256'] for row in unavailable):
            raise ValueError('Unavailable hypothesis cannot be dispatched')
        generation += 1
        spent = PRIOR_COUNTS.get(family, 0) + len(unavailable) + generation
        cap = protocol['budget']['maximum_outer_rounds'] * sum(len(s['variants']) for s in protocol['strategies'][family])
        if spent > cap:
            raise ValueError('Inherited family candidate budget exhausted')
        identifier = f'continuation-{generation:03d}'
        parent = next(c for c in candidates if c['id'] == schedule.best_id)
        child = realize(family, identifier, Path(parent['skill']), profile, strategy, archive_path(family, generation - 1))
        keep = [c for c in candidates if c['id'] in {'baseline', schedule.best_id}]
        ancestry = {p for c in keep for p in c['parents']}
        while any(c['id'] in ancestry and c not in keep for c in candidates):
            keep += [c for c in candidates if c['id'] in ancestry and c not in keep]
            ancestry = {p for c in keep for p in c['parents']}
        keep.append({'id': identifier, 'skill': str(child), 'parents': [schedule.best_id],
            'rationale': strategy['rationale'] + ' Exact profile and historical development bindings are sealed.'})
        candidates, record, archive = evaluate_new(owner, family, generation, keep, identifier)
        score = record['summary']['meanReward']
        improved = schedule.observe(identifier, profile, score,
            evaluable=record['evaluable'], qualified=record['qualification']['passed'])
        outcome = {'candidate': identifier, 'strategy': strategy['id'], 'variant': variant,
            'score': score, 'qualified': record['qualification']['passed'], 'improved': improved,
            'consecutive_failures': schedule.failures, 'best_candidate': schedule.best_id,
            'best_score': schedule.best_score, 'job': record['jobDirectory'],
            'archive': str(archive_path(family, generation)), 'historical': False}
        outcomes.append(outcome)
        write(WORK / 'progress' / family / f'{generation:03d}.json', {'outcome': outcome, 'events': schedule.events})
        print(json.dumps({'event': 'attempt', 'family': family, **outcome}), flush=True)
    return finish_family(family, schedule, candidates, archive, generation, outcomes, PRIOR_COUNTS.get(family, 0), unavailable)


def parallel_lanes(action, families, errors, phase):
    """Complete independent lanes without dropping others after one failure."""
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(action, family): family for family in families}
        for future in concurrent.futures.as_completed(futures):
            family = futures[future]
            try:
                results[family] = future.result()
            except Exception as exc:
                import traceback
                error = {'family': family, 'phase': phase, 'type': type(exc).__name__,
                    'message': str(exc), 'traceback': traceback.format_exc()}
                errors.append(error)
                write(WORK / 'errors' / (phase + '-' + family + '.json'), error)
                print(json.dumps({'event': 'lane-error', 'phase': phase, 'family': family,
                    'type': type(exc).__name__, 'other_independent_lanes_continue': True}), flush=True)
    return results


def run():
    """Execute the prospectively sealed continuation without reruns."""
    if os.name == 'nt':
        raise ValueError('Native execution requires Linux/WSL')
    verify_frozen()
    protocol, historical = read(WORK / 'protocol.json'), read(WORK / 'historical-inputs.json')
    write(WORK / 'dispatch-start.json', {'contract_sha256': sha(WORK / EXECUTION_CONTRACT),
        'families': list(FAMILIES), 'resubmission': False, 'historical_jobs': 66})
    errors, prepared, results = [], {}, {}
    for family in PRIOR_COUNTS:
        prepared[family] = import_family(family, historical['families'][family])
    prepared.update(parallel_lanes(new_baseline, NEW_FAMILIES, errors, 'baseline'))
    for family in ('legacy', 'embeddings'):
        results[family] = search_family(family, prepared[family], historical, protocol)
    order = [f for f in protocol['continuation']['search_order'] if f in prepared]
    results.update(parallel_lanes(lambda f: search_family(f, prepared[f], historical, protocol), order, errors, 'search'))
    if errors or set(results) != set(FAMILIES):
        write(WORK / 'development-stop.json', {'status': 'incomplete', 'errors': errors,
            'terminal_families': sorted(results), 'validation_opened': False})
        raise RuntimeError('Preserve incomplete lanes; joint selection is unavailable')
    profile = PROFILES.baseline_profile()
    for family, row in results.items():
        profile[family] = row['profile'][family]
    write(WORK / 'family-sweep-complete.json', {'status': 'family-searches-complete-joint-replay-pending',
        'profile': profile, 'historical_incomplete_hypotheses': 2,
        'families': [{k: row[k] for k in ('family', 'treatment', 'generation', 'baseline_score', 'score', 'final_archive', 'winner')}
                     for _, row in sorted(results.items())], 'validation_opened': False})


if __name__ == '__main__':
    run()
