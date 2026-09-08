"""Create offline native tasks from a qualified, evaluator-free Enterprise input."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from prepare import (REPO, WORK, NAME, FAMILIES, MODES, PRIMARY, IMAGE, IMAGE_TAG,
                     tree, read, write, sha, posix, linux, command)


def imported_modules(family, skill_files):
    modules = {'legacy':[], 'turso':['_turso_read'], 'embeddings':['_embedding_snapshot'],
               'classical':['_classical_snapshot'], 'adaptive':['_adaptive_snapshot'],
               'entity-graph':['_entity_graph_model','_entity_graph_snapshot'],
               'ensemble':['_entity_graph_model','_adaptive_snapshot','_embedding_snapshot',
                           '_entity_graph_snapshot','_ensemble_snapshot'],
               'graphify':['_graphify_snapshot']}[family]
    return {f'assets/families/{family}/consultant/scripts/{name}.py':
            skill_files[f'assets/families/{family}/consultant/scripts/{name}.py'] for name in modules}


def make_image(name, dataset):
    """Build an offline task image containing declared inputs and four helpers."""
    if linux(['docker','image','inspect',IMAGE_TAG,'--format','{{.Id}}']) != IMAGE:
        raise ValueError('Base runtime tag drift')
    context = WORK/'image-contexts'/name
    context.mkdir(parents=True,exist_ok=False)
    shutil.copytree(dataset,context/'dataset')
    (context/'runtime').mkdir()
    for filename in ('bridge.py','prepare_strategy_bundles.py','evaluate_all_routes.py','legacy_comparator.py'):
        shutil.copyfile(WORK/'runtime'/filename,context/'runtime'/filename)
    (context/'Dockerfile').write_text(
        f'FROM {IMAGE_TAG}\nCOPY runtime/ /opt/knowledge/evolution/runtime/\n'
        'COPY dataset/ /dataset/\nRUN chmod -R a-w /dataset\n'
        'ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 '
        'HF_HUB_CACHE=/models/huggingface/hub OMP_NUM_THREADS=2 MKL_NUM_THREADS=2\nWORKDIR /workspace\n',
        encoding='utf-8',newline='\n')
    tag = 'knowledge-enterprise-stratified:e7-'+name
    command(['wsl','-d','Ubuntu','--exec','docker','build','--pull=false','--network=none','-t',tag,posix(context)],
            WORK/'logs'/('image-'+name+'.log'))
    image = linux(['docker','image','inspect',tag,'--format','{{.Id}}'])
    if linux(['docker','image','inspect',IMAGE_TAG,'--format','{{.Id}}']) != IMAGE:
        raise ValueError('Base runtime changed during construction')
    return image


def write_task(task, family, image, oracle, output_path):
    """Place labels only in separate-container tests and task-free instructions."""
    (task/'tests/runtime/support').mkdir(parents=True,exist_ok=False)
    (task/'environment').mkdir()
    instruction = {'family':family,'output_path':output_path,
        'instruction':'Build and independently validate the staged family from /dataset/input, reproduce its complete knowledge, and rank every request in /dataset/queries.json at Top-10 with exact authoritative identities. Write the declared structured result.'}
    (task/'instruction.md').write_text(json.dumps(instruction,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    (task/'task.toml').write_text(f'''schema_version = "1.3"
artifacts = [{{ source = "{output_path}", destination = "response.json" }}]
[metadata]
capability = "source-grounded-retrieval"
resource_class = "cpu-two-threads"
[agent]
timeout_sec = 3600.0
network_mode = "public"
[verifier]
timeout_sec = 180.0
environment_mode = "separate"
network_mode = "public"
[verifier.environment]
docker_image = "{IMAGE}"
os = "linux"
network_mode = "public"
cpus = 2
memory_mb = 2048
[environment]
docker_image = "{image}"
os = "linux"
network_mode = "public"
cpus = 2
memory_mb = 6144
storage_mb = 24576
workdir = "/workspace"
''',encoding='utf-8',newline='\n')
    compose = 'services:\n  main:\n    network_mode: none\n'
    (task/'environment/docker-compose.yaml').write_text(compose,encoding='utf-8',newline='\n')
    (task/'tests/docker-compose.yaml').write_text(compose+'    volumes:\n      - type: bind\n        source: .\n        target: /tests\n        read_only: true\n',encoding='utf-8',newline='\n')
    files = tree(WORK/'baseline'/NAME)
    contract = {**oracle,'family':family,'routes':MODES[family],'primary_route':PRIMARY[family],
                'output_path':output_path,'verifier_output_path':output_path,
                'skill_files':files,'imported_candidate_modules':imported_modules(family,files),
                'mutable_skill_paths':['assets/retrieval-profile.json']}
    write(task/'tests/contract.json',contract)
    shutil.copyfile(WORK/'runtime/verifier.py',task/'tests/verifier.py')
    shutil.copyfile(WORK/'runtime/evaluate_all_routes.py',task/'tests/runtime/support/evaluate_all_routes.py')
    (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\n'
        'python -B -c \'from pathlib import Path; assert sorted(p.name for p in Path("/sys/class/net").iterdir()) == ["lo"]\'\n'
        'python -B /tests/verifier.py --scoring /tests/runtime/support/evaluate_all_routes.py\n',encoding='utf-8',newline='\n')


def prepare():
    capacity = WORK/'native-oracle'
    if read(capacity/'qualification.json')['status'] != 'pass':
        raise ValueError('Qualified canonical source construction is required')
    ledger = capacity/'knowledge/semantic/records.jsonl'
    records = {row['record_id']:row for line in ledger.read_text(encoding='utf-8').split('\n') if line.strip()
               for row in [json.loads(line)]}
    if len(records) != 6000:
        raise ValueError('Canonical evidence inventory changed')
    identities = {key:{field:row[field] for field in ('record_id','record_sha256','source_id','concept_id','concept_path')}
                  for key,row in records.items()}
    selected = read(WORK/'development-selection-v2/selected.private.json')
    population = [json.loads(line) for line in (REPO/'evaluations/enterprise-rag-bench/raw/questions.jsonl').read_text(encoding='utf-8').splitlines()]
    if any(bool(q['expected_doc_ids']) == (q['question_type'] in ('high_level','info_not_found')) for q in population):
        raise ValueError('Category-wide retrieval eligibility condition changed')
    if sum(q['population_to_sample_weight'] for q in selected if q['expected_doc_ids']) != 470:
        raise ValueError('Frozen reference-population weights changed')
    write(WORK/'sampling-audit.json',{'status':'pass','eligible_weight_sum':470,
        'development_questions':120,'eligible_development_questions':112,
        'no_reference_categories':{'high_level':10,'info_not_found':20},
        'estimator':'Eight eligible category sample means weighted by their population sizes / 470; exactly equal to the implemented normalized inverse-inclusion weighted mean.',
        'selection_sha256':sha(WORK/'development-selection-v2/selected.private.json')})
    metadata = {}
    for phase, questions in (('development',selected),('recalculation',population)):
        dataset = WORK/'agent-inputs'/phase
        (dataset/'input/documents').mkdir(parents=True,exist_ok=False)
        shutil.copyfile(WORK/'corpus/input/manifest.json',dataset/'input/manifest.json')
        for path in sorted((WORK/'corpus/input/documents').glob('*.jsonl')):
            shutil.copyfile(path,dataset/'input/documents'/path.name)
        ordered = sorted(questions,key=lambda q:q['question_id'])
        public = [{'id':q['question_id'],'question':q['question']} for q in ordered]
        write(dataset/'queries.json',public)
        queries = [{'id':q['question_id'],'question':q['question'],'relevant':sorted(set(q['expected_doc_ids'])),
                    'category':q['question_type'],'weight':q.get('population_to_sample_weight',1.0),
                    'block':q.get('development_block')} for q in ordered]
        if any(not set(q['relevant']).issubset(records) for q in queries):
            raise ValueError('Unresolved original qrels')
        oracle = {'questions':queries,'record_identities':identities,
                  'records':{key:row['record_sha256'] for key,row in records.items()},
                  'source_binding':tree(dataset)}
        image = make_image(phase,dataset)
        for family in FAMILIES:
            key = hashlib.sha256(('e7\0'+phase+'\0'+family).encode()).hexdigest()[:20]
            task = WORK/'tasks/development'/('retrieval-'+key)
            output = '/workspace/result-'+key[:8]+'/ranking.json'
            write_task(task,family,image,oracle,output)
            metadata[phase+':'+family] = {'task':posix(task),'image':image,'family':family,
                                         'phase':phase,'source_group':'enterprise-public-exposed'}
        print(json.dumps({'phase':phase,'tasks':8,'queries_per_task':len(queries),'documents':6000}),flush=True)
    write(WORK/'development-task-map.json',metadata)


if __name__ == '__main__':
    prepare()
