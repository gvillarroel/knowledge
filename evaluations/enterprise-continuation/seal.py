"""Bind the E8 continuation and its immutable ancestry before independent review."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from prepare import HERE, REPO, WORK, HISTORY, NAME, EXECUTION_CONTRACT, read, write, tree, sha, posix, organize, host


def contract():
    """Create the prospective execution manifest without starting a stage."""
    prior = read(HISTORY / 'execution-contract.json')
    source_files = dict(prior['source_files'])
    source_files.update({p.relative_to(REPO).as_posix(): sha(p) for p in HERE.glob('*.py')})
    source_files[(HERE / 'origins.json').relative_to(REPO).as_posix()] = sha(HERE / 'origins.json')
    workspace = {name: sha(WORK / name) for name in ('protocol.json', 'historical-inputs.json',
        'enterprise_agent.py', 'enterprise_final_agent.py', 'development-task-map.json',
        'job-profile-version.json', 'preflight/receipt.json', 'historical-replay-preflight.json',
        'curator/timeout-override-mechanical.json', 'curator/dispatch_guard.py', 'curator/reservation.json',
        'curator/validation-task-map.private.json')}
    for name in ('jobs', 'baseline'):
        workspace.update({name + '/' + rel: digest for rel, digest in tree(WORK / name).items()})
    history_files = dict(prior['workspace_files'])
    history_files.update({name: sha(HISTORY / name) for name in ('execution-contract.json',
        'study/ledger.jsonl', 'interruption-001/closure.json', 'interruption-001/native-audit.json',
        'interruption-001/curator-continuation-review.md')})
    historical = read(WORK / 'historical-inputs.json')
    for family, rows in historical['families'].items():
        for row in rows:
            generation = row['generation']
            paths = [host(row['archive']), HISTORY / 'dispatch' / family / f'generation-{generation:03d}/analyze.json']
            if generation:
                paths.append(HISTORY / 'progress' / family / f'{generation:03d}.json')
            for path in paths:
                history_files[path.relative_to(HISTORY).as_posix()] = sha(path)
    value = {'schema_version': 'enterprise-continuation-execution-contract/1.0',
        'windows_python': posix(Path(sys.executable)), 'source_files': source_files,
        'workspace_files': workspace, 'historical_files': history_files,
        'external_read_only_files': prior['external_read_only_files'],
        'boundary': 'All eight family selections and exact joint replay precede one frozen all-500 comparison, then one private whole-bundle gate. Historical incomplete profiles have no fitness or retry.'}
    write(WORK / EXECUTION_CONTRACT, value)
    print('Execution contract prepared for independent review; not sealed.')


def seal(review):
    """Apply the independently reviewed seal and activate only development."""
    from prepare import load
    load('e8_seal_reservation', WORK / 'curator/dispatch_guard.py').verify('preparation')
    manifest = read(WORK / EXECUTION_CONTRACT)
    for base, key in ((REPO, 'source_files'), (WORK, 'workspace_files'), (HISTORY, 'historical_files')):
        for rel, expected in manifest[key].items():
            if sha(base / rel) != expected:
                raise ValueError('Unreviewed source change: ' + rel)
    organize('seal-design', '--protocol', WORK / EXECUTION_CONTRACT, '--baseline', WORK / 'baseline' / NAME, '--review', review)
    organize('verify')
    organize('transition', '--stage-id', 'evolve', '--status', 'running')
    print('E8 sealed and development active; private validation remains closed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['contract', 'seal'])
    parser.add_argument('--review', type=Path)
    args = parser.parse_args()
    if args.action == 'seal':
        if args.review is None:
            parser.error('--review is required')
        seal(args.review.resolve())
    else:
        contract()
