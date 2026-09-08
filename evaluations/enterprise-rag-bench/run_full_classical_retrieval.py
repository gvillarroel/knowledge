"""Evaluate all public Enterprise queries against one frozen full-corpus index."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import statistics
import time

from full_corpus_classical import Index, native, sha, write_json


def retrieval_metrics(retrieved: list[str], relevant: list[str]) -> dict | None:
    """Keep no-reference questions outside retrieval metric denominators."""
    gold = set(relevant)
    if not gold:
        return None
    unique = list(dict.fromkeys(retrieved))[:10]
    hits = [position for position, identity in enumerate(unique, 1) if identity in gold]
    gain = sum(1/math.log2(position+1) for position in hits)
    ideal = sum(1/math.log2(position+1) for position in range(1, min(len(gold), 10)+1))
    return {'ndcg_at_10': gain/ideal, 'recall_at_10': len(hits)/len(gold),
            'mrr_at_10': 1/min(hits) if hits else 0.0,
            'complete_coverage_at_10': float(set(unique).issuperset(gold))}


def aggregate(rows: list[dict]) -> dict:
    """Aggregate complete retrieval cases without manufacturing answer scores."""
    scored = [row['metrics'] for row in rows if row['metrics'] is not None]
    return {'questions': len(rows), 'questions_with_references': len(scored),
            'metrics': {name: statistics.mean(row[name] for row in scored)
                        for name in scored[0]} if scored else None,
            'query_seconds': sum(row['query_seconds'] for row in rows),
            'mean_query_seconds': statistics.mean(row['query_seconds'] for row in rows),
            'p95_query_seconds': sorted(row['query_seconds'] for row in rows)[math.ceil(0.95*len(rows))-1]}


def run(index_root: Path, consultant: Path, questions_path: Path, output: Path, binding: dict) -> dict:
    """Score exactly one immutable pass and retain private per-query evidence."""
    if output.exists():
        raise FileExistsError('Retrieval result path already exists')
    if sha(questions_path) != binding['questions_sha256']:
        raise ValueError('Questions differ from the pinned public dataset')
    questions = [json.loads(line) for line in questions_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    if len(questions) != binding['expected_questions'] or len({q['question_id'] for q in questions}) != len(questions):
        raise ValueError('Incomplete or duplicate question set')
    index = Index(index_root, native(consultant))
    if index.meta['documents'] != binding['expected_documents']:
        index.close()
        raise ValueError('Full corpus is required')
    output.mkdir(parents=True)
    (output / 'cases').mkdir()
    results, categories = [], defaultdict(list)
    referenced = set()
    answer_prompts = []
    try:
        for question in sorted(questions, key=lambda q: q['question_id']):
            start = time.perf_counter()
            hits = index.search(question['question'], 10)
            seconds = time.perf_counter()-start
            ids = [hit['upstream_id'] for hit in hits]
            metrics = retrieval_metrics(ids, question['expected_doc_ids'])
            row = {'question_id': question['question_id'], 'category': question['question_type'],
                   'question': question['question'], 'query_seconds': seconds,
                   'document_ids': ids, 'hits': hits, 'metrics': metrics}
            write_json(output / 'cases' / (question['question_id']+'.json'), row)
            results.append({key: row[key] for key in ['question_id','category','query_seconds','document_ids','metrics']})
            categories[row['category']].append(row)
            referenced.update(ids)
            referenced.update(question['expected_doc_ids'])
            answer_prompts.append({'question_id': question['question_id'],
                                   'question': question['question'], 'document_ids': ids})
            if len(results) % 25 == 0:
                print(json.dumps({'phase':'retrieval','completed':len(results),'planned':len(questions)}),flush=True)
        duplicate_rows = index.db.execute('SELECT upstream_id,COUNT(*) FROM documents GROUP BY upstream_id HAVING COUNT(*)>1').fetchall()
        ambiguous_references = sorted(referenced & {row[0] for row in duplicate_rows})
        summary = {'schema_version':'enterprise-full-classical-retrieval/1.0', 'status':'complete',
                   'scope':'full-corpus-direct-bm25-retrieval',
                   'documents': index.meta['documents'], 'index_sha256': sha(index_root/'index.json'),
                   'questions_sha256': sha(questions_path), 'top_k':10, 'passes':1,
                   'all_questions':aggregate(results),
                   'categories':{category:aggregate(rows) for category,rows in sorted(categories.items())},
                   'ambiguous_upstream_ids_needed_for_answer_stage':len(ambiguous_references),
                   'answer_quality_score':None, 'public_leaderboard_position':None,
                   'model_calls':0, 'complete_semantic_okf_bundle':False}
        write_json(output/'summary.json',summary)
        write_json(output/'answer-input.json',{'questions':answer_prompts})
        write_json(output/'required-documents.json',{'document_ids':sorted(referenced),
                                                    'ambiguous_upstream_ids':ambiguous_references})
        if any(sha(index_root/name)!=digest for name,digest in index.meta['files'].items()):
            raise ValueError('Read-only index changed during retrieval')
        write_json(output/'integrity.json',{'status':'pass','index_unchanged':True,'queries':len(results),
                    'physical_citations':sum(len(row['document_ids']) for row in results)})
        return summary
    finally:
        index.close()


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['index','consultant','questions','output','binding']:
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=run(args.index,args.consultant,args.questions,args.output,
               json.loads(args.binding.read_text(encoding='utf-8')))
    print(json.dumps(result,allow_nan=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
