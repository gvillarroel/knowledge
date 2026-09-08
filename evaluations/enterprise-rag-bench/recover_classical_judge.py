"""Recover a fixed judge from exact completed response receipts, without resampling."""
from __future__ import annotations

import argparse
from collections import defaultdict,deque
from concurrent.futures import ThreadPoolExecutor,as_completed
from contextvars import ContextVar,copy_context
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import re
import sys
import threading

from full_corpus_classical import sha,write_json
from official_model_transport import ModelTransport,TransportUnavailable,bound_subscription_completion
from run_official_classical_answers import setup,tree,validate_official_completion

QUESTION=ContextVar('recovery_question')


class MissingReplay(BaseException):
    """Stop an offline question before any unavailable component becomes a zero."""


class ContextExecutor(ThreadPoolExecutor):
    """Propagate question identity into the upstream per-fact worker threads."""
    def submit(self,fn,*args,**kwargs):
        context=copy_context()
        return super().submit(context.run,fn,*args,**kwargs)


def request_key(messages):
    """Bind literal prompt bytes, retaining every repeated-call occurrence."""
    return hashlib.sha256(json.dumps(messages,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def response_text(result):
    """Extract only completed message text from an audited provider response."""
    return ''.join(p.get('text','') for item in result.get('output',[]) if item.get('type')=='message'
                   for p in item.get('content',[]) if p.get('type')=='output_text').strip()


class Replay:
    """Consume exact recorded responses before allowing any new request."""
    def __init__(self,calls,live=None):
        self.calls=calls
        self.live=live
        self.pending=defaultdict(deque)
        self.used={}
        self.lock=threading.Lock()
        for call in calls:
            self.pending[request_key(call['request']['messages'])].append(call)

    def complete(self,messages):
        """Return the next original response for these exact message bytes."""
        qid=QUESTION.get()
        key=request_key(messages)
        with self.lock:
            queue=self.pending[key]
            if queue:
                call=queue.popleft()
                self.used[call['call']]=qid
                return response_text(call['response'])
        if self.live is None:
            raise MissingReplay()
        with self.live.scope('judge:'+qid):
            return self.live.complete(messages)

    def get_llm(self,tools=None,quiet=False,reasoning_level='medium',model=None):
        """Preserve the original evaluator factory contract."""
        if tools or reasoning_level!='medium' or model not in {None,'gpt-5.6-luna'}:
            raise ValueError('Recovery cannot change the declared model treatment')
        replay=self
        class LLM:
            def generate(self,messages):
                yield replay.complete([{'role':m.role,'content':m.content} for m in messages])
        return LLM()


def load_calls(work,source=None):
    """Verify all original completions, including one post-response exit failure."""
    calls=[]
    repaired=[]
    source=source or work/'judge'
    for path in sorted((source/'calls').glob('*.json')):
        call=json.loads(path.read_text(encoding='utf-8'))
        if call['status']!='complete':
            result=call.get('bridge_failure') or {}
            if not bound_subscription_completion(result,'openai-codex','gpt-5.6-luna',call['request']['messages']):
                raise ValueError('Only a complete bound response can repair a process-exit failure')
            call={**call,'response':result}
            repaired.append(call['call'])
        result=call['response']
        if (result['model']!='gpt-5.6-luna' or result['status']!='completed'
                or result['reasoning']['effort']!='medium'
                or result['usage']['output_tokens']>8192):
            raise ValueError('Original response is not evaluable under the frozen model contract')
        calls.append(call)
    if len(repaired)!=1:
        raise ValueError('This versioned recovery requires exactly one verified completed-reply exit failure')
    return calls,repaired


def verify_response_history(work,source):
    """Bind a normalized replay cache to every immutable physical source receipt."""
    manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    originals={}
    for relative,digest in manifest['source_receipt_sha256'].items():
        path=(work/relative).resolve()
        if not path.is_relative_to(work.resolve()) or sha(path)!=digest:
            raise ValueError('Original response history changed')
        originals[relative]=json.loads(path.read_text(encoding='utf-8'))
    seen=set()
    for path in sorted((source/'calls').glob('*.json')):
        normalized=json.loads(path.read_text(encoding='utf-8'))
        original_number=normalized.pop('original_call_number')
        stage=normalized.pop('original_stage')
        digest=normalized.pop('original_sha256')
        relative=f'{stage}/calls/{original_number:06d}.json'
        normalized['call']=original_number
        if (relative in seen or relative not in originals
                or digest!=manifest['source_receipt_sha256'][relative]
                or normalized!=originals[relative]):
            raise ValueError('Normalized response differs from its original receipt')
        seen.add(relative)
    missing={row['source'] for row in manifest['unevaluable_attempts']}
    if seen & missing or seen | missing!=set(originals) or len(seen)!=manifest['available_responses']:
        raise ValueError('Response history coverage changed')
    return sha(source/'manifest.json')


def recorded_orders(calls,questions,template,extract_json):
    """Restore original document permutations before replaying literal prompts."""
    sentinel=template.format(query='RECOVERY_QUERY',gold_documents='RECOVERY_GOLD',candidate_documents='RECOVERY_CANDIDATES')
    pattern=re.escape(sentinel)
    for name,label in [('query','QUERY'),('gold','GOLD'),('candidates','CANDIDATES')]:
        pattern=pattern.replace('RECOVERY_'+label,'(?P<'+name+'>.*?)')
    matcher=re.compile(pattern,re.DOTALL)
    identities={q['question']:qid for qid,q in questions.items()}
    orders=defaultdict(list)
    attempts=defaultdict(int)
    for call in calls:
        match=matcher.fullmatch(call['request']['messages'][0]['content'])
        if not match:
            continue
        qid=identities[match['query']]
        ids=re.findall(r'^Document ID: (dsid_[a-f0-9]+)$',match['candidates'],re.MULTILINE)
        gold=re.findall(r'^Document ID: (dsid_[a-f0-9]+)$',match['gold'],re.MULTILINE)
        if attempts[qid]==0:
            orders[qid].append(ids)
        valid=False
        try:
            parsed=json.loads(extract_json(response_text(call['response'])))
            valid=all(isinstance(parsed.get(i),dict) and parsed[i].get('classification') in {'required','valid','invalid'}
                      and isinstance(parsed[i].get('reason'),str) for i in gold+ids)
        except Exception:
            pass
        attempts[qid]=0 if valid or attempts[qid]==2 else attempts[qid]+1
    return dict(orders)


def run(work,mode,generation=1):
    """Replay offline first, then complete only missing first-evaluable judgments."""
    binding,path_map=setup(work)
    suffix='' if generation==1 else f'-{generation:03d}'
    source=work/'judge' if generation==1 else work/('judge-recovery-source'+suffix)
    audit_root=work/('judge-replay-audit'+suffix)
    binding_path=work/('judge-recovery-binding'+suffix+'.json')
    history_digest=verify_response_history(work,source) if generation>1 else None
    questions_path=work.parents[1]/'evaluations/enterprise-rag-bench/raw/questions.jsonl'
    if sha(questions_path)!=binding['questions_sha256']:
        raise ValueError('Original question bank changed')
    questions={q['question_id']:q for line in questions_path.read_text(encoding='utf-8').splitlines()
               if line.strip() for q in [json.loads(line)]}
    rows=[json.loads(line) for line in (work/'answers/answers.jsonl').read_text(encoding='utf-8').splitlines()]
    submission=json.loads((work/'answers/submission.json').read_text(encoding='utf-8'))
    if (sha(work/'answers/answers.jsonl')!=submission['answers_sha256']
            or sha(work/'answer-binding.json')!=submission['answer_binding_sha256']
            or len(rows)!=500 or {r['question_id'] for r in rows}!=set(questions)):
        raise ValueError('The original 500-answer submission changed')
    calls,repaired=load_calls(work,source)
    import src.llm
    import src.llm.factory
    import importlib
    # Import the unchanged official functions after the replay factory is installed.
    replay=Replay(calls)
    src.llm.get_llm=src.llm.factory.get_llm=replay.get_llm
    evaluator=importlib.import_module('src.scripts.answer_evaluation.metrics_based_eval')
    utilities=importlib.import_module('src.utils.eval_utils')
    orders=recorded_orders(calls,questions,utilities.ANSWER_DOC_EVALUATION_PROMPT,utilities.extract_json_from_response)
    counters=defaultdict(int)
    original_shuffle=utilities.random.shuffle
    random.seed(binding['random_seed'])

    def shuffle(values):
        qid=QUESTION.get()
        offset=counters[qid]
        counters[qid]+=1
        if offset<len(orders.get(qid,[])):
            order=orders[qid][offset]
            if sorted(order)!=sorted(values):
                raise ValueError('Recorded document permutation does not match the frozen candidates')
            values[:]=order
        else:
            original_shuffle(values)
    utilities.random.shuffle=shuffle
    evaluator.ThreadPoolExecutor=ContextExecutor
    failures=defaultdict(list)
    names={'evaluate_answer_correctness':True,'evaluate_documents_with_consensus':True,
           'update_gold_answer':False,'extract_answer_facts':False,'extract_anti_hallucination_facts':False,
           'strip_answer_citations':False,'validate_single_fact':False}
    def audit(name,original,tuple_result):
        def call(*args,**kwargs):
            result=original(*args,**kwargs)
            if (result[0] is None if tuple_result else result is None):
                failures[QUESTION.get()].append(name)
            return result
        return call
    for name,tuple_result in names.items():
        setattr(evaluator,name,audit(name,getattr(evaluator,name),tuple_result))

    target=audit_root if mode=='audit' else work/f'judge-recovery-{generation:03d}'
    target.mkdir()
    (target/'cases').mkdir()
    retained={}
    if mode=='live':
        audit_result=json.loads((audit_root/'completion.json').read_text(encoding='utf-8'))
        frozen=json.loads(binding_path.read_text(encoding='utf-8'))
        if (tree(Path(__file__).resolve().parent)!=frozen['runner_code']
                or sha(audit_root/'completion.json')!=frozen['audit_sha256']
                or tree(audit_root)!=frozen['audit_files']
                or tree(source/'calls')!=frozen['original_calls']
                or history_digest!=frozen.get('source_history_manifest_sha256')
                or sha(work/'answer-binding.json')!=frozen['parent_binding_sha256']):
            raise ValueError('Frozen recovery or offline audit changed')
        for qid in audit_result['complete_ids']:
            retained[qid]=json.loads((audit_root/'cases'/(qid+'.json')).read_text(encoding='utf-8'))
        used_by_complete={int(number) for number,qid in audit_result['used_calls'].items() if qid in retained}
        replay=Replay([c for c in calls if c['call'] not in used_by_complete],
            ModelTransport(binding['provider'],target/'calls',frozen['remaining_budget_usd'],
                           binding['model_concurrency'],model=binding['model'],allow_empty=True))
        src.llm.get_llm=src.llm.factory.get_llm=evaluator.get_llm=utilities.get_llm=replay.get_llm
        import src.utils.questions as question_tools
        question_tools.get_llm=replay.get_llm
    complete=dict(retained)
    missing=[]

    def score(row):
        qid=row['question_id']
        token=QUESTION.set(qid)
        row=copy.deepcopy(row)
        try:
            # Exact order and delegates from upstream evaluate_single_question.
            row['answer']=evaluator.strip_answer_citations(row['answer'])
            updated=None
            if row.get('document_ids') and questions[qid].get('expected_doc_ids'):
                _,updated=evaluator.process_question_docs(row,questions,path_map)
            result=evaluator.score_answer(row,updated or questions[qid],questions[qid])
            if failures[qid]:
                raise TransportUnavailable('An upstream helper did not provide an evaluable verdict')
            receipt={'result':result,'updated_question':updated}
            write_json(target/'cases'/(qid+'.json'),receipt)
            return qid,receipt
        except MissingReplay:
            return qid,None
        finally:
            QUESTION.reset(token)
    try:
        pending=[row for row in rows if row['question_id'] not in retained]
        with ContextExecutor(max_workers=1 if mode=='audit' else binding['question_concurrency']) as pool:
            for future in as_completed([pool.submit(score,row) for row in pending]):
                qid,receipt=future.result()
                if receipt is None:
                    missing.append(qid)
                else:
                    complete[qid]=receipt
                if (len(complete)+len(missing))%25==0:
                    print(json.dumps({'phase':mode,'complete_questions':len(complete),
                                      'missing_questions':len(missing),'planned':500}),flush=True)
        summary={'mode':mode,'complete_ids':sorted(complete),'missing_ids':sorted(missing),
                 'used_calls':replay.used,'recovered_completed_reply_calls':repaired,
                 'recorded_permutation_questions':len(orders)}
        if mode=='live':
            if len(complete)!=500 or missing or replay.live.errors or any(failures.values()):
                raise TransportUnavailable('Recovered evaluation must cover all 500 questions without errors')
            all_used=set(used_by_complete)|set(replay.used)
            if all_used!={c['call'] for c in calls}:
                raise ValueError('Some original completed model responses were not preserved')
            results=[complete[qid]['result'] for qid in sorted(complete)]
            result={'aggregate_stats':evaluator.build_aggregate_stats(results,0,500),
                    'question_type_stats':evaluator.build_question_type_stats(results),'questions':results}
            checked=validate_official_completion(result,set(questions))
            write_json(target/'results.json',result)
            summary.update(status=checked['status'],questions=500,result_sha256=sha(target/'results.json'),
                           aggregate_stats=checked['aggregate_stats'],new_model_usage=replay.live.summary(),
                           original_responses_preserved=len(all_used),retained_questions=len(retained))
        else:
            # No request may belong to different questions unless its actual replies agree.
            owners=defaultdict(set)
            replies=defaultdict(set)
            for call in calls:
                key=request_key(call['request']['messages'])
                if call['call'] in replay.used:
                    owners[key].add(replay.used[call['call']])
                replies[key].add(response_text(call['response']))
            if any(len(owners[k])>1 and len(replies[k])>1 for k in owners):
                raise ValueError('Ambiguous cross-question response ownership cannot be recovered')
            prior={r['question_id']:r for r in json.loads((source/'results.json').read_text(encoding='utf-8'))['questions']}
            summary['original_result_matches']=sum(prior[qid]==r['result'] for qid,r in complete.items())
        write_json(target/'completion.json',summary)
        print(json.dumps({key:value for key,value in summary.items() if key not in {'complete_ids','missing_ids','used_calls'}}))
        return summary
    finally:
        if replay.live:
            write_json(target/'usage.json',{'helper_failures':dict(failures),**replay.live.summary()})
        utilities.random.shuffle=original_shuffle


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('mode',choices=['audit','live'])
    parser.add_argument('--generation',type=int,choices=[1,2,3],default=1)
    args=parser.parse_args()
    run(args.work.resolve(),args.mode,args.generation)
