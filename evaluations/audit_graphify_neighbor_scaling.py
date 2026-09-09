"""Compare an isolated neighbor-selection prototype with the exact source function.

Only synthetic records are accepted. This is a host microbenchmark, not a skill
candidate, Harbor job, retrieval evaluation, or permission to modify a sealed
builder. Source extraction uses a closed set of AST definitions without importing
the builder or executing its module entrypoints.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import random
import re
import statistics
import time
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ('skills/build-semantic-okf-knowledge-skill/assets/families/'
                 'graphify/builder/scripts/_graphify_projection.py')


def load_functions(source=SOURCE, *, neighbors=1):
    """Load the source function and a bounded-neighbor prototype in isolation."""
    if not isinstance(neighbors, int) or isinstance(neighbors, bool) or neighbors < 1:
        raise ValueError('neighbors must be a positive integer')
    text = source.read_text(encoding='utf-8')
    module = ast.parse(text)
    names = ('_record_tokens', '_lexical_similarity_pairs')
    nodes = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if [node.name for node in nodes] != list(names):
        raise ValueError('source definitions changed')
    namespace = dict(math=math, PurePosixPath=PurePosixPath, Mapping=Mapping,
                     Iterable=Iterable, Any=Any, LEXICAL_NEIGHBORS=neighbors,
                     LEXICAL_TOKEN_RE=re.compile(r'\w+', re.UNICODE))
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), namespace)
    function = ast.get_source_segment(text, nodes[1])
    start = function.index('    scores: dict[tuple[int, int], float] = {}')
    # Preserve exact feature extraction, IDF and norm calculation. Replace only
    # score storage, endpoint selection and the equivalent mutual-edge output.
    replacement = '''    best: list[list[tuple[float, int]]] = [[] for _ in rows]
    bridge_partitions = len({row[2] for row in rows}) > 1

    def retain(index, score, neighbor):
        item = (score, neighbor)
        key = (-score, rows[neighbor][0])
        selected = best[index]
        if len(selected) == LEXICAL_NEIGHBORS:
            last_score, last_neighbor = selected[-1]
            if key >= (-last_score, rows[last_neighbor][0]):
                return
        selected.append(item)
        selected.sort(key=lambda value: (-value[0], rows[value[1]][0]))
        del selected[LEXICAL_NEIGHBORS:]

    for left in range(total):
        for right in range(left + 1, total):
            if bridge_partitions and rows[left][2] == rows[right][2]:
                continue
            common = rows[left][1] & rows[right][1]
            if not common or not norms[left] or not norms[right]:
                continue
            score = sum(weights[token] ** 2 for token in common) / (norms[left] * norms[right])
            if score > 0:
                retain(left, score, right)
                retain(right, score, left)
    directed = {(left, right): score for left, items in enumerate(best)
                for score, right in items}
    selected = [(left, right) for left, right in directed
                if left < right and (right, left) in directed]
    return [(rows[left][0], rows[right][0], round(directed[(left, right)], 12))
            for left, right in sorted(selected, key=lambda pair: (rows[pair[0]][0], rows[pair[1]][0]))]
'''
    prototype_source = function[:start] + replacement
    alternate = dict(namespace)
    exec(compile(prototype_source, '<synthetic-neighbor-prototype>', 'exec'), alternate)
    return namespace['_lexical_similarity_pairs'], alternate['_lexical_similarity_pairs'], {
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'original_function_sha256': hashlib.sha256(function.encode()).hexdigest(),
        'prototype_function_sha256': hashlib.sha256(prototype_source.encode()).hexdigest(),
    }


def synthetic_records(count, seed, *, partitions=7, dense=True):
    """Create content-free generated fixtures with exact identities and tie cases."""
    rng = random.Random(seed)
    result = []
    for index in range(count):
        words = [f'term{rng.randrange(60)}' for _ in range(rng.randrange(0, 16))]
        result.append({
            'concept_path': f'concepts/{index:06d}.md',
            'record_id': f'root/p{index % partitions}/r{index:06d}',
            'title': 'shared synthetic fixture' if dense else f'unique{index}',
            'concept_type': 'document' if dense else '',
            'body': ' '.join(words),
        })
    return result


def benchmark(sizes, repeats):
    """Check output equality before reporting paired host-only function timings."""
    original, prototype, bindings = load_functions()
    rows = []
    for count in sizes:
        records = synthetic_records(count, 60109)
        durations = {'original': [], 'prototype': []}
        hashes = set()
        for repeat in range(repeats):
            functions = [('original', original), ('prototype', prototype)]
            if repeat % 2:
                functions.reverse()
            results = {}
            for name, function in functions:
                started = time.perf_counter()
                results[name] = function(records)
                durations[name].append(time.perf_counter() - started)
            if results['original'] != results['prototype']:
                raise ValueError('prototype changed an edge, endpoint, order or score')
            hashes.add(hashlib.sha256(json.dumps(results['original'], separators=(',', ':')).encode()).hexdigest())
        if len(hashes) != 1:
            raise ValueError('source outputs changed across repeats')
        medians = {name: statistics.median(values) for name, values in durations.items()}
        rows.append({'records': count, 'repeats': repeats, 'durations_seconds': durations,
                     'median_seconds': medians, 'ratio_original_to_prototype': medians['original'] / medians['prototype'],
                     'identical_edges': len(results['original']), 'output_sha256': hashes.pop(),
                     'original_dense_score_slots': count * (count - 1) // 2,
                     'original_dense_endpoint_checks': count * count * (count - 1) // 2,
                     'prototype_retained_neighbor_bound': count})
    return {'schema': 'graphify-synthetic-neighbor-scaling/1.0', 'bindings': bindings,
            'rows': rows, 'synthetic_only': True, 'source_modified': False,
            'native_trials': 0, 'candidate_bundles': 0, 'retrieval_quality_measured': False,
            'limits': 'One host, synthetic short records, isolated function only. No full-build speed or native quality claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sizes', nargs='+', type=int, default=[100, 200, 400, 800])
    parser.add_argument('--repeats', type=int, default=3)
    args = parser.parse_args()
    if args.output.exists() or any(n < 2 or n > 1024 for n in args.sizes) or not 1 <= args.repeats <= 5:
        parser.error('use a fresh output, sizes 2..1024 and repeats 1..5')
    result = benchmark(args.sizes, args.repeats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'output': str(args.output), 'rows': len(result['rows']), 'native_trials': 0}))


if __name__ == '__main__':
    main()
