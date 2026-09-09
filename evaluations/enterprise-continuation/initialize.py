"""Version native jobs and register the complete E8 portfolio before sealing."""
from __future__ import annotations

import argparse
import importlib.util

from prepare import WORK, HISTORY, NAME, FAMILIES, read, write, posix, organize, sha


def prepare_jobs():
    """Keep historical task paths and declare only a paired final timeout override."""
    if sha(WORK / 'enterprise_agent.py') != sha(HISTORY / 'enterprise_agent.py'):
        raise ValueError('Inherited development adapter changed')
    for source in sorted((HISTORY / 'jobs').glob('*.json')):
        value = read(source)
        value['job_name'] = value['job_name'].replace('e7-', 'e8-', 1)
        value['jobs_dir'] = posix(WORK / 'native-jobs')
        for agent in value['agents']:
            agent['skills'] = [posix(WORK / 'baseline' / NAME)]
        if source.name == 'joint-recalculation.json':
            for agent in value['agents']:
                agent.update(name='enterprise-stratified-final', import_path='enterprise_final_agent:SkillRetrievalAgent',
                             override_timeout_sec=10800.0)
        write(WORK / 'jobs' / source.name, value)
    original = (HISTORY / 'enterprise_agent.py').read_text(encoding='utf-8')
    if original.count('timeout_sec=3600') != 1:
        raise ValueError('Unexpected inherited runtime timeout')
    final = original.replace('return "enterprise-stratified-retrieval"', 'return "enterprise-stratified-final"')
    final = final.replace('return "3.0.0"', 'return "3.1.0"').replace('timeout_sec=3600', 'timeout_sec=10800')
    with (WORK / 'enterprise_final_agent.py').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(final)
    write(WORK / 'job-profile-version.json', {'schema_version': 'enterprise-e8-job-profile/1.0',
        'task_bytes_changed': False, 'task_roots_reused_at_exact_original_paths': True,
        'development_joint_validation_adapter_sha256': sha(WORK / 'enterprise_agent.py'),
        'retrospective_adapter_sha256': sha(WORK / 'enterprise_final_agent.py'),
        'retrospective_agent_override_timeout_sec': 10800,
        'retrospective_adapter_exec_timeout_sec': 10800,
        'original_agent_timeout_sec': 3600, 'builder_subprocess_timeout_sec': 2400,
        'policy': 'Only final all-500 jobs use the longer native override, identically for both arms. Native task defaults remain inherited and immutable.'})
    print('Prepared 19 native job profiles; no study initialization or execution.')


def initialize():
    """Register unchanged task roots and prospective downstream stages."""
    spec = importlib.util.spec_from_file_location('e8_initial_reservation', WORK / 'curator/dispatch_guard.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.verify('preparation')
    protocol = read(WORK / 'protocol.json')
    organize('init', '--study-id', 'enterprise-e8', '--title',
        'Continuation of stratified Enterprise retrieval evolution', '--objective', protocol['selection'],
        '--comparison-profile', 'enterprise-stratified-native-v3-historical-continuation-final-v4')
    for split in ('development', 'validation'):
        organize('add-dataset', '--dataset-id', split, '--split', split, '--source', HISTORY / 'tasks' / split)
    for identifier, kind, owner, dataset, dependency in (
        ('evolve', 'evolution', 'harbor-reflective-pareto-search', 'development', None),
        ('recalculate', 'comparison', 'harbor-run-results', 'development', 'evolve'),
        ('validate', 'validation', 'harbor-reflective-pareto-search', 'validation', 'recalculate'),
        ('publish', 'publication', 'harbor-organize-evaluations', None, 'validate')):
        args = ['--stage-id', identifier, '--kind', kind, '--owner-skill', owner]
        if dataset:
            args += ['--dataset-id', dataset]
        if dependency:
            args += ['--depends-on', dependency]
        organize('add-stage', *args)
    print('Registered unchanged 32 task roots and four prospective stages; no execution or release.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['jobs', 'register'])
    args = parser.parse_args()
    prepare_jobs() if args.action == 'jobs' else initialize()
