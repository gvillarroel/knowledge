"""Protect official scoring, exact model selection and unavailable-result gates."""
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import urllib.error

import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'evaluations/enterprise-rag-bench'
sys.path.insert(0,str(SCRIPTS))
import official_model_transport as transport
import run_full_classical_retrieval as retrieval
import run_official_classical_answers as official
import recover_classical_judge as recovery


def test_retrieval_metric_reference_denominators_and_duplicate_ids():
    assert retrieval.retrieval_metrics(['a'],[]) is None
    metrics=retrieval.retrieval_metrics(['a','a','x','b'],['a','b','b'])
    assert metrics=={'ndcg_at_10':pytest.approx((1+1/2)/(1+1/__import__('math').log2(3))),
                     'recall_at_10':1.0,'mrr_at_10':1.0,'complete_coverage_at_10':1.0}
    assert retrieval.retrieval_metrics([],['a'])==dict.fromkeys(metrics,0.0)


def test_aggregate_keeps_unanswerable_questions_outside_retrieval_means():
    rows=[{'metrics':None,'query_seconds':1},
          {'metrics':{'recall_at_10':0.5},'query_seconds':2}]
    result=retrieval.aggregate(rows)
    assert result['questions']==2 and result['questions_with_references']==1
    assert result['metrics']=={'recall_at_10':0.5}


def test_original_document_path_cannot_escape(tmp_path):
    for path in ['../outside.json','/absolute.json','C:/absolute.json','a\\b.json']:
        with pytest.raises(ValueError):
            official.document_file(tmp_path,path)
    assert official.document_file(tmp_path,'source/document.json')==tmp_path/'source/document.json'


def test_canonical_public_citations_preserve_first_hits_without_refilling_or_reordering():
    exporter=SimpleNamespace(get_export_filename=lambda identity,name:identity+'__'+name[:-5]+'.txt',
                             convert_to_text=lambda doc:doc['text'])
    originals={'a':{'path':'jira/canonical.json','document':{'text':'Exact canonical text'}},
               'b':{'path':'gmail/second.json','document':{'text':'Second text'}}}
    first={'upstream_id':'a','upstream_path':'jira/a__canonical.txt','raw_body':'Exact canonical text','raw_sha256':'first'}
    alias={**first,'upstream_path':'jira/a__alias.txt','raw_body':'Different duplicate body','raw_sha256':'alias'}
    second={'upstream_id':'b','upstream_path':'gmail/b__second.txt','raw_body':'Second text','raw_sha256':'second'}
    ids,dropped=official.canonical_citations([first,alias,second],originals,exporter)
    assert ids==['a','b']
    assert dropped==[{'upstream_id':'a','upstream_path':'jira/a__alias.txt','raw_sha256':'alias'}]
    with pytest.raises(ValueError,match='First retrieved identity'):
        official.canonical_citations([alias,first,second],originals,exporter)
    with pytest.raises(ValueError,match='exactly match'):
        official.canonical_citations([{**first,'raw_body':'Changed text'}],originals,exporter)


def response(text='READY',finish='stop',model='openai/gpt-5.4'):
    return {'model':model,'provider':'OpenAI','choices':[{'finish_reason':finish,'message':{'content':text}}],
            'usage':{'prompt_tokens':10,'completion_tokens':5,'prompt_tokens_details':{'cached_tokens':2},'cost':0.0001}}


def test_exact_openrouter_model_reasoning_usage_and_secret_redaction(tmp_path,monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-secret-never-publish')
    captured=[]
    def request(req,timeout):
        captured.append(json.loads(req.data))
        return io.BytesIO(json.dumps(response()).encode())
    monkeypatch.setattr(transport.urllib.request,'urlopen',request)
    client=transport.ModelTransport('openrouter',tmp_path/'calls')
    assert client.complete([{'role':'user','content':'Reply READY'}])=='READY'
    assert captured[0]['model']=='openai/gpt-5.4'
    assert captured[0]['reasoning']=={'effort':'medium'}
    assert captured[0]['provider']['allow_fallbacks'] is False
    assert client.summary()['input_tokens']==10
    assert client.summary()['cached_input_tokens']==2
    assert client.summary()['cost_usd']==0.0001
    assert 'test-secret-never-publish' not in (tmp_path/'calls/000000.json').read_text()


def test_openai_responses_shape_and_estimated_usage(tmp_path,monkeypatch):
    monkeypatch.setenv('LLM_API_KEY','test-openai-secret')
    captured=[]
    payload={'model':'gpt-5.4-2026-03-05','status':'completed',
             'usage':{'input_tokens':100,'output_tokens':20,'input_tokens_details':{'cached_tokens':40}},
             'output':[{'type':'reasoning','summary':[]},
                       {'type':'message','content':[{'type':'output_text','text':'READY'}]}]}
    def request(req,timeout):
        captured.append((req.full_url,json.loads(req.data)))
        return io.BytesIO(json.dumps(payload).encode())
    monkeypatch.setattr(transport.urllib.request,'urlopen',request)
    client=transport.ModelTransport('openai',tmp_path/'calls')
    assert client.complete([{'role':'user','content':'Reply READY'}])=='READY'
    endpoint,body=captured[0]
    assert endpoint=='https://api.openai.com/v1/responses'
    assert body['model']=='gpt-5.4' and body['store'] is False
    assert body['reasoning']=={'effort':'medium'} and body['max_output_tokens']==8192
    assert body['input']==[{'role':'user','content':'Reply READY'}]
    assert client.summary()['cost_usd']==pytest.approx(60*2.5e-6+40*0.25e-6+20*15e-6)
    assert client.summary()['cost_basis']=='published-token-rate-estimate'


def test_copilot_bridge_keeps_actual_model_usage_and_private_config_out_of_requests(tmp_path,monkeypatch):
    config=tmp_path/'config.json'
    config.write_text(json.dumps({'node_executable':'node'}),encoding='utf-8')
    monkeypatch.setenv('ENTERPRISE_COPILOT_CONFIG',str(config))
    captured=[]
    payload={'model':'gpt-5.4-2026-03-05','status':'completed',
             'usage':{'input_tokens':100,'output_tokens':20,'input_tokens_details':{'cached_tokens':40}},
             'output':[{'type':'message','content':[{'type':'output_text','text':'READY'}]}]}
    def run(argv,**kwargs):
        captured.append((argv,json.loads(kwargs['input'])))
        return SimpleNamespace(returncode=0,stdout=json.dumps(payload).encode(),stderr=b'')
    monkeypatch.setattr(transport.subprocess,'run',run)
    client=transport.ModelTransport('github-copilot',tmp_path/'calls')
    assert client.complete([{'role':'user','content':'Reply READY'}])=='READY'
    assert captured[0][0][2]==str(config)
    assert captured[0][1]['model']=='gpt-5.4'
    assert str(config) not in json.dumps(captured[0][1])
    assert client.summary()['input_tokens']==100 and client.summary()['cached_input_tokens']==40
    assert client.summary()['cost_usd']==pytest.approx(0.00046)
    assert 'not a Copilot invoice' in client.summary()['cost_basis']


def test_luna_codex_is_an_explicit_separate_model_treatment(tmp_path,monkeypatch):
    config=tmp_path/'config.json'
    config.write_text(json.dumps({'node_executable':'node'}),encoding='utf-8')
    monkeypatch.setenv('ENTERPRISE_CODEX_CONFIG',str(config))
    payload={'model':'gpt-5.6-luna','status':'completed',
             'usage':{'input_tokens':100,'output_tokens':20,'input_tokens_details':{'cached_tokens':40}},
             'output':[{'type':'message','content':[{'type':'output_text','text':'READY'}]}]}
    requests=[]
    def run(argv,**kwargs):
        requests.append(json.loads(kwargs['input']))
        return SimpleNamespace(returncode=0,stdout=json.dumps(payload).encode(),stderr=b'')
    monkeypatch.setattr(transport.subprocess,'run',run)
    client=transport.ModelTransport('openai-codex',tmp_path/'calls',model='gpt-5.6-luna')
    assert client.complete([{'role':'user','content':'Reply READY'}])=='READY'
    assert requests[0]['model']=='gpt-5.6-luna' and requests[0]['provider']=='openai-codex'
    assert client.summary()['model']=='gpt-5.6-luna'
    assert client.summary()['cost_usd']==pytest.approx((60*.2+40*.02+20*1.2)/1e6)
    assert 'not a Codex invoice' in client.summary()['cost_basis']
    assert client.token_rates(True)==(.4,.04,1.8)
    with pytest.raises(ValueError):
        client.get_llm(model='gpt-5.4')
    payload['model']='gpt-5.6-sol'
    with pytest.raises(transport.TransportUnavailable):
        client.complete([{'role':'user','content':'Reply READY'}])
    assert client.errors==1


def test_codex_host_output_limit_rejects_overlong_outputs_and_preserves_usage(tmp_path,monkeypatch):
    config=tmp_path/'config.json'
    config.write_text(json.dumps({'node_executable':'node'}),encoding='utf-8')
    monkeypatch.setenv('ENTERPRISE_CODEX_CONFIG',str(config))
    payload={'model':'gpt-5.6-luna','status':'completed',
             'usage':{'input_tokens':100,'output_tokens':8193},
             'output':[{'type':'message','content':[{'type':'output_text','text':'Overlong'}]}]}
    monkeypatch.setattr(transport.subprocess,'run',lambda *a,**k:SimpleNamespace(
        returncode=0,stdout=json.dumps(payload).encode(),stderr=b''))
    client=transport.ModelTransport('openai-codex',tmp_path/'calls',model='gpt-5.6-luna')
    with pytest.raises(transport.TransportUnavailable):
        client.complete([{'role':'user','content':'test'}])
    assert client.summary()['output_tokens']==8193
    assert client.summary()['transport_errors']==1


def test_complete_subscription_reply_survives_a_later_child_exit_error(tmp_path,monkeypatch):
    config=tmp_path/'config.json'
    config.write_text(json.dumps({'node_executable':'node'}),encoding='utf-8')
    monkeypatch.setenv('ENTERPRISE_CODEX_CONFIG',str(config))
    messages=[{'role':'user','content':'Exact prompt'}]
    payload={'model':'gpt-5.6-luna','status':'completed','reasoning':{'effort':'medium'},
        'usage':{'input_tokens':10,'output_tokens':5},
        'output':[{'type':'message','content':[{'type':'output_text','text':'yes'}]}],
        'bridge':{'provider':'openai-codex','http_status':200,'request_count':1,'provider_payload':{
            'model':'gpt-5.6-luna','store':False,'reasoning':{'effort':'medium'},
            'input':[{'role':'user','content':[{'type':'input_text','text':'Exact prompt'}]}]}}}
    monkeypatch.setattr(transport.subprocess,'run',lambda *a,**k:SimpleNamespace(
        returncode=3221226505,stdout=json.dumps(payload).encode(),stderr=b''))
    client=transport.ModelTransport('openai-codex',tmp_path/'calls',model='gpt-5.6-luna')
    assert client.complete(messages)=='yes'
    receipt=json.loads((tmp_path/'calls/000000.json').read_text(encoding='utf-8'))
    assert receipt['completed_reply_preserved_after_child_exit_error'] is True
    assert client.summary()['calls']==1 and client.errors==0
    payload['bridge']['provider_payload']['input'][0]['content'][0]['text']='Different prompt'
    assert transport.bound_subscription_completion(payload,'openai-codex','gpt-5.6-luna',messages) is False


def test_durable_reply_is_used_when_process_stdout_is_unreadable(tmp_path,monkeypatch):
    config=tmp_path/'config.json'
    config.write_text(json.dumps({'node_executable':'node'}),encoding='utf-8')
    monkeypatch.setenv('ENTERPRISE_CODEX_CONFIG',str(config))
    messages=[{'role':'user','content':'Exact prompt'}]
    payload={'model':'gpt-5.6-luna','status':'completed','reasoning':{'effort':'medium'},
        'usage':{'input_tokens':10,'output_tokens':5},
        'output':[{'type':'message','content':[{'type':'output_text','text':'yes'}]}],
        'bridge':{'provider':'openai-codex','http_status':200,'request_count':1,'provider_payload':{
            'model':'gpt-5.6-luna','store':False,'reasoning':{'effort':'medium'},
            'input':[{'role':'user','content':[{'type':'input_text','text':'Exact prompt'}]}]}}}
    def run(argv,**kwargs):
        Path(argv[3]).write_text(json.dumps(payload),encoding='utf-8')
        return SimpleNamespace(returncode=1,stdout=b'unreadable process output',stderr=b'local exit error')
    monkeypatch.setattr(transport.subprocess,'run',run)
    client=transport.ModelTransport('openai-codex',tmp_path/'calls',model='gpt-5.6-luna')
    assert client.complete(messages)=='yes'
    assert client.summary()['calls']==1 and client.errors==0
    receipt=json.loads((tmp_path/'calls/000000.json').read_text(encoding='utf-8'))
    assert receipt['durable_provider_reply']=='provider-responses/000000.json'
    assert (tmp_path/'calls/bridge-logs/000000.stdout').read_bytes()==b'unreadable process output'


def test_offline_replay_preserves_each_occurrence_and_never_invents_missing_calls():
    messages=[{'role':'user','content':'Repeated identical prompt'}]
    calls=[{'call':i,'request':{'messages':messages},'response':{
        'output':[{'type':'message','content':[{'type':'output_text','text':text}]}]}}
        for i,text in enumerate(['yes','no'])]
    replay=recovery.Replay(calls)
    token=recovery.QUESTION.set('synthetic-question')
    try:
        assert replay.complete(messages)=='yes'
        assert replay.complete(messages)=='no'
        with pytest.raises(recovery.MissingReplay):
            replay.complete(messages)
        assert replay.used=={0:'synthetic-question',1:'synthetic-question'}
    finally:
        recovery.QUESTION.reset(token)


def test_nested_fact_workers_keep_their_question_provenance():
    token=recovery.QUESTION.set('synthetic-question')
    try:
        with recovery.ContextExecutor(max_workers=2) as pool:
            assert pool.submit(recovery.QUESTION.get).result()=='synthetic-question'
    finally:
        recovery.QUESTION.reset(token)


def test_replay_history_detects_tampering_in_original_and_normalized_receipts(tmp_path):
    original=tmp_path/'judge/calls/000000.json'
    original.parent.mkdir(parents=True)
    row={'call':0,'status':'complete','response':{'text':'fixed original reply'}}
    original.write_text(json.dumps(row),encoding='utf-8')
    source=tmp_path/'history'
    (source/'calls').mkdir(parents=True)
    digest=recovery.sha(original)
    manifest={'source_receipt_sha256':{'judge/calls/000000.json':digest},
              'unevaluable_attempts':[],'available_responses':1}
    (source/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    normalized={**row,'original_call_number':0,'original_stage':'judge','original_sha256':digest}
    cached=source/'calls/000000.json'
    cached.write_text(json.dumps(normalized),encoding='utf-8')
    assert recovery.verify_response_history(tmp_path,source)==recovery.sha(source/'manifest.json')
    cached.write_text(json.dumps({**normalized,'status':'changed'}),encoding='utf-8')
    with pytest.raises(ValueError,match='Normalized response'):
        recovery.verify_response_history(tmp_path,source)
    original.write_text(json.dumps({**row,'status':'changed'}),encoding='utf-8')
    with pytest.raises(ValueError,match='Original response history'):
        recovery.verify_response_history(tmp_path,source)


def test_recorded_document_orders_distinguish_parser_retries_from_consensus_runs():
    template='{query}\nGOLD\n{gold_documents}\nCANDIDATES\n{candidate_documents}'
    identity_a,identity_b='dsid_'+('a'*32),'dsid_'+('b'*32)
    def prompt(order):
        return template.format(query='Synthetic query',gold_documents='',
            candidate_documents='\n'.join('Document ID: '+i for i in order))
    valid=json.dumps({i:{'classification':'invalid','reason':'Synthetic reason'} for i in [identity_a,identity_b]})
    calls=[{'request':{'messages':[{'role':'user','content':prompt(order)}]},
            'response':{'output':[{'type':'message','content':[{'type':'output_text','text':reply}]}]}}
           for order,reply in [([identity_a,identity_b],'invalid JSON'),
                               ([identity_a,identity_b],valid),([identity_b,identity_a],valid)]]
    orders=recovery.recorded_orders(calls,{'synthetic':{'question':'Synthetic query'}},template,lambda t:t)
    assert orders=={'synthetic':[[identity_a,identity_b],[identity_b,identity_a]]}


@pytest.mark.parametrize('payload',[response(finish='length'),response(text=''),response(model='openai/gpt-5.4-mini')])
def test_truncation_empty_and_model_substitution_stop_before_ranking(tmp_path,monkeypatch,payload):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-key')
    calls=[]
    def request(*args,**kwargs):
        calls.append(1)
        return io.BytesIO(json.dumps(payload).encode())
    monkeypatch.setattr(transport.urllib.request,'urlopen',request)
    client=transport.ModelTransport('openrouter',tmp_path/'calls')
    with pytest.raises(transport.TransportUnavailable):
        client.complete([{'role':'user','content':'test'}])
    with pytest.raises(transport.TransportUnavailable):
        client.complete([{'role':'user','content':'test'}])
    assert len(calls)==1 and client.errors==1


def test_no_credit_is_unavailable_and_not_a_semantic_zero(tmp_path,monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-key')
    def request(*args,**kwargs):
        raise urllib.error.HTTPError('https://openrouter.ai',402,'Payment required',{},None)
    monkeypatch.setattr(transport.urllib.request,'urlopen',request)
    client=transport.ModelTransport('openrouter',tmp_path/'calls')
    with pytest.raises(transport.TransportUnavailable):
        client.complete([{'role':'user','content':'test'}])
    receipt=json.loads((tmp_path/'calls/000000.json').read_text())
    assert receipt['status']=='unavailable' and receipt['http_status']==402
    assert 'score' not in receipt


def test_completed_empty_judge_reply_reaches_upstream_fallback_without_resampling(tmp_path,monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-key')
    calls=[]
    def request(*args,**kwargs):
        calls.append(1)
        return io.BytesIO(json.dumps(response(text='')).encode())
    monkeypatch.setattr(transport.urllib.request,'urlopen',request)
    client=transport.ModelTransport('openrouter',tmp_path/'judge',allow_empty=True)
    assert client.complete([{'role':'user','content':'Strip all citations from this reference list'}])==''
    assert len(calls)==1 and client.errors==0
    receipt=json.loads((tmp_path/'judge/000000.json').read_text())
    assert receipt['status']=='complete' and receipt['response']['choices'][0]['message']['content']==''


def test_budget_gate_and_factory_do_not_call_another_provider(tmp_path,monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY','test-key')
    client=transport.ModelTransport('openrouter',tmp_path/'calls',budget_usd=0.00001)
    with pytest.raises(transport.TransportUnavailable):
        client.complete([{'role':'user','content':'test'}])
    assert client.next_call==0
    with pytest.raises(ValueError):
        client.get_llm(model='gpt-5.4-mini')
    with pytest.raises(ValueError):
        client.get_llm(reasoning_level='low')


def official_result():
    """Use anticorrelated quality values to distinguish mean products from products of means."""
    rows=[{'question_id':f'question-{i}', 'corrected':False, 'answer_correct':i%2==0,
           'completeness_pct':20.0 if i%2==0 else 100.0,
           'document_recall_pct':75.0 if i<470 else None,
           'invalid_extra_docs':3 if i<470 else None} for i in range(500)]
    return {'questions':rows,'aggregate_stats':{
        'total_questions':500,'completed_questions':500,'skipped_rows':0,
        'num_corrected_questions':0,'average_correctness_pct':50.0,
        'average_completeness_pct':60.0,'combined_correctness_completeness_score':10.0,
        'average_recall_pct':75.0,'average_invalid_extra_docs':3.0}}


def test_official_completion_checks_mean_product_and_all_question_identities():
    result=official_result()
    identities={row['question_id'] for row in result['questions']}
    checked=official.validate_official_completion(result,identities)
    assert checked['status']=='complete'
    assert checked['aggregate_stats']['combined_correctness_completeness_score']==10.0
    result['aggregate_stats']['combined_correctness_completeness_score']=30.0
    with pytest.raises(transport.TransportUnavailable,match='aggregate'):
        official.validate_official_completion(result,identities)


@pytest.mark.parametrize('failure',['missing','duplicate','substituted','skipped','nan','unavailable','partial'])
def test_official_completion_rejects_unrankable_results(failure):
    result=official_result()
    identities={row['question_id'] for row in result['questions']}
    if failure=='missing':
        result['questions'].pop()
    elif failure=='duplicate':
        result['questions'][0]['question_id']='question-1'
    elif failure=='substituted':
        result['questions'][0]['question_id']='unplanned-question'
    elif failure=='skipped':
        result['aggregate_stats']['skipped_rows']=1
    elif failure=='nan':
        result['questions'][0]['completeness_pct']=float('nan')
    elif failure=='unavailable':
        result['questions'][0]['answer_correct']=None
    else:
        result['aggregate_stats']['completed_questions']=499
    with pytest.raises(transport.TransportUnavailable):
        official.validate_official_completion(result,identities)


def test_upstream_audit_distinguishes_valid_negative_verdicts_from_terminal_failures():
    evaluator=SimpleNamespace(
        evaluate_answer_correctness=lambda:(False,'Not supported'),
        evaluate_documents_with_consensus=lambda:(None,False,'Parsing exhausted'),
        update_gold_answer=lambda:'Updated answer',
        extract_answer_facts=lambda:None,
        extract_anti_hallucination_facts=lambda:[],
        strip_answer_citations=lambda:'Plain answer',
        validate_single_fact=lambda:False)
    original=evaluator.evaluate_answer_correctness
    with official.observe_evaluator(evaluator) as failures:
        assert evaluator.evaluate_answer_correctness()==(False,'Not supported')
        assert evaluator.validate_single_fact() is False
        assert evaluator.extract_anti_hallucination_facts()==[]
        assert failures==[]
        assert evaluator.evaluate_documents_with_consensus()==(None,False,'Parsing exhausted')
        assert evaluator.extract_answer_facts() is None
    assert failures==['evaluate_documents_with_consensus:unavailable','extract_answer_facts:unavailable']
    assert evaluator.evaluate_answer_correctness is original
