"""Publish all observed development rows without completing an interrupted generation."""
from __future__ import annotations

import json
import math
from pathlib import Path

from aggregate_campaign import FIELDS, PROFILES
from aggregate_development import (best_by_dataset, change_counts, elapsed_seconds, host_path,
                                   number, primary_changes, read, render_comparison,
                                   write_csv, write_navigation_views)
from bridge import PRIMARY
from prepare_experiment import REPO, WORK, sha, tree, write_json
from run_search import verified_state

ROUTES = {
    'legacy': {'lexical'}, 'embeddings': {'hybrid', 'lexical', 'vector'},
    'classical': {'association', 'bm25', 'fusion', 'topic'}, 'adaptive': {'adaptive'},
    'entity-graph': {'entity', 'fusion', 'lexical', 'traversal'},
    'ensemble': {'fast', 'quality', 'robust'}, 'graphify': {'search'}, 'turso': {'lexical-sql'},
}
DATASETS = {'architecture', 'astro', 'data-science', 'enterprise'}


def quality(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Expected a finite quality value on the original 0-1 scale')
    return value


def project_job(job, metadata):
    """Preserve the missing cell and keep a partial mean out of every ranking."""
    profile = job['label'].removeprefix('knowledge-retrieval-e5-g001-development-')
    if profile not in PROFILES[1] or len(metadata) != 32:
        raise ValueError('Unexpected development job or task membership')
    expected = {(dataset, family) for dataset in DATASETS for family in PRIMARY}
    if {(row['source_cohort'], row['family']) for row in metadata.values()} != expected:
        raise ValueError('Only the declared public development taxonomy may be projected')
    directory = host_path(job['jobDirectory'])
    native = read(directory / 'result.json')
    stats = native['stats']
    summary = job['summary']
    trial_paths = sorted(directory.glob('*/result.json'))
    if (native['n_total_trials'] != 32 or summary['requestedTrials'] != 32
            or stats['n_completed_trials'] != len(trial_paths)
            or summary['completedTrials'] != len(trial_paths)
            or summary['erroredTrials'] != stats['n_errored_trials']):
        raise ValueError('Native source and reporter completion disagree')
    if job['complete'] and (len(trial_paths) != 32 or native['finished_at'] is None or job['completenessProblems']):
        raise ValueError('An incomplete source cannot be presented as complete')
    seen, routes, failures = set(), [], []
    for path in trial_paths:
        trial = read(path)
        identity = trial['task_name']
        if identity not in metadata or identity in seen:
            raise ValueError('Unexpected or duplicate development trial')
        seen.add(identity)
        item = metadata[identity]
        common = {'candidate': profile, 'dataset': item['source_cohort'], 'family': item['family']}
        diagnostic_path = path.parent / 'verifier/diagnostics.json'
        diagnostic = read(diagnostic_path) if diagnostic_path.exists() else {}
        rewards = (trial.get('verifier_result') or {}).get('rewards') or {}
        if trial.get('exception_info') or rewards.get('evidence_integrity') != 1 or diagnostic.get('status') != 'pass':
            failures.append({**common, 'status': 'non-evaluable', 'error_type': 'native-execution-or-integrity-failure'})
            continue
        if diagnostic['question_count'] != 40 or set(diagnostic['routes']) != ROUTES[item['family']]:
            raise ValueError('The declared route grid or query cohort changed')
        primary = diagnostic['routes'][PRIMARY[item['family']]]['ndcg_at_10']
        if not math.isclose(quality(rewards['reward']), quality(primary), abs_tol=1e-12, rel_tol=0):
            raise ValueError('Primary route and native reward disagree')
        for route, metrics in diagnostic['routes'].items():
            row = {**common, 'route': route, 'primary': route == PRIMARY[item['family']], 'questions': 40,
                   **{key: quality(metrics[key]) for key in ('ndcg_at_10', 'recall_at_10', 'mrr_at_10', 'full_qrel_coverage_at_10')},
                   'p95_ms': metrics['p95_ms'], 'double_build_seconds': diagnostic['build_seconds'],
                   'knowledge_bytes': diagnostic['knowledge_bytes'],
                   'agent_execution_seconds': elapsed_seconds(trial.get('agent_execution')),
                   'native_trial_seconds': elapsed_seconds(trial)}
            for key in ('p95_ms', 'double_build_seconds', 'knowledge_bytes', 'agent_execution_seconds', 'native_trial_seconds'):
                value = row[key]
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                    raise ValueError('Resource measurements must be finite nonnegative values or unavailable')
            routes.append(row)
    for identity in sorted(set(metadata) - seen):
        item = metadata[identity]
        failures.append({'candidate': profile, 'dataset': item['source_cohort'], 'family': item['family'],
                         'status': 'interrupted-no-native-result', 'error_type': 'unavailable'})
    qualified = bool(job['complete'] and len(seen) == 32 and not failures and stats['n_errored_trials'] == 0)
    metrics = [metric for group in stats['evals'].values() for metric in group['metrics']]
    if len(metrics) != 1 or len(job['skillProvenance']) != 1:
        raise ValueError('Expected one declared native evaluation profile and skill')
    mean = quality(metrics[0]['reward'])
    if not math.isclose(mean, quality(summary['reward']['average']), abs_tol=1e-12, rel_tol=0):
        raise ValueError('Native reporter and source mean disagree')
    candidate = {'candidate': profile, 'qualified': qualified, 'expected_trials': 32, 'completed_trials': len(seen),
                 'errors': stats['n_errored_trials'], 'scored_trials': sum(row['primary'] for row in routes),
                 'mean_ndcg_at_10': mean if qualified else None, 'native_diagnostic_mean_reward': mean,
                 'skill_digest': job['skillProvenance'][0]['digest'], 'source_skill_digest': None,
                 'job_id': job['jobId'], 'job_result_sha256': sha(directory / 'result.json'),
                 'native_lock_sha256': sha(directory / 'lock.json')}
    return candidate, routes, failures


def combine(g0, g1):
    """Join descriptive rows with explicit generation IDs, without a Pareto archive."""
    data = {'schema_version': 'retrieval-interrupted-development/1.0', 'study': 'e5',
            'phase': 'interrupted-development-publication', 'validation_used': False,
            'native_generation_one_archive_available': False, 'selection_established': False,
            'promotion_established': False, 'candidates': [], 'routes': [], 'failures': [], 'primary_changes': []}
    for generation, source in enumerate((g0, g1)):
        if {row['candidate'] for row in source['candidates']} != PROFILES[generation]:
            raise ValueError('Every planned profile must remain in the interrupted report')
        for key, fields in FIELDS.items():
            for row in source[key]:
                data[key].append({**{field: row[field] for field in fields}, 'generation': generation,
                                  'profile': row['candidate'], 'candidate': f'g{generation}-' + row['candidate']})
    data.update(expected_native_trials=sum(row['expected_trials'] for row in data['candidates']),
                completed_native_trials=sum(row['completed_trials'] for row in data['candidates']),
                native_recorded_errors=sum(row['errors'] for row in data['candidates']))
    data['unavailable_native_trials'] = data['expected_native_trials'] - data['completed_native_trials']
    data['best_default_by_dataset'] = best_by_dataset(data)
    data['best_all_routes_by_dataset'] = best_by_dataset(data, primary_only=False)
    return data


def render(output, data):
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'aggregates.json', data)
    for key in FIELDS:
        write_csv(output / (key + '.csv'), data[key])
    navigation = write_navigation_views(output, data)
    qualification = {row['candidate']: row['qualified'] for row in data['candidates']}
    primary = [{**row, 'profile_qualified': qualification[row['candidate']]} for row in data['routes'] if row['primary']]
    write_csv(output / 'cta.csv', primary)
    lines = ['# Development comparison after an interrupted generation', '',
             '[Study overview](../README.md) · [Aggregate provenance](aggregates.json) · [CTA](cta.md)', '',
             f"**{data['completed_native_trials']} / {data['expected_native_trials']} native trials have results; {data['unavailable_native_trials']} is unavailable.** The controller and its last container stopped before generation one produced a native archive. Recorded native errors cover completed results only; zero recorded errors does not mean a complete campaign.", '',
             'This report preserves both generations, all ten measured runs of nine profiles, and the missing cell. It creates no archive or selection and opens no private gate. Generation zero retains its original archive; generation one has none. Qualified in these tables means all 32 cells are complete, error-free and meet the integrity gate. It does not imply archive membership or validation.', '',
             'Binary nDCG@10 uses a 0-100 display scale. Complete profile means equally weight the 32 default-route cells. Differences use each generation\'s own baseline. Repeated baselines retain separate identities and are not independent samples.', '',
             '| Run | Complete / expected | Recorded errors | Qualified | nDCG@10 | Gain, pp | Improved / tied / regressed |',
             '|---|---:|---:|---|---:|---:|---|']
    for row in sorted(data['candidates'], key=lambda row: (row['mean_ndcg_at_10'] is None, -(row['mean_ndcg_at_10'] or 0), row['candidate'])):
        counts = ' / '.join(str(row[key]) if row[key] is not None else 'unavailable' for key in ('improved_cells', 'unchanged_cells', 'regressed_cells'))
        lines.append(f"| [{row['candidate']}](by-profile/{row['candidate']}.md) | {row['completed_trials']} / {row['expected_trials']} | {row['errors']} | {row['qualified']} | {number(row['mean_ndcg_at_10'])} | {number(row['mean_gain'])} | {counts} |")
    for key, title in (('best_default_by_dataset', 'Best measured default skill on each dataset'), ('best_all_routes_by_dataset', 'Best measured strategy across all 18 routes')):
        lines += ['', '## ' + title, '', 'Only complete qualified profiles enter these descriptive maxima. A route maximum is not a validated routing policy.', '',
                  '| Dataset | Skill / route | nDCG@10 | Run(s) |', '|---|---|---:|---|']
        for row in data[key]:
            groups = {}
            for winner in row['winners']:
                label = winner['family'] + ' / ' + winner.get('route', PRIMARY[winner['family']])
                groups.setdefault(label, []).append(winner['profile'])
            for label, names in groups.items():
                lines.append(f"| [{row['dataset']}](by-dataset/{row['dataset']}.md) | {label} | {number(row['ndcg_at_10'])} | {', '.join(names)} |")
    lines += ['', '## Browse every measurement', '']
    for directory, names in navigation.items():
        lines += [directory + ': ' + ' · '.join(f'[{name}]({directory}/{name}.md)' for name in names), '']
    lines += ['## Unavailable evidence', '', '[All failed or missing cells](failures.csv). The interrupted Data-science / Ensemble cell has no native TrialResult, reward, final duration or verified build artifact. Its missing measurement is not set to zero or replaced with another profile. The partial profile\'s measured rows remain diagnostic, with no comparable mean, gain or win.', '',
              '![Generation-one measurements, including the unavailable cell](comparison.png)', '',
              '[Generation-zero comparison and chart](../generation-000/README.md) · [Every paired default cell](primary_changes.csv)', '',
              'These are reduced internal retrieval diagnostics, not official EnterpriseRAG answer-quality scores or full BEIR results. The independent validation portfolio remains sealed. No canonical profile is promoted by this report.', '']
    (output / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    cta = ['# Cost, time and accuracy of observed development trials', '', '[General comparison](README.md) · [Exact measurements](cta.csv)', '',
           'Each row preserves its generation and profile. Query P95 is one route/cohort measurement; percentiles are not pooled. Build time includes two builds and validators. Agent and native trial durations cover the complete evaluation, not one production query. Missing cells have no invented timing.', '',
           'The native trials recorded zero instruction-model tokens and provider charge. This excludes assistant research, authoring, review and orchestration. Local CPU/model execution is unpriced and the host was shared. No speedup guarantee follows from these descriptive timings.', '',
           '| Dataset | Family | Run | Qualified | nDCG@10 | Query P95 ms | Double build s | Agent s, all routes | Native trial s | Knowledge MiB |',
           '|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for row in sorted(primary, key=lambda row: (row['dataset'], row['family'], row['candidate'])):
        cta.append(f"| {row['dataset']} | {row['family']} | {row['candidate']} | {row['profile_qualified']} | {number(row['ndcg_at_10'])} | {row['p95_ms']:.2f} | {row['double_build_seconds']:.2f} | {number(row['agent_execution_seconds'], 1)} | {number(row['native_trial_seconds'], 1)} | {row['knowledge_bytes'] / 2**20:.2f} |")
    (output / 'cta.md').write_text('\n'.join(cta) + '\n', encoding='utf-8')


def main():
    state = verified_state()
    if state['validationRelease'] or state['holdoutRelease'] or state['stages']['evolve']['status'] != 'running':
        raise ValueError('Publish this diagnostic before terminal closure or private release')
    if (WORK / 'pareto/development/generation-001/pareto-archive.json').exists():
        raise ValueError('Use complete generation reporting when a native archive exists')
    native_root = WORK / 'native-reports/interrupted-generation-001'
    receipt = read(native_root / 'receipt.json')
    if not receipt['source_unchanged'] or receipt['native_jobs_started'] or receipt['validation_used']:
        raise ValueError('Expected read-only development normalization')
    if any(tree(Path(path)) != commitment for path, commitment in receipt['source_trees'].items()):
        raise ValueError('Interrupted native evidence changed after normalization')
    reports = []
    for label in ('complete-profiles', 'incomplete-profile'):
        path = native_root / label / 'final-report.json'
        if sha(path) != receipt['report_sha256'][label]:
            raise ValueError('Native report digest changed')
        report = read(path)
        if report['source'] != 'harbor' or report['rewardKey'] != 'reward':
            raise ValueError('Expected native Harbor reward reporting')
        reports.append(report)
    if reports[0]['comparison']['warning'] is not None or not reports[0]['comparison']['enabled'] or reports[1]['comparison']['enabled']:
        raise ValueError('Only complete native profiles may have a native comparison')
    jobs = [job for report in reports for job in report['jobs']]
    expected_paths = {str((WORK / 'pareto/development/generation-001/harbor-jobs' / ('knowledge-retrieval-e5-g001-development-' + name)).resolve()) for name in PROFILES[1]}
    if len(jobs) != 5 or {str(host_path(job['jobDirectory']).resolve()) for job in jobs} != expected_paths:
        raise ValueError('Source report job membership differs from the frozen generation')
    metadata = {row['task_id']: row for path in (WORK / 'curator/development').glob('*-tasks.json') for row in read(path)}
    g1 = {'candidates': [], 'routes': [], 'failures': []}
    for job in jobs:
        candidate, routes, failures = project_job(job, metadata)
        g1['candidates'].append(candidate)
        g1['routes'].extend(routes)
        g1['failures'].extend(failures)
    g1['primary_changes'] = primary_changes(g1)
    baseline = next(row['mean_ndcg_at_10'] for row in g1['candidates'] if row['candidate'] == 'baseline')
    for row in g1['candidates']:
        row.update(mean_gain=row['mean_ndcg_at_10'] - baseline if row['mean_ndcg_at_10'] is not None and baseline is not None else None,
                   **change_counts(row['candidate'], g1['primary_changes']))
    g0_path = REPO / 'evaluations/reports/evolution/e5/generation-000/aggregates.json'
    evidence = state['evidence']['generation-zero-public-report']
    if Path(evidence['source']).resolve() != g0_path.parent.resolve():
        raise ValueError('The first generation must be registered as immutable evidence')
    data = combine(read(g0_path), g1)
    data.update(generation_zero_aggregate_sha256=sha(g0_path), native_interruption_receipt_sha256=sha(native_root / 'receipt.json'),
                native_report_sha256=receipt['report_sha256'], reporter_sha256=sha(Path(__file__)),
                hardware_sha256=sha(WORK / 'hardware.json'))
    output = REPO / 'evaluations/reports/evolution/e5/interrupted-development-001'
    render(output, data)
    render_comparison(output, g1)
    print(json.dumps({'status': 'published-interrupted-development', 'completed': data['completed_native_trials'],
                      'expected': data['expected_native_trials'], 'route_rows': len(data['routes']), 'unavailable': data['unavailable_native_trials']}))


if __name__ == '__main__':
    main()
