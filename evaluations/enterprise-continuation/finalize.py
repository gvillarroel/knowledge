"""Joint native replay, exact freeze, retrospective comparison and one-way gate."""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
from pathlib import Path
import subprocess
import sys

from prepare import HERE, WORK, NAME, FAMILIES, OWNER, read, write, sha, posix, organize
from native import load, verify_frozen, realize, evaluate_new, archive_path


def host(value):
    return Path('C:/'+value[len('/mnt/c/'):]) if os.name=='nt' and value.startswith('/mnt/c/') else Path(value)


def require_host(windows):
    if (os.name=='nt') != windows:
        raise ValueError('This stage requires '+('the Windows organizer host' if windows else 'native Linux Harbor'))


def qualified(record):
    return (record['evaluable'] and record['qualification']['passed']
            and record['promotionEligibleProvenance'] and record['summary']['errorCount']==0)


def check_replay(record, expected):
    if not qualified(record):
        raise ValueError('Joint replay is not qualified and evaluable')
    observed = {row['taskName']:row['meanReward'] for row in record['cases']}
    if set(observed) != set(expected) or any(
        not math.isclose(observed[key],value,rel_tol=0,abs_tol=1e-12)
        for key,value in expected.items()):
        raise ValueError('Joint replay differs from the individually selected family scores')


def joint():
    require_host(False)
    verify_frozen()
    result = read(WORK/'family-sweep-complete.json')
    if len(result['families']) != 8 or {r['family'] for r in result['families']} != set(FAMILIES):
        raise ValueError('All eight family searches must finish before joint replay')
    taskmap = read(WORK/'development-task-map.json')
    expected = lambda key: {Path(taskmap['development:'+r['family']]['task']).name:r[key]
                            for r in result['families']}
    owner = load('e8_joint_pareto',OWNER)
    candidates = [{'id':'baseline','skill':str(WORK/'baseline'/NAME),'parents':[],
                   'rationale':'Unchanged all-family native control for the joint replay.'}]
    candidates, baseline, archive = evaluate_new(owner,'joint',0,candidates,'baseline')
    check_replay(baseline,expected('baseline_score'))
    changed = result['profile'] != read(WORK/'baseline'/NAME/'assets/retrieval-profile.json')
    generation, selected = 0, 'baseline'
    if changed:
        candidate = realize('joint','merged',WORK/'baseline'/NAME,result['profile'],
            {'id':'joint-development-merge','rationale':
             'Combine the exact eight completed development incumbents in their disjoint family profile keys. No new hypothesis, question, or private evidence is introduced.'},
            WORK/'family-sweep-complete.json')
        candidates.append({'id':'merged','skill':str(candidate),'parents':['baseline'],
                           'rationale':'Exact development-only family merge; native joint replay required.'})
        generation, selected = 1, 'merged'
        candidates, merged, archive = evaluate_new(owner,'joint',generation,candidates,selected)
        check_replay(merged,expected('score'))
        if archive['bestAggregateCandidate'] != selected:
            raise ValueError('Joint merge is not the native owner selection')
    write(WORK/'joint-result.json',{'status':'complete','changed':changed,
        'selected_candidate':selected,'generation':generation,
        'archive':str(archive_path('joint',generation)),
        'config':str(WORK/'dispatch/joint'/f'generation-{generation:03d}/analyze.json'),
        'families':result['families'],'validation_opened':False})
    print(json.dumps({'event':'joint-replay-complete','changed':changed}),flush=True)


def freeze():
    require_host(True)
    from study_guard import verify
    verify('development')
    result = read(WORK/'joint-result.json')
    config = read(host(result['config']))
    archive = read(host(result['archive']))
    selected = next(c for c in config['candidates'] if c['id']==result['selected_candidate'])
    member = next(c for c in archive['archive'] if c['candidateId']==selected['id'])
    if not member['qualified'] or not member['promotionEligibleProvenance']:
        raise ValueError('Unqualified joint selection')
    config['search'].update(selectedCandidate=selected['id'],developmentArchive=result['archive'])
    write(WORK/'gate.json',config)
    selection = {'candidate':selected['id'],'source':selected['skill'],
        'skill_digest':member['skillDigest'],'archive_sha256':sha(host(result['archive'])),
        'gate_config_sha256':sha(WORK/'gate.json'),'unchanged':not result['changed'],
        'families':8,'private_gate_opened':False,'reselection_permitted':False}
    write(WORK/'selection.json',selection)
    for family in FAMILIES:
        organize('record-evidence','--evidence-id','development-'+family,'--stage-id','evolve',
                 '--kind','evolution-report','--role','development','--path',WORK/'search'/family/'development')
    for identifier, kind, role, path in (
        ('joint-native-replay','evolution-report','development',WORK/'search/joint/development'),
        ('joint-selection','decision','decision',WORK/'selection.json'),
        ('frozen-joint-candidate','candidate','development',host(selected['skill'])),
        ('completed-family-sweep','decision','decision',WORK/'family-sweep-complete.json')):
        organize('record-evidence','--evidence-id',identifier,'--stage-id','evolve',
                 '--kind',kind,'--role',role,'--path',path)
    organize('transition','--stage-id','evolve','--status','completed')
    organize('transition','--stage-id','recalculate','--status','running')
    print('Joint selection frozen. All-500 retrospective comparison active; reselection forbidden.')


def bound_gate():
    selection = read(WORK/'selection.json')
    if sha(WORK/'gate.json') != selection['gate_config_sha256']:
        raise ValueError('Frozen gate configuration changed')
    config = read(WORK/'gate.json')
    if sha(host(config['search']['developmentArchive'])) != selection['archive_sha256']:
        raise ValueError('Frozen development archive changed')
    selected = next(c for c in config['candidates'] if c['id']==selection['candidate'])
    if selected['skill'] != selection['source']:
        raise ValueError('Frozen candidate path changed')
    return selection,config


def recalculate():
    require_host(False)
    verify_frozen('recalculation')
    selection, gate = bound_gate()
    owner = load('e8_retrospective_native',OWNER)
    owner.validate_development_archive_binding(owner.normalize_config(WORK/'gate.json'),
        read(host(gate['search']['developmentArchive'])))
    baseline = next(c for c in gate['candidates'] if c['id']=='baseline')
    candidate = next(c for c in gate['candidates'] if c['id']==selection['candidate'])
    config = copy.deepcopy(gate)
    config['search'] = {'id':'enterprise-e8-retrospective',
        'baselineSkill':baseline['skill'],'baselineCandidate':'baseline',
        'outputDir':str(WORK/'retrospective'),'generation':0}
    config['harbor']['developmentJob'] = str(WORK/'jobs/joint-recalculation.json')
    config['candidates'] = [dict(id='baseline',skill=baseline['skill'],parents=[],rationale='Frozen baseline'),
        dict(id='frozen',skill=candidate['skill'],parents=['baseline'],rationale='Joint frozen selection; comparison only')]
    write(WORK/'recalculation.json',config)
    records = owner.run_candidate_jobs(owner.normalize_config(WORK/'recalculation.json'),
        phase='development',analyze_only=False,candidate_ids=['baseline','frozen'])
    owner.validate_comparable(records)
    if any(not qualified(row) or len(row['cases'])!=8 for row in records):
        raise ValueError('All-500 native comparison incomplete or unqualified')
    if records[1]['skillDigest'] != selection['skill_digest']:
        raise ValueError('All-500 comparison changed the frozen skill')
    reporter = '/mnt/c/Users/villa/.codex/skills/harbor-run-results/scripts/report_harbor_jobs.py'
    with (WORK/'logs/recalculation-report.log').open('xb') as stream:
        subprocess.run([sys.executable,'-B',reporter,*[r['jobDirectory'] for r in records],
            '--compare','--pass-threshold','0.8','--output-dir',str(WORK/'native-reports/recalculation')],
            stdout=stream,stderr=subprocess.STDOUT,check=True)
    write(WORK/'recalculation-result.json',{'status':'complete','source':'native-harbor',
        'comparison_only':True,'reselection_permitted':False,'selection_sha256':sha(WORK/'selection.json'),
        'jobs':{row['candidateId']:row['jobDirectory'] for row in records},
        'records':records,'question_count_per_family':500,'retrieval_eligible':470,
        'documents':6000,'official_overall_evaluated':False})
    print(json.dumps({'event':'all-500-recalculation-complete','native_trials':16}),flush=True)


def release():
    require_host(True)
    from study_guard import verify
    verify('recalculation')
    selection,_ = bound_gate()
    result = read(WORK/'recalculation-result.json')
    if result['status']!='complete' or result['selection_sha256']!=sha(WORK/'selection.json'):
        raise ValueError('Frozen retrospective comparison is incomplete')
    for identifier,kind,path in (
        ('all-500-native-results','final-report',WORK/'native-reports/recalculation'),
        ('all-500-comparison-binding','decision',WORK/'recalculation-result.json')):
        organize('record-evidence','--evidence-id',identifier,'--stage-id','recalculate',
                 '--kind',kind,'--role','development' if kind=='final-report' else 'decision','--path',path)
    organize('transition','--stage-id','recalculate','--status','completed')
    if selection['unchanged']:
        write(WORK/'terminal-decision.json',{'decision':'baseline-retained','promoted':False,
            'reason':'No development profile improved; private portfolio remains unopened.',
            'private_gate_opened':False,'further_evolution_permitted':False})
        organize('transition','--stage-id','validate','--status','stopped',
                 '--note','Unchanged joint candidate; preserve unopened private portfolio')
        organize('transition','--stage-id','publish','--status','stopped',
                 '--note','Reviewed development and retrospective results may be reported without promotion')
        return
    organize('release-validation','--selection-id','joint-finalist','--selected-stage','evolve',
             '--candidate-evidence',host(selection['source']))
    organize('transition','--stage-id','validate','--status','running')
    print('Single reserved validation release recorded for the exact joint candidate.')


def gate():
    require_host(False)
    if read(WORK/'selection.json')['unchanged']:
        return
    verify_frozen('validation')
    selection,_ = bound_gate()
    owner = load('e8_terminal_native_pareto',OWNER)
    result = owner.holdout(owner.normalize_config(WORK/'gate.json'),analyze_only=False)
    write(WORK/'gate-execution.json',result)
    print(json.dumps({'event':'native-private-gate-complete','families':8}),flush=True)


def family_gate(native, metadata):
    """Tighten the native aggregate gate using the preregistered family means."""
    mapping = {Path(row['task']).name:row for row in metadata.values()}
    cases = native['perCase']
    if len(cases)!=16 or {r['taskName'] for r in cases}!=set(mapping):
        raise ValueError('Private native gate task coverage differs from the reservation')
    rows = []
    for family in FAMILIES:
        selected = [r for r in cases if mapping[r['taskName']]['family']==family]
        if len(selected)!=2 or len({mapping[r['taskName']]['source_group'] for r in selected})!=2:
            raise ValueError('Private family is missing a source group')
        evaluable = all(r['evaluable'] and type(r['delta']) in (int,float)
                        and math.isfinite(r['delta']) for r in selected)
        gain = sum(r['delta'] for r in selected)/2 if evaluable else None
        rows.append({'family':family,'source_groups':2,'evaluable':evaluable,
                     'mean_gain':gain,'accepted':evaluable and gain>=0})
    accepted = (native['promoted'] and native['baselineQualified'] and native['candidateQualified']
                and all(row['accepted'] for row in rows))
    return accepted,rows


def close():
    require_host(True)
    if read(WORK/'selection.json')['unchanged']:
        return
    from study_guard import verify
    verify('validation')
    selection,_ = bound_gate()
    source = WORK/'search/joint/holdout/promotion.json'
    promotion = read(source)
    if promotion['selectedSkillDigest']!=selection['skill_digest']:
        raise ValueError('Private gate changed the joint candidate')
    accepted,rows = family_gate(promotion['holdout'],read(WORK/'curator/validation-task-map.private.json'))
    write(WORK/'terminal-decision.json',{'schema_version':'enterprise-joint-terminal/1.0',
        'source':'native-harbor-rewards','decision':'accepted-for-declared-scope' if accepted else 'keep-baseline',
        'promoted':accepted,'selected_skill_digest':selection['skill_digest'],
        'private_gate_opened':True,'further_evolution_permitted':False,
        'families':rows,'native_promotion_sha256':sha(source),
        'native_aggregate_gate_passed':promotion['holdout']['promoted'],
        'canonical_skill_installed':False})
    for identifier,kind,role,path in (
        ('terminal-native-gate','evolution-report','validation',source.parent),
        ('joint-terminal-decision','decision','decision',WORK/'terminal-decision.json')):
        organize('record-evidence','--evidence-id',identifier,'--stage-id','validate',
                 '--kind',kind,'--role',role,'--path',path)
    organize('transition','--stage-id','validate','--status','completed')
    organize('transition','--stage-id','publish','--status','running')
    print(json.dumps({'event':'terminal-decision','accepted':accepted,'further_evolution_permitted':False}),flush=True)


if __name__ == '__main__':
    commands = {'joint':joint,'freeze':freeze,'recalculate':recalculate,
                'release':release,'gate':gate,'close':close}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=list(commands))
    commands[parser.parse_args().phase]()
