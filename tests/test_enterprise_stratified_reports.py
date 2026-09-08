"""Native aggregate reporting must retain missingness, units and paired scope."""
import importlib.util
import copy
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1]/'evaluations/publish_enterprise_stratified.py'
SPEC = importlib.util.spec_from_file_location('enterprise_e7_reports',SOURCE)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def metrics(value):
    return {key:value for key in REPORT.METRICS}


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
    assert result['alternatives'][0]['metrics']['ndcg_at_10']==60
    assert result['alternatives'][0]['metrics']['representative_p95_ms']==234.5
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
    receipt={'status':'complete','selection_sha256':REPORT.sha(REPORT.WORK/'selection.json')}
    (REPORT.WORK/'recalculation-result.json').write_text(REPORT.json.dumps(receipt),encoding='utf-8')
    questions=tmp_path/'evaluations/enterprise-rag-bench/raw/questions.jsonl'
    questions.parent.mkdir(parents=True)
    questions.write_text('{"question_type":"changed-category"}\n',encoding='utf-8')
    with pytest.raises(ValueError,match='question metadata'):
        REPORT.collect()
