"""Measure corpus-only native construction resources before study sealing.

No query, answer, relevance annotation, candidate ranking or model judge is read.
The small build is a capacity probe and supplies no retrieval-quality evidence.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import time
import zlib

from dataset import digest, write_new

REPO = Path(__file__).resolve().parents[2]
IMAGE = 'sha256:bcd2b2b57b968ff8b4976bedf8c5ddf7b7e2ff41c341f7a13a05ae4df2ffc9d8'


def linux(path: Path) -> str:
    path = path.resolve()
    return '/mnt/'+path.drive[0].lower()+path.as_posix()[2:]


def prepare(work: Path, count: int) -> dict:
    """Select corpus rows by a query-independent, fixed identity hash."""
    if not 100 <= count <= 20000:
        raise ValueError('Capacity probes admit 100 through 20000 records')
    work.mkdir(parents=True, exist_ok=False)
    original = REPO/'tmp/enterprise-classical-full-20260908/full-index/index'
    database = sqlite3.connect((original/'documents.sqlite').as_uri()+'?mode=ro&immutable=1', uri=True)
    with database:
        identities = database.execute('SELECT number, document_id FROM documents').fetchall()
        chosen = sorted(identities, key=lambda row: hashlib.sha256(
            ('e7-corpus-capacity-v1\0'+row[1]).encode()).hexdigest())[:count]
        source = work/'input'
        (source/'documents').mkdir(parents=True)
        prior = REPO/'tmp/enterprise-g2-replay/input'
        manifest = json.loads((prior/'manifest.json').read_text(encoding='utf-8'))
        sources = {}
        characters = 0
        with ExitStack() as stack:
            files = {row['id']: stack.enter_context((source/row['path']).open('x', encoding='utf-8', newline='\n'))
                     for row in manifest['sources']}
            for number, identity in sorted(chosen, key=lambda row: row[1]):
                payload = database.execute('SELECT payload FROM documents WHERE number=?', (number,)).fetchone()[0]
                row = json.loads(zlib.decompress(payload))
                body = row['raw_body']
                value = {'id': row['upstream_id'], 'title': row['title'], 'body': body,
                         'upstream_path': row['upstream_path'], 'upstream_sha256': row['raw_sha256']}
                # Native JSONL readers split Unicode line boundaries. Escaping
                # preserves exact decoded text without creating physical rows.
                files[row['source_id']].write(json.dumps(value, ensure_ascii=True, sort_keys=True)+'\n')
                characters += len(body)
                sources[row['source_id']] = sources.get(row['source_id'], 0)+1
        write_new(source/'manifest.json', manifest)
        shutil.copyfile(prior/'guidance.md', source/'guidance.md')
        shutil.copytree(prior/'plans', source/'plans')
    database.close()
    tools = work/'tool'
    tools.mkdir()
    for name in ('compare_generator_versions.py', 'fulltext_projection.py'):
        shutil.copyfile(REPO/'evaluations/enterprise-rag-bench'/name, tools/name)
    summary = {'purpose': 'Corpus-only construction capacity; no retrieval fitness',
               'documents': count, 'body_characters': characters, 'sources': sources,
               'index_metadata_sha256': digest(original/'index.json'),
               'image': IMAGE, 'cpu_limit': 4, 'memory_limit_gib': 12,
               'input_files': {path.relative_to(source).as_posix(): digest(path)
                               for path in sorted(source.rglob('*')) if path.is_file()}}
    write_new(work/'capacity-input.json', summary)
    return summary


def build(work: Path, family: str) -> dict:
    """Use the unchanged generator in an offline, resource-limited container."""
    output = work/'runs'/family
    output.mkdir(parents=True, exist_ok=False)
    argv = ['wsl', '-d', 'Ubuntu', '--exec', 'docker', 'run', '--rm', '--network=none',
            '--cpus=4', '--memory=12g', '--memory-swap=12g',
            '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'PYTHONUTF8=1',
            '-e', 'HF_HUB_CACHE=/models/huggingface/hub', '-e', 'HF_HUB_OFFLINE=1',
            '-e', 'TRANSFORMERS_OFFLINE=1', '-e', 'OMP_NUM_THREADS=4', '-e', 'MKL_NUM_THREADS=4']
    for host, target, readonly in ((work/'input','/input',True), (work/'tool','/tool',True),
                                   (REPO/'skills/build-semantic-okf-knowledge-skill','/generator',True),
                                   (REPO/'tmp/e5/models/hub','/models/huggingface/hub',True),
                                   (output,'/out',False)):
        argv += ['--mount', 'type=bind,source='+linux(host)+',target='+target+(',readonly' if readonly else '')]
    command = ['python', '-B', '/tool/compare_generator_versions.py', 'build', '--family', family,
               '--input', '/input', '--generator', '/generator', '--expert', '/out/capacity-expert',
               '--output', '/out/build.json']
    if family not in ('legacy','turso','graphify'):
        command += ['--plan', '/input/plans/'+family+'.json']
    # The wrapper records child peak RSS even when construction fails. It does
    # not reinterpret a failed build as a completed knowledge artifact.
    wrapper = ('import json,resource,subprocess,sys,time; start=time.monotonic(); '
               'result=subprocess.run(sys.argv[1:]); '
               'json.dump(dict(exit_code=result.returncode,seconds=time.monotonic()-start,'
               'peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss),'
               'open("/out/resources.json","x")); sys.exit(result.returncode)')
    argv += [IMAGE, 'python', '-B', '-c', wrapper, *command]
    started = time.monotonic()
    with (output/'execution.log').open('xb') as stream:
        result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT, timeout=3900)
    summary = {'family':family, 'exit_code':result.returncode, 'wall_seconds':time.monotonic()-started,
               'retrieval_queries':0, 'retrieval_quality_measured':False}
    if (output/'resources.json').exists():
        summary['resources'] = json.loads((output/'resources.json').read_text())
    if (output/'build.json').exists():
        receipt = json.loads((output/'build.json').read_text())
        summary['status'] = receipt['status']
        summary['source_fidelity'] = receipt['source_fidelity']
    write_new(output/'execution.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', required=True, type=Path)
    parser.add_argument('--count', type=int, default=2000)
    parser.add_argument('--family', choices=('legacy','embeddings','classical','adaptive','entity-graph','ensemble','graphify','turso'))
    args = parser.parse_args()
    print(json.dumps(build(args.work, args.family) if args.family else prepare(args.work,args.count)), flush=True)


if __name__ == '__main__':
    main()
