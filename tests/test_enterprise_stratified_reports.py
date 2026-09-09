"""Native aggregate reporting must retain missingness, units and paired scope."""
import importlib.util
import copy
import ast
import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1]/'evaluations/publish_enterprise_stratified.py'
SPEC = importlib.util.spec_from_file_location('enterprise_e7_reports',SOURCE)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def metrics(value):
    return {key:value for key in REPORT.METRICS}


def test_report_routes_match_the_native_execution_inventory():
    source=SOURCE.parent/'enterprise-stratified-evolution/prepare.py'
    declarations={node.targets[0].id:ast.literal_eval(node.value)
                  for node in ast.parse(source.read_text(encoding='utf-8')).body
                  if isinstance(node,ast.Assign) and len(node.targets)==1
                  and isinstance(node.targets[0],ast.Name) and node.targets[0].id in {'MODES','PRIMARY'}}
    assert REPORT.PRIMARY==declarations['PRIMARY']
    assert {family:set(modes) for family,modes in REPORT.ROUTES.items()}=={
        family:set(modes) for family,modes in declarations['MODES'].items()}


def test_no_reference_cases_do_not_become_zero_scores():
    result = REPORT.aggregate_group([metrics(.8),None,metrics(.4)],[0,1,2])
    assert result['questions']==3 and result['retrieval_eligible']==2
    assert result['ndcg_at_10']==pytest.approx(.6)
    missing = REPORT.aggregate_group([None],[0])
    assert missing['retrieval_eligible']==0
    assert all(missing[key] is None for key in REPORT.METRICS)


def test_native_execution_penalty_is_not_published_as_measured_zero_ndcg():
    outcome={'candidate':'candidate-001','strategy':'semantic-segmentation','score':0,
             'qualified':False,'improved':False,'consecutive_failures':1}
    native={'qualification':{'passed':False},'evaluable':True,
            'summary':{'errorCount':1,'observedMeanReward':None}}
    result=REPORT.summarize_attempt(outcome,native)
    assert result['score'] is None and result['scheduler_reward']==0
    assert result['status']=='native-execution-error' and result['execution_errors']==1
    assert result['consecutive_failures']==1 and not result['qualified']


def test_valid_zero_score_remains_a_measured_zero():
    outcome={'candidate':'candidate-002','strategy':'fixture','score':0}
    native={'qualification':{'passed':True},'evaluable':True,
            'summary':{'errorCount':0,'observedMeanReward':0}}
    result=REPORT.summarize_attempt(outcome,native)
    assert result['score']==0 and result['status']=='qualified'
    native['summary']['errorCount']=1
    with pytest.raises(ValueError,match='error-free'):
        REPORT.summarize_attempt(outcome,native)


def test_failed_integrity_score_is_excluded_from_quality_comparison():
    outcome={'candidate':'candidate-003','strategy':'fixture','score':.8}
    native={'qualification':{'passed':False},'evaluable':True,
            'summary':{'errorCount':0,'observedMeanReward':.8}}
    result=REPORT.summarize_attempt(outcome,native)
    assert result['score'] is None and result['scheduler_reward']==.8
    assert result['status']=='qualification-failed'


@pytest.mark.parametrize('bad',[True,float('nan'),float('inf'),-0.1,1.1,'0.5'])
def test_malformed_native_case_metrics_are_not_coerced(bad):
    with pytest.raises(ValueError,match='aggregate'):
        REPORT.aggregate_group([metrics(bad)],[0])


def test_group_comparison_requires_both_fixed_arms():
    row = {'family':'classical','arm':'baseline','primary':True,'ndcg_at_10':.5}
    with pytest.raises(ValueError,match='paired'):
        REPORT.paired([row])
    pairs = REPORT.paired([row,{**row,'arm':'frozen','ndcg_at_10':.4}])
    assert pairs[('classical',)]['frozen']['ndcg_at_10']==.4


def test_catalog_converts_ratios_to_percent_but_preserves_latency_units():
    value = {'execution_contract_sha256':'a'*64,'routes':[
        dict(family='classical',arm='baseline',route='fusion',primary=True,
             query_p95_ms=234.5,**metrics(.6)),
        dict(family='classical',arm='frozen',route='fusion',primary=True,
             query_p95_ms=100.2,**metrics(.7)),
        dict(family='classical',arm='frozen',route='bm25',primary=False,
             query_p95_ms=12,**metrics(.9))]}
    result = REPORT.comparison(value)
    assert len(result['alternatives'])==2
    assert [r['id'] for r in result['alternatives']]==['classical-frozen','classical-baseline']
    baseline=next(r for r in result['alternatives'] if r['id']=='classical-baseline')
    assert baseline['metrics']['ndcg_at_10']==60
    assert baseline['metrics']['representative_p95_ms']==234.5
    assert result['dataset_scope']['cohort']=='retrospective-all-500'


def test_publisher_refuses_incomplete_recalculation_before_loading_raw_inputs(tmp_path,monkeypatch):
    monkeypatch.setattr(REPORT,'WORK',tmp_path)
    for name,value in (('recalculation-result',{'status':'running'}),
                       ('selection',{}),('terminal-decision',{})):
        (tmp_path/(name+'.json')).write_text(REPORT.json.dumps(value))
    with pytest.raises(ValueError,match='completed selection'):
        REPORT.collect()


def test_duplicate_pair_rows_cannot_silently_replace_an_observation():
    row={'family':'classical','arm':'baseline','primary':True}
    with pytest.raises(ValueError,match='Duplicate'):
        REPORT.paired([row,row])


def group_rows(scores,eligible=3):
    return [dict(group='fixture',dimension='application',family=family,arm=arm,
                 questions=4,retrieval_eligible=eligible,ndcg_at_10=score if arm=='frozen' else 1)
            for family,score in scores.items() for arm in ('baseline','frozen')]


def test_group_leaders_preserve_exact_ties_and_do_not_select_using_baseline():
    rows=group_rows({'classical':.8,'legacy':.8,'embeddings':.7})
    original=copy.deepcopy(rows)
    assert REPORT.group_leaders(rows,'application')==[
        {'group':'fixture','families':['classical','legacy'],'score':.8,'questions':4,'retrieval_eligible':3}]
    assert rows==original


def test_group_with_no_references_has_no_winner():
    row=REPORT.group_leaders(group_rows({'classical':None,'legacy':None},eligible=0),'application')[0]
    assert row['families']==[] and row['score'] is None and row['retrieval_eligible']==0


def test_groups_with_different_family_denominators_are_not_ranked():
    rows=group_rows({'classical':.8,'legacy':.7})
    rows[-1]['retrieval_eligible']=2
    with pytest.raises(ValueError,match='denominators'):
        REPORT.group_leaders(rows,'application')


def scheduler_fixture():
    folder=SOURCE.parent/'enterprise-stratified-evolution'
    modules={}
    for name in ('sweep','profiles'):
        spec=importlib.util.spec_from_file_location('report_fixture_'+name,folder/(name+'.py'))
        modules[name]=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modules[name])
    baseline=modules['profiles'].baseline_profile()
    strategies=[{'id':'saturation','variants':[{'engine':'bm25','k1':1.2},{'engine':'bm25','k1':.6}]}]
    state=modules['sweep'].Sweep(strategies,'baseline',.5,baseline)
    outcomes=[{'candidate':'baseline','score':.5}]
    while proposed:=state.next():
        mechanism,variant=proposed
        profile=modules['profiles'].mutate(state.profile,'legacy',variant)
        if not state.claim(profile):
            continue
        candidate='candidate-'+str(len(outcomes))
        score=.6 if variant['k1']==1.2 else .55
        improved=state.observe(candidate,profile,score)
        outcomes.append(dict(candidate=candidate,strategy=mechanism['id'],variant=variant,
            score=score,qualified=True,improved=improved,best_candidate=state.best_id,
            best_score=state.best_score,consecutive_failures=state.failures))
    result=dict(family='legacy',baseline_score=.5,outcomes=outcomes,generation=len(outcomes)-1,
        events=state.events,profile=state.profile,winner={'id':state.best_id},status=state.stop_reason,rounds=state.round)
    return result,strategies,baseline,modules


def test_history_replay_rejects_forged_decisions_and_missing_attempts():
    result,strategies,baseline,modules=scheduler_fixture()
    args=(strategies,baseline,modules['profiles'],modules['sweep'],5)
    REPORT.replay_history(result,*args)
    forged=copy.deepcopy(result)
    forged['outcomes'][1]['improved']=False
    with pytest.raises(ValueError,match='decision'):
        REPORT.replay_history(forged,*args)
    missing=copy.deepcopy(result)
    missing['outcomes'].pop()
    with pytest.raises(ValueError,match='scheduled'):
        REPORT.replay_history(missing,*args)
    false_stop=copy.deepcopy(result)
    false_stop['status']='outer-round-budget-exhausted'
    with pytest.raises(ValueError,match='Terminal'):
        REPORT.replay_history(false_stop,*args)


def test_changed_public_metadata_cannot_relabel_completed_case_scores(tmp_path,monkeypatch):
    monkeypatch.setattr(REPORT,'REPO',tmp_path)
    monkeypatch.setattr(REPORT,'WORK',tmp_path/'work')
    REPORT.WORK.mkdir()
    (REPORT.WORK/'selection.json').write_text('{}',encoding='utf-8')
    (REPORT.WORK/'terminal-decision.json').write_text('{}',encoding='utf-8')
    protocol={'development':{'questions_sha256':'0'*64,'selection_sha256':'0'*64}}
    (REPORT.WORK/'protocol.json').write_text(REPORT.json.dumps(protocol),encoding='utf-8')
    contract={'workspace_files':{'protocol.json':REPORT.sha(REPORT.WORK/'protocol.json')}}
    (REPORT.WORK/'execution-contract.json').write_text(REPORT.json.dumps(contract),encoding='utf-8')
    receipt={'status':'complete','selection_sha256':REPORT.sha(REPORT.WORK/'selection.json'),
             'jobs':{'baseline':'unused','frozen':'unused'}}
    (REPORT.WORK/'recalculation-result.json').write_text(REPORT.json.dumps(receipt),encoding='utf-8')
    questions=tmp_path/'evaluations/enterprise-rag-bench/raw/questions.jsonl'
    questions.parent.mkdir(parents=True)
    questions.write_text('{"question_type":"changed-category"}\n',encoding='utf-8')
    with pytest.raises(ValueError,match='question metadata'):
        REPORT.collect()


def final_report_fixture(tmp_path,monkeypatch):
    """Fixture-only collection contract: this does not execute or score Harbor."""
    monkeypatch.setattr(REPORT,'REPO',tmp_path)
    monkeypatch.setattr(REPORT,'WORK',tmp_path/'work')

    def write(path,value):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(REPORT.json.dumps(value),encoding='utf-8')

    questions=[{'question_id':f'q{i:04d}','question_type':'eligible' if i<470 else 'unreferenced',
                'source_types':['fixture'],'expected_doc_ids':['reference'] if i<470 else []}
               for i in range(500)]
    questions_path=tmp_path/'evaluations/enterprise-rag-bench/raw/questions.jsonl'
    questions_path.parent.mkdir(parents=True)
    questions_path.write_text('\n'.join(REPORT.json.dumps(q) for q in questions)+'\n',encoding='utf-8')
    selected=REPORT.WORK/'development-selection-v2/selected.private.json'
    write(selected,questions[:112]+questions[470:478])
    write(REPORT.WORK/'selection.json',{'skill_digest':'sha256:'+'a'*64})
    write(REPORT.WORK/'terminal-decision.json',{'decision':'baseline-retained','private_gate_opened':False})
    write(REPORT.WORK/'protocol.json',{'development':{'questions_sha256':REPORT.sha(questions_path),
                                                    'selection_sha256':REPORT.sha(selected)}})
    write(REPORT.WORK/'execution-contract.json',{'workspace_files':{
        'protocol.json':REPORT.sha(REPORT.WORK/'protocol.json')}})
    write(REPORT.WORK/'development-task-map.json',{f:{'task':'/fixture/'+f,'family':f,'phase':'recalculation'}
                                                  for f in REPORT.PRIMARY})
    dates={'started_at':'2026-01-01T00:00:00','finished_at':'2026-01-01T00:00:02'}
    job_state={**dates,'n_total_trials':8,'stats':{'n_completed_trials':8,'n_running_trials':0,
                                               'n_pending_trials':0,'n_errored_trials':0,'n_cancelled_trials':0}}
    jobs={arm:REPORT.WORK/'native'/arm for arm in ('baseline','frozen')}
    for arm,job in jobs.items():
        write(job/'result.json',job_state)
        write(job/'lock.json',{'fixture_only':True})
        for family,modes in REPORT.ROUTES.items():
            write(job/family/'result.json',{**dates,'task_name':family,'exception_info':None,
                'agent_execution':dates,'verifier_result':{'rewards':{'reward':.8,'evidence_integrity':1}}})
            write(job/family/'verifier/diagnostics.json',{'status':'pass','question_count':500,
                'routes':{mode:{**metrics(.8),'p95_ms':12} for mode in modes},
                'cases':{mode:[metrics(.8)]*470+[None]*30 for mode in modes},
                'build_seconds':1.5,'knowledge_bytes':4096})
    write(REPORT.WORK/'recalculation-result.json',{'status':'complete',
        'selection_sha256':REPORT.sha(REPORT.WORK/'selection.json'),
        'jobs':{arm:str(path) for arm,path in jobs.items()}})
    for family in REPORT.PRIMARY:
        write(REPORT.WORK/'family-results'/(family+'.json'),{'family':family,'treatment':'fixture-only',
            'status':'full-round-without-improvement','generation':0,'rounds':1,
            'baseline_score':.8,'score':.8,'profile':{family:{'plan':{},'search':{}}},'events':[]})
    # The real stopping audit has separate tests and an actual native Legacy
    # replay; isolate this test to final collection, scope and report rendering.
    monkeypatch.setattr(REPORT,'audit_development',lambda *args,**kwargs:[{'candidate':'baseline','strategy':'baseline',
        'score':.8,'qualified':True,'status':'qualified','execution_errors':0,'native_job_seconds':2}])
    return jobs


def test_full_collection_covers_sixteen_trials_and_all_fixed_routes(tmp_path,monkeypatch):
    final_report_fixture(tmp_path,monkeypatch)
    result=REPORT.collect()
    assert len(result['bindings'])==16 and len(result['routes'])==36
    primary=[r for r in result['routes'] if r['primary']]
    assert len(primary)==16 and {r['family'] for r in primary}==set(REPORT.PRIMARY)
    assert all(r['questions']==500 and r['retrieval_eligible']==470 for r in result['routes'])
    assert all(r['ndcg_at_10']==pytest.approx(.8) for r in result['routes'])
    files=REPORT.render(result)
    assert all('skills/'+family+'.md' in files for family in REPORT.PRIMARY)
    assert 'unreferenced' in files['categories.md'] and 'N/A' in files['categories.md']
    contract=REPORT.comparison(result)
    assert len(contract['alternatives'])==16
    spec=importlib.util.spec_from_file_location('fixture_final_comparison_validator',
        SOURCE.with_name('validate_comparison_contract.py'))
    validator=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    table=validator.validate_report_against_contract(files['README.md'],contract)
    assert len(table.rows)==16
    assert '## Paired family deltas' in files['README.md']


def test_invalid_primary_contract_is_rejected_before_creating_publication(tmp_path,monkeypatch):
    final_report_fixture(tmp_path,monkeypatch)
    contract=REPORT.comparison(REPORT.collect())
    contract['alternatives'][0]['metrics'].pop('representative_p95_ms')
    monkeypatch.setattr(REPORT,'comparison',lambda value:contract)
    output=tmp_path/'unpublished'
    monkeypatch.setattr(sys,'argv',['publish_enterprise_stratified.py','--output',str(output)])
    with pytest.raises(ValueError,match='must provide exactly'):
        REPORT.main()
    assert not output.exists()


def test_same_route_count_cannot_hide_a_missing_primary(tmp_path,monkeypatch):
    jobs=final_report_fixture(tmp_path,monkeypatch)
    path=jobs['frozen']/'classical/verifier/diagnostics.json'
    value=REPORT.read(path)
    for key in ('routes','cases'):
        value[key]['invented']=value[key].pop('fusion')
    path.write_text(REPORT.json.dumps(value),encoding='utf-8')
    with pytest.raises(ValueError,match='declared family contract'):
        REPORT.collect()


def test_complete_receipt_does_not_hide_an_unfinished_native_arm(tmp_path,monkeypatch):
    jobs=final_report_fixture(tmp_path,monkeypatch)
    path=jobs['frozen']/'result.json'
    value=REPORT.read(path)
    value['finished_at']=None
    value['stats']['n_running_trials']=1
    path.write_text(REPORT.json.dumps(value),encoding='utf-8')
    with pytest.raises(ValueError,match='arm is incomplete'):
        REPORT.collect()


def test_final_collection_refuses_a_missing_comparison_arm(tmp_path,monkeypatch):
    final_report_fixture(tmp_path,monkeypatch)
    path=REPORT.WORK/'recalculation-result.json'
    value=REPORT.read(path)
    value['jobs'].pop('baseline')
    path.write_text(REPORT.json.dumps(value),encoding='utf-8')
    with pytest.raises(ValueError,match='exactly the baseline and frozen arms'):
        REPORT.collect()


def test_accepted_native_gate_does_not_claim_repository_installation(tmp_path,monkeypatch):
    final_report_fixture(tmp_path,monkeypatch)
    path=REPORT.WORK/'terminal-decision.json'
    value={'decision':'accepted-for-declared-scope','promoted':True,
           'private_gate_opened':True,'canonical_skill_installed':False}
    path.write_text(REPORT.json.dumps(value),encoding='utf-8')
    result=REPORT.collect()
    assert result['terminal_decision']['promoted'] is True
    assert result['terminal_decision']['canonical_skill_installed'] is False
    assert result['repository_installation']['installed_by_native_gate'] is False
    text=REPORT.render(result)['README.md']
    assert 'accepted-for-declared-scope' in text
    assert 'Gate acceptance alone does not establish that the canonical skills have changed' in text


def test_native_terminal_receipt_cannot_certify_a_later_installation(tmp_path,monkeypatch):
    final_report_fixture(tmp_path,monkeypatch)
    path=REPORT.WORK/'terminal-decision.json'
    value=REPORT.read(path)
    value['canonical_skill_installed']=True
    path.write_text(REPORT.json.dumps(value),encoding='utf-8')
    with pytest.raises(ValueError,match='does not certify repository installation'):
        REPORT.collect()


def test_continuation_report_preserves_scope_and_distinguishes_historical_runtime(tmp_path,monkeypatch):
    final_report_fixture(tmp_path,monkeypatch)
    result=REPORT.collect()
    result['campaign']='E8'
    for row in result['development']:
        row.update(historical_variants=0,new_variants=0,unavailable_hypotheses=0)
    contract=REPORT.comparison(result)
    assert contract['dataset_scope']['dataset_id']=='enterprise-rag-e8-fulltext-500'
    assert len(contract['alternatives'])==16
    files=REPORT.render(result)
    assert files['README.md'].startswith('# EnterpriseRAG E8:')
    assert 'docs/enterprise-continuation.md' in files['README.md']
    assert '10,800-second' in files['cta.md'] and '66 completed historical jobs once' in files['cta.md']
    assert 'partial runtime is excluded' in files['cta.md']
    assert '../../../e7/legacy-generated-expert-001/' in files['skills/legacy.md']
    assert '../../../e7/turso-generated-expert-001/' in files['skills/turso.md']
    assert 'Completed variants' in files['development.md']
