"""Prepare prospective E8 controls while retaining immutable E7 inputs."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORK = REPO / 'tmp/e8'
EXECUTION_CONTRACT = 'execution-contract-v2.json'
HISTORY = REPO / 'tmp/e7'
OLD = REPO / 'tmp/e5'
NAME = 'build-semantic-okf-knowledge-skill'
HPY = '/home/villa/.local/share/uv/tools/harbor/bin/python'
ORGANIZER = REPO.parent / 'skill-arena/skills/harbor-organize-evaluations/scripts/manage_harbor_evaluations.py'
OWNER = Path(('C:/Users/villa' if os.name == 'nt' else '/mnt/c/Users/villa') + '/.codex/skills/harbor-reflective-pareto-search/scripts/harbor_reflective_pareto.py')


def load(name, path):
    """Load one explicit source file without modifying its directory."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PROFILES = load('e8_profiles', REPO / 'evaluations/enterprise-stratified-evolution/profiles.py')
SCHEDULER = load('e8_scheduler', REPO / 'evaluations/enterprise-stratified-evolution/sweep.py')
FAMILIES, CONSTRUCTION = PROFILES.FAMILIES, PROFILES.CONSTRUCTION
PRIOR_COUNTS = {'legacy': 16, 'embeddings': 6, 'classical': 22, 'adaptive': 18}
NEW_FAMILIES = ('turso', 'graphify', 'entity-graph', 'ensemble')


def read(path):
    """Read a declared JSON artifact."""
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    """Hash exact regular-file bytes."""
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def tree(root):
    """Inventory an unlinked artifact tree without including metadata."""
    result = {}
    for path in sorted(Path(root).rglob('*')):
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise ValueError('Linked artifact')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha(path)
    return result


def write(path, value):
    """Write new evidence once; an existing destination is an error."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def posix(path):
    """Resolve a shared path for native WSL execution."""
    path = Path(path).resolve()
    return '/mnt/' + path.drive[0].lower() + '/' + path.as_posix().split(':/', 1)[1] if os.name == 'nt' else str(path)


def host(value):
    """Resolve a shared path on the registering host."""
    return Path('C:/' + value[len('/mnt/c/'):]) if os.name == 'nt' and str(value).startswith('/mnt/c/') else Path(value)


def organize(action, *args):
    """Invoke the maintained organizer and preserve its exact response."""
    logs = WORK / 'logs/organizer'
    logs.mkdir(parents=True, exist_ok=True)
    number = len(list(logs.glob('*.log')))
    with (logs / f'{number:03d}-{action}.log').open('xb') as stream:
        result = subprocess.run([sys.executable, '-B', str(ORGANIZER), action, str(WORK / 'study'), *map(str, args)],
                                stdout=stream, stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise RuntimeError(f'Organizer rejected {action}; inspect the preserved log')


def historical_inputs():
    """Bind completed original jobs and unavailable proposals without rescoring."""
    closure = read(HISTORY / 'interruption-001/closure.json')
    if closure['status'] != 'stopped-no-private-release' or closure['validation_released']:
        raise ValueError('Terminal unconsumed E7 is required')
    result = {'schema_version': 'enterprise-historical-inputs/1.0', 'source_study': 'enterprise-e7',
        'closure_sha256': sha(HISTORY / 'interruption-001/closure.json'),
        'ledger_sha256': sha(HISTORY / 'study/ledger.jsonl'), 'families': {}, 'unavailable': {}}
    for family, count in PRIOR_COUNTS.items():
        rows = []
        for generation in range(count + 1):
            folder = HISTORY / 'dispatch' / family / f'generation-{generation:03d}'
            config = read(folder / 'analyze.json')
            identifier = 'baseline' if generation == 0 else f'candidate-{generation:03d}'
            candidate = next(c for c in config['candidates'] if c['id'] == identifier)
            job, skill = host(candidate['jobDirectory']), host(candidate['skill'])
            native = read(job / 'result.json')
            if not native['finished_at']:
                raise ValueError('Only complete native jobs may be historical analysis inputs')
            rows.append({'generation': generation, 'candidate': candidate,
                'archive': posix(HISTORY / 'search' / family / 'development' / f'generation-{generation:03d}' / 'pareto-archive.json'),
                'job_files': tree(job), 'skill_files': tree(skill),
                'profile': read(skill / 'assets/retrieval-profile.json'),
                'analyze_config_sha256': sha(folder / 'analyze.json'),
                'outcome': None if generation == 0 else read(HISTORY / 'progress' / family / f'{generation:03d}.json')['outcome']})
        result['families'][family] = rows
    for family, generation in (('classical', 23), ('adaptive', 19)):
        contract = HISTORY / 'realizations' / family / f'candidate-{generation:03d}' / 'mutation-contract.json'
        original = read(contract)
        result['unavailable'][family] = {'candidate': f'candidate-{generation:03d}',
            'profile': original['exact_profile'], 'profile_sha256': SCHEDULER.digest(original['exact_profile']),
            'contract_sha256': sha(contract), 'contract': posix(contract),
            'fitness': None, 'counts_as_evaluable_miss': False, 'reissue_permitted': False}
    assert sum(len(v) for v in result['families'].values()) == 66
    write(WORK / 'historical-inputs.json', result)
    return result


def scaffold():
    """Create new controls without executing candidates or reading private tasks."""
    if (WORK / 'protocol.json').exists():
        raise ValueError('E8 scaffold already exists')
    imported = historical_inputs()
    shutil.copytree(HISTORY / 'baseline' / NAME, WORK / 'baseline' / NAME)
    shutil.copyfile(HISTORY / 'enterprise_agent.py', WORK / 'enterprise_agent.py')
    shutil.copyfile(HISTORY / 'development-task-map.json', WORK / 'development-task-map.json')
    protocol = read(HISTORY / 'protocol.json')
    protocol.update(id='enterprise-e8', schema_version='enterprise-stratified-continuation/1.0')
    protocol['historical_inputs_sha256'] = sha(WORK / 'historical-inputs.json')
    protocol['continuation'] = {
        'source_study': 'enterprise-e7', 'source_state': 'interrupted-terminal-no-private-release',
        'historical_completed_jobs': 66, 'historical_completed_variants': 62,
        'historical_incomplete_variants': 2, 'historical_qualified_jobs': 60,
        'historical_execution_errors': 6, 'reset_budget': False,
        'first_new_baselines': list(NEW_FAMILIES),
        'search_order': [*NEW_FAMILIES, 'classical', 'adaptive'],
        'terminal_families_imported_without_new_search': ['legacy', 'embeddings'],
        'replay': 'Revalidate all exact completed candidate/job mappings in new native generation-zero archives. Reconstruct E7 counters, incumbents, complete-profile history and round positions from its exact full measured prefix.',
        'unavailable': {f: {k: v for k, v in row.items() if k != 'profile'} for f, row in imported['unavailable'].items()},
        'unavailable_policy': 'Permanently reserve each interrupted complete profile; skip it without score, miss or counter reset. No reissue under a new identifier. Disclose unavailable hypothesis coverage in stopping and final claims.',
        'dispatch': 'Complete an initial baseline pass for all four unstarted families, with two workers. Then search all six unfinished lanes. Failure stops its lane and is preserved; other independent lanes continue. All eight qualified terminal selections remain required for joint replay.',
        'restart': 'No automatic retry or rerun. Exclusive run artifacts reject duplicate supervisors. An incomplete new native cell stops its lane for owner review; it cannot be inferred complete.',
        'memory': 'Historical development and optimizer notes remain host-only, outside all candidate bundles, task images and executor mounts.',
        'runtime': 'Original development, joint and private agent/task limits stay fixed. Retrospective JobConfig and final adapter declare a paired 10800-second limit before execution; original task bytes remain unchanged.',
        'timing_claim': 'Host restarted with WSL kernel and Docker identity captured at preflight. Historical versus new timing is descriptive, not a paired speed claim; exact joint replay must reproduce quality.',
    }
    protocol['budget'].update(maximum_additional_variants=585-64, inherited_started_variants=64,
        additional_baseline_trials=4, historical_completed_trials=66, historical_incomplete_trials=2)
    protocol['failure_rule'] += ' E8 inherits consumed rounds and attempts. The two historical unavailable profiles are excluded without fitness or an evaluable miss; stopping must report that incomplete hypothesis coverage.'
    write(WORK / 'protocol.json', protocol)
    print(json.dumps({'status': 'draft-not-registered-or-sealed', 'historical_jobs': 66, 'new_trials': 0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['scaffold'])
    parser.parse_args()
    scaffold()
