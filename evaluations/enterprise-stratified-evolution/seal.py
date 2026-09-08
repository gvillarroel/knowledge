"""Bind reviewed native execution controls, then seal and activate evolution."""
import argparse
import sys
from pathlib import Path

from prepare import HERE, REPO, WORK, OLD, NAME, OWNER, ORGANIZER, read, write, tree, sha, posix, organize


def contract():
    source_files = {p.relative_to(REPO).as_posix():sha(p) for p in sorted(HERE.glob('*.py'))}
    workspace_files = {name:sha(WORK/name) for name in (
        'protocol.json','enterprise_agent.py','development-task-map.json',
        'curator/validation-task-map.private.json','curator/dispatch_guard.py',
        'curator/reservation-v2.json','development-selection-v2/selected.private.json',
        'corpus/inventory.private.json','sampling-audit.json',
        'native-oracle/qualification.json','native-oracle/source-fidelity.json')}
    for name in ('jobs','baseline','runtime','tasks','agent-inputs'):
        workspace_files.update({name+'/'+relative:value for relative,value in tree(WORK/name).items()})
    realizer = Path('C:/Users/villa/.codex/skills/harbor-realize-skill-candidate/scripts/realize_skill_candidate.py')
    reporter = Path('C:/Users/villa/.codex/skills/harbor-run-results/scripts/report_harbor_jobs.py')
    external = {posix(path):sha(path) for path in (OWNER,ORGANIZER,realizer,reporter)}
    model = read(OLD/'model-inventory.json')
    model_root = OLD/'models/hub'/('models--'+model['model_id'].replace('/','--'))/'snapshots'/model['revision']
    if tree(model_root) != model['files']:
        raise ValueError('Pinned offline model drift')
    external.update({posix(model_root/relative):value for relative,value in model['files'].items()})
    value = {'schema_version':'enterprise-execution-contract/2.0',
             'windows_python':posix(Path(sys.executable)), 'source_files':source_files,
             'workspace_files':workspace_files,'external_read_only_files':external,
             'boundary':'The final all-500 comparison is retrospective, after the exact joint freeze and before private release; it cannot change selection. The private gate accepts or rejects the joint bundle once.'}
    write(WORK/'execution-contract.json',value)
    print('Execution contract ready for independent final review; not sealed.')


def seal(review):
    value = read(WORK/'execution-contract.json')
    for relative,expected in value['source_files'].items():
        if sha(REPO/relative) != expected:
            raise ValueError('Unreviewed controller change: '+relative)
    for relative,expected in value['workspace_files'].items():
        if sha(WORK/relative) != expected:
            raise ValueError('Unreviewed execution input change: '+relative)
    organize('seal-design','--protocol',WORK/'execution-contract.json',
             '--baseline',WORK/'baseline'/NAME,'--review',review)
    organize('verify')
    organize('transition','--stage-id','evolve','--status','running')
    print('Reviewed study sealed; evolution active; validation remains closed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['contract','seal'])
    parser.add_argument('--review',type=Path)
    args = parser.parse_args()
    if args.action == 'seal':
        if args.review is None:
            parser.error('--review is required for sealing')
        seal(args.review.resolve())
    else:
        contract()
