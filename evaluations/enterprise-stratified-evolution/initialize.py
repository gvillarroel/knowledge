"""Register every task and ordered stage before independent review and sealing."""
from prepare import (WORK, OLD, NAME, FAMILIES, read, write, posix, organize)


def job(name, rows, concurrency=1):
    return {'job_name':'e7-'+name, 'jobs_dir':posix(WORK/'native-jobs'),
            'n_attempts':1, 'n_concurrent_trials':concurrency, 'quiet':True,
            'retry':{'max_retries':0},
            'environment':{'type':'docker','delete':True,'mounts':[
                {'type':'bind','source':posix(OLD/'models/hub'),
                 'target':'/models/huggingface/hub','read_only':True,
                 'bind':{'create_host_path':False}}]},
            'agents':[{'name':'enterprise-stratified-retrieval',
                       'import_path':'enterprise_agent:SkillRetrievalAgent',
                       'model_name':'local/deterministic-retrieval-v3',
                       'skills':[posix(WORK/'baseline'/NAME)]}],
            'tasks':[{'path':row['task']} for row in rows]}


def initialize():
    public = read(WORK/'development-task-map.json')
    # Opaque dispatch metadata is used mechanically; no private task payloads
    # are read by this controller or incorporated into mutation evidence.
    private = read(WORK/'curator/validation-task-map.private.json')
    for family in FAMILIES:
        for phase, rows in (
            ('development',[public['development:'+family]]),
            ('validation',[row for row in private.values() if row['family']==family])):
            write(WORK/'jobs'/(family+'-'+phase+'.json'),job(family+'-'+phase,rows))
    for phase, rows in (
        ('development',[public['development:'+family] for family in FAMILIES]),
        ('recalculation',[public['recalculation:'+family] for family in FAMILIES]),
        ('validation',list(private.values()))):
        write(WORK/'jobs'/('joint-'+phase+'.json'),job('joint-'+phase,rows,2))
    protocol = read(WORK/'protocol.json')
    organize('init','--study-id','enterprise-e7','--title',
             'Stratified full-text Enterprise retrieval evolution',
             '--objective',protocol['selection'],
             '--comparison-profile','enterprise-stratified-native-v3-offline')
    for split in ('development','validation'):
        organize('add-dataset','--dataset-id',split,'--split',split,
                 '--source',WORK/'tasks'/split)
    for identifier, kind, owner, dataset, dependency in (
        ('evolve','evolution','harbor-reflective-pareto-search','development',None),
        ('recalculate','comparison','harbor-run-results','development','evolve'),
        ('validate','validation','harbor-reflective-pareto-search','validation','recalculate'),
        ('publish','publication','harbor-organize-evaluations',None,'validate')):
        args = ['--stage-id',identifier,'--kind',kind,'--owner-skill',owner]
        if dataset:
            args += ['--dataset-id',dataset]
        if dependency:
            args += ['--depends-on',dependency]
        organize('add-stage',*args)
    print('Registered 32 task roots and four planned stages; no execution or release.')


if __name__ == '__main__':
    initialize()
