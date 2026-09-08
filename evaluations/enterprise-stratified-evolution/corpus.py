"""Prepare a fixed full-text, reference-enriched internal Enterprise corpus.

All 500 public questions have prior exposure. Include their references and
the previous full-corpus BM25 contexts, then add source-stratified distractors.
This is explicitly a reduced-corpus diagnostic, never a full-corpus score.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import zlib

from dataset import digest, write_new

REPO = Path(__file__).resolve().parents[2]


def priority(identity: str) -> str:
    return hashlib.sha256(('e7-corpus-v1\0'+identity).encode()).hexdigest()


def render_text(text: str) -> str:
    """Render Unicode next-line, line and paragraph separators as LF.

    The unchanged canonical builders split serialized RDF/JSONL with Python
    splitlines(). Normalize these three newline characters at the explicit
    source adapter boundary, preserving all other characters. Original bytes
    remain in the frozen source archive and are separately digest-bound.
    """
    return text.translate({0x85:'\n',0x2028:'\n',0x2029:'\n'})


def prepare(output: Path, target: int = 6000, minimum_per_source: int = 100) -> dict:
    """Create a new evaluator-free corpus, preserving every decoded body."""
    if target != 6000 or minimum_per_source != 100:
        raise ValueError('The predeclared internal corpus contract is fixed')
    full = REPO/'tmp/enterprise-classical-full-20260908'
    source = REPO/'tmp/enterprise-g2-replay/input'
    questions_path = REPO/'evaluations/enterprise-rag-bench/raw/questions.jsonl'
    query_rows = [json.loads(line) for line in questions_path.read_text(encoding='utf-8').splitlines()]
    contexts_path = full/'retrieval/answer-input-public.json'
    contexts = json.loads(contexts_path.read_text(encoding='utf-8'))['questions']
    references = {key for row in query_rows for key in row['expected_doc_ids']}
    required = references | {key for row in contexts for key in row['document_ids']}
    index_root = full/'full-index/index'
    database = sqlite3.connect((index_root/'documents.sqlite').as_uri()+'?mode=ro&immutable=1', uri=True)
    identities = database.execute('SELECT number,upstream_id FROM documents ORDER BY number').fetchall()
    groups = {}
    for number, identity in identities:
        groups.setdefault(identity,[]).append(number)
    if not required.issubset(groups):
        raise ValueError('Required evidence is absent from the full source index')
    available = {identity:numbers[0] for identity,numbers in groups.items() if len(numbers) == 1}
    canonical = json.loads((full/'uuid_index.json').read_text(encoding='utf-8'))
    aliases = []
    for identity in sorted(required-available.keys()):
        public_path = PurePosixPath(canonical[identity])
        canonical_export = (public_path.parent/(identity+'__'+public_path.stem+'.txt')).as_posix()
        matches = []
        for number in groups[identity]:
            packed = database.execute('SELECT payload FROM documents WHERE number=?',(number,)).fetchone()[0]
            row = json.loads(zlib.decompress(packed))
            if row['upstream_path'] == canonical_export:
                matches.append(number)
        if len(matches) != 1:
            raise ValueError('Required alias does not uniquely match the pinned public path')
        available[identity] = matches[0]
        aliases.append(identity)
    order = sorted(available, key=priority)
    cache = {}
    def get(identity):
        if identity not in cache:
            packed = database.execute('SELECT payload FROM documents WHERE number=?',(available[identity],)).fetchone()[0]
            cache[identity] = json.loads(zlib.decompress(packed))
        return cache[identity]
    selected = set(required)
    counts = Counter(get(identity)['source_id'] for identity in sorted(selected))
    manifest = json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    source_ids = {row['id'] for row in manifest['sources']}
    # Inspect only as many shuffled corpus rows as needed for each minimum;
    # all queried rows are original source records without evaluator fields.
    for identity in order:
        if all(counts[source_id] >= minimum_per_source for source_id in source_ids):
            break
        row = get(identity)
        if identity not in selected and counts[row['source_id']] < minimum_per_source:
            selected.add(identity)
            counts[row['source_id']] += 1
    if len(selected) > target:
        raise ValueError('Required evidence and source minima exceed the frozen corpus budget')
    for identity in order:
        if len(selected) == target:
            break
        if identity not in selected:
            selected.add(identity)
    output.mkdir(parents=True, exist_ok=False)
    incoming = output/'input'
    (incoming/'documents').mkdir(parents=True)
    counts = Counter()
    body_characters = 0
    normalized_bodies = separator_count = 0
    inventory = []
    with ExitStack() as stack:
        streams = {row['id']:stack.enter_context((incoming/row['path']).open('x',encoding='utf-8',newline='\n'))
                   for row in manifest['sources']}
        for identity in sorted(selected):
            row = get(identity)
            raw_body = row['raw_body']
            value = {'id':identity,'title':render_text(row['title']),'body':render_text(raw_body),
                     'upstream_path':row['upstream_path'],'upstream_sha256':row['raw_sha256']}
            streams[row['source_id']].write(json.dumps(value,sort_keys=True,ensure_ascii=True)+'\n')
            counts[row['source_id']] += 1
            body_characters += len(value['body'])
            normalized_bodies += value['body'] != raw_body
            separator_count += sum(raw_body.count(chr(c)) for c in (0x85,0x2028,0x2029))
            inventory.append({'id':identity,'source':row['source_id'],'raw_sha256':row['raw_sha256'],
                              'original_body_sha256':hashlib.sha256(raw_body.encode()).hexdigest(),
                              'rendered_body_sha256':hashlib.sha256(value['body'].encode()).hexdigest()})
    database.close()
    manifest['bundle']['title'] = 'EnterpriseRAG internal full-text 6000-document corpus'
    manifest['bundle']['description'] = 'Fixed reference-enriched full-text corpus for retrospective internal comparison.'
    write_new(incoming/'manifest.json',manifest)
    shutil.copyfile(source/'guidance.md',incoming/'guidance.md')
    shutil.copytree(source/'plans',incoming/'plans')
    write_new(output/'inventory.private.json',inventory)
    summary = {'schema_version':'enterprise-internal-corpus/1.0','status':'prepared-not-sealed',
               'documents':len(selected),'sources':dict(counts),'body_characters':body_characters,
               'rendering':'U+0085, U+2028 and U+2029 rendered as LF; every other character preserved',
               'newline_normalized_bodies':normalized_bodies,'newline_characters_normalized':separator_count,
               'required_aliases_bound_to_pinned_public_path':len(aliases),
               'required_reference_documents':len(references),'prior_context_and_reference_union':len(required),
               'source_minimum':minimum_per_source,'selection_uses_candidate_outcomes':False,
               'uses_previously_exposed_references':True,'all_500_questions_retrospective':True,
               'official_full_corpus_comparable':False,
               'questions_sha256':digest(questions_path),'prior_contexts_sha256':digest(contexts_path),
               'inventory_sha256':digest(output/'inventory.private.json'),
               'input_files':{p.relative_to(incoming).as_posix():digest(p) for p in sorted(incoming.rglob('*')) if p.is_file()}}
    write_new(output/'summary.redacted.json',summary)
    return {k:v for k,v in summary.items() if k != 'input_files'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.output)),flush=True)


if __name__ == '__main__':
    main()
