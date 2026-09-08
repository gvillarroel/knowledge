"""Generate Classical answers and run pinned upstream EnterpriseRAG evaluation.

The answer and judge processes are separate. Answer generation receives only
questions, retrieved IDs and their source documents. Gold answers and facts are
loaded only by the judge. No score is published from incomplete model work.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
import hashlib
import importlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import random
import sys
import threading
import urllib.parse
import urllib.request

from full_corpus_classical import sha, write_json
from official_model_transport import ModelTransport, TransportUnavailable


def document_file(root: Path, relative: str) -> Path:
    """Resolve one pinned source path without accepting traversal or links."""
    path=PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise ValueError('Unsafe source path')
    target=root.joinpath(*path.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Source path escaped the declared document root')
    return target


def acquire_documents(work: Path) -> dict:
    """Fetch the exact original JSON for every retrieved or reference document."""
    required=json.loads((work/'retrieval/required-documents.json').read_text(encoding='utf-8'))
    uuid_index=json.loads((work/'uuid_index.json').read_text(encoding='utf-8'))
    revision=json.loads((work/'upstream-revision.json').read_text(encoding='utf-8'))['commit']
    root=work/'official-documents/generated_data/sources'
    if (work/'official-documents/manifest.json').exists():
        raise FileExistsError('Official document acquisition is already sealed')
    root.mkdir(parents=True,exist_ok=True)

    def fetch(identity):
        relative=uuid_index[identity]
        path=document_file(root,relative)
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            url=('https://raw.githubusercontent.com/onyx-dot-app/EnterpriseRAG-Bench/'+revision+
                 '/generated_data/sources/'+urllib.parse.quote(relative,safe='/'))
            request=urllib.request.Request(url,headers={'User-Agent':'knowledge-enterpriserag-full/1.0'})
            with urllib.request.urlopen(request,timeout=120) as response:
                payload=response.read()
            parsed=json.loads(payload)
            if parsed.get('dataset_doc_uuid')!=identity:
                raise ValueError('Original source identity does not match the reference')
            with path.open('xb') as stream:
                stream.write(payload)
        parsed=json.loads(path.read_text(encoding='utf-8'))
        if parsed.get('dataset_doc_uuid')!=identity:
            raise ValueError('Cached original source identity mismatch')
        return identity,{'path':relative,'sha256':sha(path),'bytes':path.stat().st_size}

    with ThreadPoolExecutor(max_workers=8) as pool:
        files=dict(pool.map(fetch,required['document_ids']))
    receipt={'upstream_commit':revision,'documents':len(files),'files':dict(sorted(files.items())),
             'colliding_ids_requiring_citation_resolution':required['ambiguous_upstream_ids'],
             'uuid_index_sha256':sha(work/'uuid_index.json')}
    write_json(work/'official-documents/manifest.json',receipt)
    return {'status':'complete','documents':len(files)}


def canonical_citations(hits: list[dict], originals: dict, exporter) -> tuple[list[str],list[dict]]:
    """Deduplicate public IDs only when the first hit exactly matches the official source."""
    kept=[]
    dropped=[]
    for hit in hits:
        identity=hit['upstream_id']
        if identity in kept:
            dropped.append({'upstream_id':identity,'upstream_path':hit['upstream_path'],
                            'raw_sha256':hit['raw_sha256']})
            continue
        source=originals[identity]
        path=PurePosixPath(source['path'])
        expected_path=str(path.parent/exporter.get_export_filename(identity,path.name))
        expected_text=exporter.convert_to_text(source['document']).replace('\r\n','\n').replace('\r','\n')
        if hit['upstream_path']!=expected_path or hit['raw_body']!=expected_text:
            raise ValueError('First retrieved identity does not exactly match the pinned official source')
        kept.append(identity)
    return kept,dropped


def resolve_citations(work: Path) -> dict:
    """Bind canonical public citations before any answer, retaining the raw retrieval pass."""
    if (work/'answers').exists() or (work/'judge').exists():
        raise ValueError('Citation projection must precede all model answers')
    manifest=json.loads((work/'official-documents/manifest.json').read_text(encoding='utf-8'))
    sys.path.insert(0,str(work/'upstream-code'))
    exporter=importlib.import_module('src.scripts.data_gen_stage_4_data_export.export_data')
    root=work/'official-documents/generated_data/sources'
    originals={}
    for identity,row in manifest['files'].items():
        path=document_file(root,row['path'])
        if sha(path)!=row['sha256']:
            raise ValueError('Original source changed before citation projection')
        originals[identity]={'path':row['path'],'document':json.loads(path.read_text(encoding='utf-8'))}
    original=json.loads((work/'retrieval/answer-input.json').read_text(encoding='utf-8'))
    rows=[]
    dropped=[]
    for row in original['questions']:
        case=json.loads((work/'retrieval/cases'/(row['question_id']+'.json')).read_text(encoding='utf-8'))
        if case['question']!=row['question'] or case['document_ids']!=row['document_ids']:
            raise ValueError('Question-only inputs diverged from frozen retrieval evidence')
        ids,excluded=canonical_citations(case['hits'],originals,exporter)
        rows.append({**row,'document_ids':ids})
        if excluded:
            dropped.append({'question_id':row['question_id'],'duplicate_physical_citations':excluded})
    projection=work/'retrieval/answer-input-public.json'
    write_json(projection,{'questions':rows})
    receipt={'status':'pass','policy':'first hit must match pinned original JSON path and exact export text; deduplicate public IDs without refill',
             'questions':len(rows),'source_input_sha256':sha(work/'retrieval/answer-input.json'),
             'projected_input_sha256':sha(projection),'documents_manifest_sha256':sha(work/'official-documents/manifest.json'),
             'retrieval_summary_sha256':sha(work/'retrieval/summary.json'),
             'affected_questions':len(dropped),'dropped_physical_citations':sum(len(r['duplicate_physical_citations']) for r in dropped),
             'unique_citations':sum(len(r['document_ids']) for r in rows),'dropped':dropped,
             'retrieval_rankings_changed':False,'source_corpus_changed':False,'model_calls':0}
    write_json(work/'citation-binding.json',receipt)
    return {key:receipt[key] for key in ['status','questions','affected_questions','dropped_physical_citations','unique_citations']}


def tree(root: Path) -> dict:
    """Bind code and published evidence without transient interpreter files."""
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}


def copilot_runtime_binding(work: Path, provider: str = 'github-copilot') -> dict:
    """Verify a private copied runtime while excluding refreshable credentials."""
    variable='ENTERPRISE_CODEX_CONFIG' if provider=='openai-codex' else 'ENTERPRISE_COPILOT_CONFIG'
    config_path=Path(os.environ[variable]).resolve()
    if not config_path.is_relative_to(work):
        raise ValueError('Copilot configuration must be inside the local work directory')
    config=json.loads(config_path.read_text(encoding='utf-8'))
    for key in ['authPath','modelsStorePath','piPackageRoot','node_executable']:
        if not Path(config[key]).resolve().is_relative_to(work):
            raise ValueError('Copilot runtime and refresh paths must remain inside the work directory')
    lock_path=config_path.with_name('runtime-lock.json')
    lock=json.loads(lock_path.read_text(encoding='utf-8'))
    if tree(Path(config['piPackageRoot']))!=lock['files'] or sha(Path(config['node_executable']))!=lock['node_sha256']:
        raise ValueError('Frozen Copilot runtime changed')
    return {'config_sha256':sha(config_path),'runtime_lock_sha256':sha(lock_path),
            'pi_version':lock['pi_version'],'node_version':lock['node_version'],
            'node_sha256':lock['node_sha256'],'credential_content_included':False}


def seal(work: Path, provider: str, budget: float, model: str = 'gpt-5.4',
         concurrency: int = 4, model_concurrency: int = 8) -> dict:
    """Freeze provider, exact prompts, evaluator code and inputs before answers."""
    if (work/'answers').exists() or (work/'judge').exists():
        raise ValueError('Cannot seal after answer or judge execution starts')
    if not math.isfinite(budget) or budget <= 0:
        raise ValueError('A positive finite execution budget is required')
    if model not in {'gpt-5.4','gpt-5.6-luna'} or min(concurrency,model_concurrency)<1:
        raise ValueError('An allowlisted model and positive concurrency are required')
    citations=json.loads((work/'citation-binding.json').read_text(encoding='utf-8'))
    if (citations['status']!='pass' or citations['questions']!=500
            or citations['projected_input_sha256']!=sha(work/'retrieval/answer-input-public.json')
            or citations['source_input_sha256']!=sha(work/'retrieval/answer-input.json')
            or citations['documents_manifest_sha256']!=sha(work/'official-documents/manifest.json')
            or citations['retrieval_summary_sha256']!=sha(work/'retrieval/summary.json')):
        raise ValueError('A verified canonical public citation projection is required')
    source=Path(__file__).resolve().parent
    frozen=work/'answer-tools'
    frozen.mkdir()
    import shutil
    for name in ['run_official_classical_answers.py','official_model_transport.py',
                 'subscription_model_bridge.mjs','full_corpus_classical.py']:
        shutil.copyfile(source/name,frozen/name)
    binding={'schema_version':'enterprise-official-classical/1.1','provider':provider,'model':model,
             'reasoning':'medium','top_k':10,'questions':500,'answer_attempts':1,
             'max_output_tokens':8192,'budget_usd':budget,'model_concurrency':model_concurrency,
             'question_concurrency':concurrency,'answer_model':model,'judge_model':model,
             'public_comparison_eligible':model=='gpt-5.4' and provider!='openai-codex',
             'subscription_protocol':({'system_instruction':'You are a helpful assistant.',
                  'text_verbosity':'low','api_output_cap':None,'host_output_acceptance_limit':8192,
                  'reservation_output_maximum':128000} if provider=='openai-codex' else None),
             'answer_input_file':'retrieval/answer-input-public.json',
             'answer_input_sha256':sha(work/'retrieval/answer-input-public.json'),
             'citation_binding_sha256':sha(work/'citation-binding.json'),
             'retrieval_sha256':sha(work/'retrieval/summary.json'),
             'questions_sha256':json.loads((work/'index-binding.json').read_text(encoding='utf-8'))['questions_sha256'],
             'documents_manifest_sha256':sha(work/'official-documents/manifest.json'),
             'upstream_code':tree(work/'upstream-code'), 'runner_code':tree(frozen),
             'citation_stripping':True,'document_correction':True,
             'upstream_parser_attempts':3,'http_retries':0,'random_seed':20260908,
             'score_contract':'unchanged upstream metrics_based_eval with correction enabled',
             'scope':'Local reproduction; not submitted or independently verified by the leaderboard maintainers'}
    if provider in {'github-copilot','openai-codex'}:
        binding['copilot_runtime']=copilot_runtime_binding(work,provider)
    write_json(work/'answer-binding.json',binding)
    return {'status':'sealed','binding_sha256':sha(work/'answer-binding.json')}


def setup(work: Path):
    """Verify bindings and import the pinned upstream code from its own root."""
    binding=json.loads((work/'answer-binding.json').read_text(encoding='utf-8'))
    if binding['provider'] in {'github-copilot','openai-codex'} and copilot_runtime_binding(work,binding['provider'])!=binding['copilot_runtime']:
        raise ValueError('Frozen Copilot runtime binding changed')
    if tree(work/'upstream-code')!=binding['upstream_code'] or tree(work/'answer-tools')!=binding['runner_code']:
        raise ValueError('Frozen upstream or runner code changed')
    if sha(work/binding['answer_input_file'])!=binding['answer_input_sha256']:
        raise ValueError('Frozen answer inputs changed')
    if sha(work/'citation-binding.json')!=binding['citation_binding_sha256']:
        raise ValueError('Frozen public citation projection changed')
    if sha(work/'retrieval/summary.json')!=binding['retrieval_sha256']:
        raise ValueError('Frozen retrieval summary changed')
    manifest=work/'official-documents/manifest.json'
    if sha(manifest)!=binding['documents_manifest_sha256']:
        raise ValueError('Original source bindings changed')
    docs=json.loads(manifest.read_text(encoding='utf-8'))
    root=work/'official-documents/generated_data/sources'
    for row in docs['files'].values():
        if sha(document_file(root,row['path']))!=row['sha256']:
            raise ValueError('Original source bytes changed')
    os.chdir(work/'official-documents')
    sys.path.insert(0,str(work/'upstream-code'))
    return binding,{identity:row['path'] for identity,row in docs['files'].items()}


def generate_answers(work: Path) -> dict:
    """Make one fresh answer per question with the upstream baseline prompt."""
    binding,uuid_index=setup(work)
    from src.prompts.vector_search_answer_gen import ANSWER_GEN_PROMPT
    from src.utils.retrieval import format_context_documents
    rows=json.loads((work/binding['answer_input_file']).read_text(encoding='utf-8'))['questions']
    if len(rows)!=500 or len({row['question_id'] for row in rows})!=500:
        raise ValueError('Exactly 500 question-only answer inputs are required')
    output=work/'answers'
    output.mkdir()
    transport=ModelTransport(binding['provider'],output/'calls',binding['budget_usd'],
                             binding['model_concurrency'],model=binding['answer_model'])

    def answer(row):
        context=format_context_documents(row['document_ids'],uuid_index)
        if '[Error loading document:' in context:
            raise ValueError('Answer evidence failed to load')
        prompt=ANSWER_GEN_PROMPT.format(context_documents=context,question=row['question'])
        with transport.scope('answer:'+row['question_id']):
            text=transport.complete([{'role':'user','content':prompt}])
        result={'question_id':row['question_id'],'answer':text,'document_ids':row['document_ids']}
        write_json(output/(row['question_id']+'.json'),result)
        return result

    completed=[]
    try:
        with ThreadPoolExecutor(max_workers=binding['question_concurrency']) as pool:
            futures=[pool.submit(answer,row) for row in rows]
            for future in as_completed(futures):
                completed.append(future.result())
                if len(completed)%25==0:
                    print(json.dumps({'phase':'answers','completed':len(completed),'planned':500}),flush=True)
        if len(completed)!=500 or transport.errors:
            raise TransportUnavailable('Answer stage is incomplete')
        with (output/'answers.jsonl').open('x',encoding='utf-8',newline='\n') as stream:
            for row in sorted(completed,key=lambda r:r['question_id']):
                stream.write(json.dumps(row,ensure_ascii=False)+'\n')
        write_json(output/'submission.json',{
            'status':'complete','questions':500,
            'answers_sha256':sha(output/'answers.jsonl'),
            'answer_binding_sha256':sha(work/'answer-binding.json')})
        return {'status':'complete','questions':500,**transport.summary()}
    finally:
        write_json(output/'usage.json',{'completed_answers':len(completed),**transport.summary()})


def validate_official_completion(result: dict, expected_ids: set[str]) -> dict:
    """Require every official judgment and independently verify its mean score."""
    stats=result['aggregate_stats']
    rows=result['questions']
    identities=[row['question_id'] for row in rows]
    if (len(expected_ids)!=500 or len(rows)!=500 or len(set(identities))!=500
            or set(identities)!=expected_ids or stats['total_questions']!=500
            or stats['completed_questions']!=500 or stats['skipped_rows']!=0):
        raise TransportUnavailable('The official result does not cover all 500 frozen questions')

    def number(value, maximum=100):
        return (type(value) in {int,float} and math.isfinite(value)
                and 0 <= value <= maximum)

    for row in rows:
        if (type(row['answer_correct']) is not bool or type(row['corrected']) is not bool
                or not number(row['completeness_pct'])
                or (row['document_recall_pct'] is not None and not number(row['document_recall_pct']))
                or (row['invalid_extra_docs'] is not None and not number(row['invalid_extra_docs'],math.inf))):
            raise TransportUnavailable('The official result contains an unavailable or invalid judgment')
    recalls=[row['document_recall_pct'] for row in rows if row['document_recall_pct'] is not None]
    extras=[row['invalid_extra_docs'] for row in rows if row['invalid_extra_docs'] is not None]
    expected={
        'num_corrected_questions':sum(row['corrected'] for row in rows),
        'average_correctness_pct':round(sum(row['answer_correct'] for row in rows)/500*100,2),
        'average_completeness_pct':round(sum(row['completeness_pct'] for row in rows)/500,2),
        'combined_correctness_completeness_score':round(
            sum(row['completeness_pct'] if row['answer_correct'] else 0 for row in rows)/500,2),
        'average_recall_pct':round(sum(recalls)/len(recalls),2) if recalls else 0.0,
        'average_invalid_extra_docs':round(sum(extras)/len(extras),2) if extras else 0.0}
    if any(not number(stats[key],math.inf) or stats[key]!=value for key,value in expected.items()):
        raise TransportUnavailable('The official aggregate does not match its question-level evidence')
    return {'status':'complete','questions':500,'aggregate_stats':stats}


@contextmanager
def observe_evaluator(evaluator):
    """Audit terminal helper failures while retaining exact upstream return values."""
    names={'evaluate_answer_correctness':True,'evaluate_documents_with_consensus':True,
           'update_gold_answer':False,'extract_answer_facts':False,
           'extract_anti_hallucination_facts':False,'strip_answer_citations':False,
           'validate_single_fact':False}
    originals={name:getattr(evaluator,name) for name in names}
    failures=[]
    lock=threading.Lock()

    def wrap(name,original):
        def call(*args,**kwargs):
            try:
                result=original(*args,**kwargs)
            except Exception:
                with lock:
                    failures.append(name+':exception')
                raise
            terminal=result[0] is None if names[name] else result is None
            if terminal:
                with lock:
                    failures.append(name+':unavailable')
            return result
        return call

    try:
        for name,original in originals.items():
            setattr(evaluator,name,wrap(name,original))
        yield failures
    finally:
        for name,original in originals.items():
            setattr(evaluator,name,original)


def judge_answers(work: Path, questions: Path) -> dict:
    """Use the unchanged official scorer and its document-correction procedure."""
    binding,uuid_index=setup(work)
    if sha(questions)!=binding['questions_sha256']:
        raise ValueError('Pinned official question bank changed')
    answer_file=work/'answers/answers.jsonl'
    submission=json.loads((work/'answers/submission.json').read_text(encoding='utf-8'))
    if (sha(answer_file)!=submission['answers_sha256']
            or sha(work/'answer-binding.json')!=submission['answer_binding_sha256']):
        raise ValueError('The frozen answer submission changed')
    answer_rows=[json.loads(row) for row in answer_file.read_text(encoding='utf-8').splitlines()]
    if len(answer_rows)!=500 or len({row['question_id'] for row in answer_rows})!=500:
        raise ValueError('A complete frozen 500-answer submission is required')
    answers_usage=json.loads((work/'answers/usage.json').read_text(encoding='utf-8'))
    if answers_usage['transport_errors']:
        raise ValueError('Unavailable answer work cannot be ranked')
    output=work/'judge'
    output.mkdir()
    budget=binding['budget_usd']-answers_usage['cost_usd']
    transport=ModelTransport(binding['provider'],output/'calls',budget,
                             binding['model_concurrency'],model=binding['judge_model'],allow_empty=True)
    import src.llm
    import src.llm.factory
    src.llm.get_llm=transport.get_llm
    src.llm.factory.get_llm=transport.get_llm
    # Imports below bind the same transport in every official fact/correction
    # helper; the prompts and evaluation functions themselves remain unchanged.
    evaluator=importlib.import_module('src.scripts.answer_evaluation.metrics_based_eval')
    cache=output/'uuid-index.json'
    write_json(cache,uuid_index)
    random.seed(binding['random_seed'])
    previous=sys.argv
    sys.argv=['metrics_based_eval','--answers-file',str(answer_file),'--questions-file',str(questions),
              '--results-file',str(output/'results.json'),'--updated-questions-file',str(output/'questions-updated.jsonl'),
              '--uuid-index-cache-file',str(cache),'--parallelism',str(binding['question_concurrency'])]
    evaluator_failures=[]
    try:
        with observe_evaluator(evaluator) as evaluator_failures:
            evaluator.main()
        result=json.loads((output/'results.json').read_text(encoding='utf-8'))
        if transport.errors or evaluator_failures:
            raise TransportUnavailable('Model errors make the official evaluation unavailable')
        expected_ids={row['question_id'] for row in json.loads(
            (work/binding['answer_input_file']).read_text(encoding='utf-8'))['questions']}
        complete=validate_official_completion(result,expected_ids)
        complete.update(result_sha256=sha(output/'results.json'),**transport.summary())
        write_json(output/'completion.json',complete)
        return complete
    finally:
        sys.argv=previous
        write_json(output/'usage.json',{'evaluator_failures':evaluator_failures,**transport.summary()})


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('acquire-documents')
    commands.add_parser('resolve-citations')
    freeze=commands.add_parser('seal')
    freeze.add_argument('--provider',choices=['openai','openrouter','github-copilot','openai-codex'],required=True)
    freeze.add_argument('--model',choices=['gpt-5.4','gpt-5.6-luna'],default='gpt-5.4')
    freeze.add_argument('--question-concurrency',type=int,default=4)
    freeze.add_argument('--model-concurrency',type=int,default=8)
    freeze.add_argument('--budget-usd',type=float,default=50)
    commands.add_parser('answer')
    judge=commands.add_parser('judge')
    judge.add_argument('--questions',type=Path,required=True)
    args=parser.parse_args()
    work=args.work.resolve()
    if args.command=='acquire-documents':
        result=acquire_documents(work)
    elif args.command=='resolve-citations':
        result=resolve_citations(work)
    elif args.command=='seal':
        result=seal(work,args.provider,args.budget_usd,args.model,args.question_concurrency,args.model_concurrency)
    elif args.command=='answer':
        result=generate_answers(work)
    else:
        result=judge_answers(work,args.questions.resolve())
    print(json.dumps(result,allow_nan=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
