"""Publish a measured E8 family prefix without dispatching or selecting trials."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import sys

REPO = Path(__file__).resolve().parents[1]
WORK = REPO / 'tmp/e8'
HISTORY = REPO / 'tmp/e7'
spec = importlib.util.spec_from_file_location('enterprise_progress_core', REPO / 'evaluations/publish_enterprise_stratified.py')
CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CORE)


def verify_report_files(contract):
    """Verify frozen artifact inputs without admitting a new live execution."""
    count = 0
    for base, key in ((REPO, 'source_files'), (WORK, 'workspace_files'), (HISTORY, 'historical_files')):
        for relative, expected in contract[key].items():
            path = PurePosixPath(relative.replace('\\', '/'))
            if path.is_absolute() or '..' in path.parts or ':' in relative:
                raise ValueError('Invalid frozen report source path')
            if CORE.sha(base / path) != expected:
                raise ValueError('Frozen report source integrity mismatch')
            count += 1
    for path, expected in contract['external_read_only_files'].items():
        if not path.startswith('/mnt/c/') or CORE.sha(CORE.host(path)) != expected:
            raise ValueError('Frozen external report source integrity mismatch')
        count += 1
    return count


def verify_report_state(state):
    """Keep intermediate derivation within sealed development and closed gates."""
    if (not state['designSeal'] or state['validationRelease'] or state['holdoutRelease']
            or state['stages']['evolve']['status'] != 'running'):
        raise ValueError('Expected sealed active development with unopened private gates')


def verify_report_sources():
    """Check native organizer/source commitments; do not invoke runtime admission."""
    contract_path = WORK / 'execution-contract-v2.json'
    count = verify_report_files(CORE.read(contract_path))
    owner_path = REPO.parent / 'skill-arena/skills/harbor-organize-evaluations/scripts/manage_harbor_evaluations.py'
    owner_spec = importlib.util.spec_from_file_location('enterprise_report_organizer', owner_path)
    owner = importlib.util.module_from_spec(owner_spec)
    sys.modules[owner_spec.name] = owner
    try:
        owner_spec.loader.exec_module(owner)
        state = owner.build_state(WORK / 'study', verify_sources=True)
        verify_report_state(state)
    finally:
        sys.modules.pop(owner_spec.name, None)
    return {'scope': 'artifact-only', 'verified_files': count,
        'execution_contract_sha256': CORE.sha(contract_path),
        'organizer_source_verification': True, 'private_released': False,
        'live_dispatch_admission_performed': False, 'native_jobs_dispatched': 0}


def load_controller():
    """Load the sealed deterministic replay helpers without executing a search."""
    folder = REPO / 'evaluations/enterprise-continuation'
    before = sys.modules.copy()
    keys = ('prepare', 'native', 'run', 'study_guard')
    sys.path.insert(0, str(folder))
    try:
        for key in keys:
            sys.modules.pop(key, None)
        spec = importlib.util.spec_from_file_location('e8_progress_replay', folder / 'run.py')
        controller = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(controller)
        return controller
    finally:
        sys.path.remove(str(folder))
        for key in keys:
            sys.modules.pop(key, None)
            if key in before:
                sys.modules[key] = before[key]


def weighted_group(questions, cases, indices):
    """Aggregate native case metrics with the frozen population weights."""
    if len(questions) != len(cases):
        raise ValueError('Case count differs from frozen metadata')
    eligible = []
    for index in indices:
        question, case = questions[index], cases[index]
        if (case is not None) != bool(question['expected_doc_ids']):
            raise ValueError('Case eligibility differs from frozen metadata')
        if case is not None:
            weight = CORE.finite(question['population_to_sample_weight'])
            if weight <= 0:
                raise ValueError('Eligible population weight must be positive')
            eligible.append((weight, case))
    weight = sum(w for w, _ in eligible)
    return {'questions': len(indices), 'retrieval_eligible': len(eligible), 'population_weight': weight,
        **{key: sum(w * CORE.finite(case[key], upper=1) for w, case in eligible) / weight if eligible else None
           for key in CORE.METRICS}}


def paired_cases(questions, left, right, indices):
    """Count descriptive case changes; do not infer independent task counts."""
    weighted_group(questions, left, indices)
    weighted_group(questions, right, indices)
    deltas = [right[i]['ndcg_at_10'] - left[i]['ndcg_at_10'] for i in indices if left[i] is not None]
    return {'improved': sum(d > 1e-12 for d in deltas), 'regressed': sum(d < -1e-12 for d in deltas),
        'tied': sum(abs(d) <= 1e-12 for d in deltas), 'without_references': len(indices) - len(deltas)}


def verify_normalized(value, directories):
    """Require the exact ordered native comparison and its locked fairness basis."""
    jobs = value['jobs']
    comparison = value['comparison']
    observed = [CORE.host(row['jobDirectory']).resolve() for row in jobs]
    if (value['source'] != 'harbor' or value['harborVersion'] != '0.18.0'
            or value['rewardKey'] != 'reward' or value['passThreshold'] != .8
            or observed != [p.resolve() for p in directories] or len(set(observed)) != len(observed)
            or not all(row['complete'] and not row['completenessProblems'] for row in jobs)
            or not comparison['enabled'] or comparison['fairnessBasis'] != 'lock-and-trial-results'
            or comparison['warning'] is not None or comparison['baseline'] != jobs[0]['label']):
        raise ValueError('Native comparison is incomplete, reordered or does not bind the measured jobs')


def replay_prefix(controller, family, generation, protocol, history):
    """Verify every cumulative decision through an explicit completed generation."""
    if type(generation) is not int or generation < 1:
        raise ValueError('A positive completed generation is required')
    base_path = WORK / 'search' / family / 'development/generation-000/pareto-archive.json'
    base = CORE.read(base_path)
    original = history['families'].get(family)
    if original:
        schedule, _ = controller.replay_history(family, original, base['candidateResults'], protocol)
    else:
        native, = [r for r in base['candidateResults'] if r['candidateId'] == 'baseline']
        if not native['evaluable'] or not native['qualification']['passed']:
            raise ValueError('Baseline lacks qualified native evidence')
        schedule = controller.SCHEDULER.Sweep(protocol['strategies'][family], 'baseline',
            native['summary']['meanReward'], controller.PROFILES.baseline_profile(),
            max_rounds=protocol['budget']['maximum_outer_rounds'])
    if family in history['unavailable']:
        controller.exclude_interrupted(schedule, family, history['unavailable'][family])
    bindings = []
    for index in range(1, generation + 1):
        progress_path = WORK / 'progress' / family / f'{index:03d}.json'
        progress = CORE.read(progress_path)
        outcome = progress['outcome']
        proposed = controller.next_unique(schedule, family)
        if proposed is None or outcome['strategy'] != proposed[0]['id'] or outcome['variant'] != proposed[1]:
            raise ValueError('Completed prefix differs from the declared proposal order')
        if outcome['candidate'] != f'continuation-{index:03d}' or outcome['historical'] is not False:
            raise ValueError('Completed opportunity has a different identity or exposure')
        archive_path = WORK / 'search' / family / 'development' / f'generation-{index:03d}/pareto-archive.json'
        if CORE.host(outcome['archive']).resolve() != archive_path.resolve():
            raise ValueError('Outcome points outside its exact native generation')
        archive = CORE.read(archive_path)
        native, = [r for r in archive['candidateResults'] if r['candidateId'] == outcome['candidate']]
        if (not archive['promotionEligibleProfile'] or not native['promotionEligibleProvenance']
                or native['summary']['meanReward'] != outcome['score']
                or native['qualification']['passed'] != outcome['qualified']):
            raise ValueError('Outcome differs from native fitness or provenance')
        previous = {'candidate': schedule.best_id, 'score': schedule.best_score}
        improved = schedule.observe(outcome['candidate'], proposed[2], outcome['score'],
            qualified=outcome['qualified'], evaluable=native['evaluable'])
        if (improved != outcome['improved'] or schedule.best_id != outcome['best_candidate']
                or schedule.best_score != outcome['best_score'] or schedule.failures != outcome['consecutive_failures']
                or archive['bestAggregateCandidate'] != schedule.best_id or progress['events'] != schedule.events):
            raise ValueError('Published retention or miss counter differs from cumulative replay')
        bindings.append({'generation': index, 'progress_sha256': CORE.sha(progress_path),
            'archive_sha256': CORE.sha(archive_path)})
    return outcome, previous, proposed[2], archive, bindings


def inspect_measurement(family, native, questions):
    """Verify one completed native trial and all weighted route aggregates."""
    if (not native['evaluable'] or not native['promotionEligibleProvenance']
            or not native['qualification']['passed'] or native['summary']['errorCount']):
        raise ValueError('A quality comparison requires a qualified error-free measurement')
    directory = CORE.host(native['jobDirectory'])
    job = CORE.read(directory / 'result.json')
    stats = job['stats']
    if (not job['finished_at'] or job['n_total_trials'] != 1 or stats['n_completed_trials'] != 1
            or any(stats[key] for key in ('n_running_trials', 'n_pending_trials', 'n_cancelled_trials', 'n_errored_trials', 'n_retries'))):
        raise ValueError('Original native job is incomplete, failed or retried')
    trial_path, = directory.glob('*/result.json')
    trial = CORE.read(trial_path)
    if trial['exception_info'] or trial['verifier_result']['rewards']['evidence_integrity'] != 1:
        raise ValueError('Original native trial lacks evidence integrity')
    diagnostics_path = trial_path.parent / 'verifier/diagnostics.json'
    diagnostic = CORE.read(diagnostics_path)
    CORE.require_family_routes(family, diagnostic)
    if diagnostic['status'] != 'pass' or diagnostic['question_count'] != 120 or len(questions) != 120:
        raise ValueError('Original development scope changed')
    indices = list(range(120))
    for route in CORE.ROUTES[family]:
        aggregate = weighted_group(questions, diagnostic['cases'][route], indices)
        if aggregate['retrieval_eligible'] != 112 or aggregate['population_weight'] != 470:
            raise ValueError('Original development denominator changed')
        if any(not math.isclose(aggregate[key], CORE.finite(diagnostic['routes'][route][key], upper=1),
                                abs_tol=1e-12, rel_tol=0) for key in CORE.METRICS):
            raise ValueError('Native weighted route aggregate differs from its cases')
        CORE.finite(diagnostic['routes'][route]['p95_ms'])
    score = diagnostic['routes'][CORE.PRIMARY[family]]['ndcg_at_10']
    if any(score != value for value in (native['summary']['meanReward'], native['summary']['observedMeanReward'],
                                        trial['verifier_result']['rewards']['reward'])):
        raise ValueError('Native primary reward differs from its route')
    row = {'candidate': native['candidateId'], 'primary_route': CORE.PRIMARY[family], 'routes': diagnostic['routes'],
        'score': score, 'skill_digest': native['skillDigest'], 'native_job_seconds': CORE.elapsed(job),
        'agent_seconds': CORE.elapsed(trial['agent_execution']), 'double_build_seconds': CORE.finite(diagnostic['build_seconds']),
        'knowledge_bytes': CORE.finite(diagnostic['knowledge_bytes']), 'evidence_integrity': 1, 'native_errors': 0, 'retries': 0,
        'native_result_sha256': CORE.sha(directory / 'result.json'), 'native_lock_sha256': CORE.sha(directory / 'lock.json'),
        'trial_result_sha256': CORE.sha(trial_path), 'diagnostics_sha256': CORE.sha(diagnostics_path)}
    return directory, row, diagnostic['cases'][CORE.PRIMARY[family]]


def collect(family, generation, normalized_path):
    """Collect one exact development prefix; sealed validation stays closed."""
    report_verification = verify_report_sources()
    protocol = CORE.read(WORK / 'protocol.json')
    contract = CORE.read(WORK / 'execution-contract-v2.json')
    history_path = WORK / 'historical-inputs.json'
    history = CORE.read(history_path)
    selection = HISTORY / 'development-selection-v2/selected.private.json'
    if (CORE.sha(history_path) != protocol['historical_inputs_sha256']
            or CORE.sha(history_path) != contract['workspace_files']['historical-inputs.json']
            or CORE.sha(selection) != protocol['development']['selection_sha256']):
        raise ValueError('Frozen historical evidence or question selection changed')
    questions = sorted(CORE.read(selection), key=lambda q: q['question_id'])
    if len(questions) != 120 or len({q['question_id'] for q in questions}) != 120:
        raise ValueError('Original question identities changed')
    outcome, previous, profile, archive, prefix = replay_prefix(load_controller(), family, generation, protocol, history)
    identifiers = list(dict.fromkeys(('baseline', previous['candidate'], outcome['candidate'])))
    rows, arrays, directories = [], {}, []
    historical_jobs = {record['candidate']['jobDirectory'] for records in history['families'].values() for record in records}
    for identifier in identifiers:
        native, = [r for r in archive['candidateResults'] if r['candidateId'] == identifier]
        directory, row, arrays[identifier] = inspect_measurement(family, native, questions)
        row['historical_job'] = native['jobDirectory'] in historical_jobs
        directories.append(directory)
        rows.append(row)
    if rows[-1]['score'] != outcome['score'] or next(r['score'] for r in rows if r['candidate'] == previous['candidate']) != previous['score']:
        raise ValueError('Comparison does not reproduce the actual previous incumbent and candidate')
    verify_normalized(CORE.read(normalized_path), directories)
    groups = defaultdict(list)
    groups[('all', 'all')] = list(range(120))
    for i, question in enumerate(questions):
        groups[('category', question['question_type'])].append(i)
        for application in set(question['source_types']):
            groups[('application', application)].append(i)
    subgroups = []
    for (dimension, group), indices in sorted(groups.items()):
        metrics = {identifier: weighted_group(questions, arrays[identifier], indices) for identifier in identifiers}
        candidate = metrics[outcome['candidate']]
        subgroups.append({'dimension': dimension, 'group': group, 'metrics': metrics,
            'comparisons': [{'reference': reference, 'delta_percentage_points':
                (candidate['ndcg_at_10'] - metrics[reference]['ndcg_at_10']) * 100 if candidate['retrieval_eligible'] else None,
                'paired_cases': paired_cases(questions, arrays[reference], arrays[outcome['candidate']], indices)}
                for reference in identifiers[:-1]]})
    return {'schema_version': 'enterprise-family-prefix-report/1.0', 'campaign': 'E8', 'status': 'partial-development',
        'report_input_verification': report_verification,
        'snapshot_utc': datetime.now(timezone.utc).isoformat(), 'family': family, 'through_generation': generation,
        'treatment': protocol['treatments'][family], 'primary_route': CORE.PRIMARY[family], 'rows': rows, 'groups': subgroups,
        'candidate': outcome['candidate'], 'previous_incumbent': previous, 'retained_candidate': outcome['best_candidate'],
        'improved_previous_incumbent': outcome['improved'], 'consecutive_misses': outcome['consecutive_failures'],
        'mechanism': outcome['strategy'], 'variant': outcome['variant'], 'declared_family_profile': profile[family],
        'prefix_bindings': prefix, 'questions': 120, 'retrieval_eligible': 112, 'eligible_population_weight': 470,
        'corpus_documents': 6000, 'llm_calls': 0, 'provider_cost_usd': None, 'validation_released': False,
        'profile_promoted': False, 'selection_final': False, 'all500_recalculation_complete': False,
        'unavailable_original_hypotheses': int(family in history['unavailable']),
        'historical_inputs_sha256': CORE.sha(history_path), 'protocol_sha256': CORE.sha(WORK / 'protocol.json'),
        'execution_contract_sha256': CORE.sha(WORK / 'execution-contract-v2.json'), 'selection_sha256': CORE.sha(selection),
        'normalized_report_sha256': CORE.sha(normalized_path)}


def render(value):
    """Keep baseline gain, incremental gain, subgroup tradeoffs and CTA distinct."""
    rows = value['rows']
    candidate = rows[-1]
    previous = value['previous_incumbent']
    lines = ['# E8 development: ' + value['family'], '', 'Snapshot: ' + value['snapshot_utc'] + '.', '',
        'The observed candidate is `' + candidate['candidate'] + '`. Its weighted nDCG@10 changed by '
        f"{100 * (candidate['score'] - rows[0]['score']):+.2f} percentage points versus baseline and "
        f"{100 * (candidate['score'] - previous['score']):+.2f} versus the previous incumbent `" + previous['candidate'] + '`.', '',
        'Recorded retention: `' + value['retained_candidate'] + '`. Consecutive misses after this opportunity: '
        + str(value['consecutive_misses']) + '. These decisions were replayed from the complete cumulative prefix.', '',
        '| Candidate | Weighted nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 | Historical job |',
        '| --- | ---: | ---: | ---: | ---: | --- |']
    for row in rows:
        lines.append('| ' + row['candidate'] + ' | ' + ' | '.join(CORE.number(row['routes'][value['primary_route']][k]) for k in CORE.METRICS)
                     + ' | ' + str(row['historical_job']) + ' |')
    lines += ['', 'Quality columns are percentages. The primary route remains `' + value['primary_route'] + '`. '
        'The comparison uses 120 exposed development questions, 112 eligible cases and category weights totaling 470, '
        'on 6,000 reference-enriched complete documents. Eight questions without references have no retrieval score.', '',
        'Mechanism: `' + value['mechanism'] + '`. Treatment: ' + value['treatment'] + '.', '',
        '```json', json.dumps(value['variant'], indent=2, sort_keys=True), '```', '',
        'This is an intermediate retrieval measurement. It does not establish all-500 performance, answer Overall, '
        'an official public rank, final selection, acceptance or installation. Diagnostic routes and application '
        'subgroups do not change retention. The separate native diagnostic reward threshold is 0.8.', '',
        '[Applications and categories](groups.md) · [All diagnostic routes](routes.md) · '
        '[Cost, time and quality](cta.md) · [Exact aggregate and evidence hashes](aggregate.json) · [Campaign](../README.md)']
    if value['family'] == 'turso':
        lines += ['', 'The registered `lexical-sql` route keeps its identifier across two execution modes. '
            'The original empty-profile baseline ranks parameterized SQL substring presence. A nonempty '
            'candidate profile loads canonical records from Turso and ranks normalized tokens with BM25 '
            'in memory. The first gain therefore includes an algorithm and token-matching change; '
            'later changes must be assessed against their actual BM25 parent. No SQL BM25 index or '
            'database schema change is implied.', '',
            'The [generated-expert delivery audit](../../e7/turso-generated-expert-001/README.md) '
            'also distinguishes this measured consultation wrapper from the portable expert default. '
            'A profile gain does not prove automatic inheritance by generated experts.']
    files = {'README.md': '\n'.join(lines) + '\n'}
    lines = ['# Applications and categories', '', '[Family report](README.md)', '',
        'Scores retain the frozen population weights. Application groups overlap and are not independent datasets. '
        'Paired case counts are unweighted. No-reference groups remain unscored.', '',
        '| Dimension | Group | Reference | Eligible | Candidate nDCG@10 | Delta pp | Improved / regressed / tied / no reference |',
        '| --- | --- | --- | ---: | ---: | ---: | --- |']
    for group in value['groups']:
        metrics = group['metrics'][value['candidate']]
        for comparison in group['comparisons']:
            counts = comparison['paired_cases']
            lines.append(f"| {group['dimension']} | {group['group']} | {comparison['reference']} | {metrics['retrieval_eligible']} | "
                f"{CORE.number(metrics['ndcg_at_10'])} | {CORE.number(comparison['delta_percentage_points'], 1)} | "
                + ' / '.join(str(counts[k]) for k in ('improved', 'regressed', 'tied', 'without_references')) + ' |')
    files['groups.md'] = '\n'.join(lines) + '\n'
    lines = ['# Native route diagnostics', '', '[Family report](README.md)', '',
        '| Route | Candidate | Weighted nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
    for route in CORE.ROUTES[value['family']]:
        for row in rows:
            lines.append('| ' + route + ' | ' + row['candidate'] + ' | '
                + ' | '.join(CORE.number(row['routes'][route][k]) for k in CORE.METRICS) + ' |')
    files['routes.md'] = '\n'.join(lines) + '\n'
    lines = ['# Cost, time and quality', '', '[Family report](README.md)', '',
        'Two CPU threads and 6 GiB per agent, with at most two concurrent trials. These original jobs have zero '
        'LLM calls, evidence integrity 1, no execution errors and zero retries. CPU inference and host costs are unpriced; '
        'provider cost is N/A. Historical jobs keep their original timing across the host restart.', '',
        '| Candidate | Native job s | Agent s | Double build s | Knowledge MiB | Primary query P95 ms |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for row in rows:
        values = (row['native_job_seconds'], row['agent_seconds'], row['double_build_seconds'],
                  row['knowledge_bytes'] / 2**20, row['routes'][value['primary_route']]['p95_ms'])
        lines.append('| ' + row['candidate'] + ' | ' + ' | '.join(CORE.number(v, 1) for v in values) + ' |')
    lines += ['', 'Timings exclude staging and supervisor overhead. The displayed jobs are selected measurement references, '
        'not the total campaign workload. Incomplete historical attempts are not assigned zero time.']
    files['cta.md'] = '\n'.join(lines) + '\n'
    return files


def main():
    """Write a new report only after exact native evidence validation succeeds."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', required=True, choices=tuple(CORE.PRIMARY))
    parser.add_argument('--generation', required=True, type=int)
    parser.add_argument('--normalized-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    value = collect(args.family, args.generation, args.normalized_report)
    files = render(value)
    files['aggregate.json'] = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    args.output.mkdir(parents=True, exist_ok=False)
    for name, text in files.items():
        (args.output / name).write_text(text, encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'published-measured-prefix', 'family': args.family,
        'through_generation': args.generation, 'improved_previous_incumbent': value['improved_previous_incumbent']}))


if __name__ == '__main__':
    main()
