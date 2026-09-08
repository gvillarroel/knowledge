"""Sample Enterprise development questions without consulting measured outcomes.

The public workload has already been evaluated. These blocks are development
partitions of one source family, not newly independent validation datasets.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import secrets


QUOTAS = {
    'basic': 24, 'semantic': 32, 'completeness': 12, 'project_related': 12,
    'intra_document_reasoning': 12, 'constrained': 8, 'conflicting_info': 4,
    'miscellaneous': 8, 'info_not_found': 4, 'high_level': 4,
}
BLOCKS = 4


def digest(path: Path) -> str:
    """Hash one immutable source file without displaying its contents."""
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def priority(seed: str, value: str) -> str:
    """Provide an order-independent, domain-separated sampling priority."""
    return hashlib.sha256(('enterprise-development-v1\0'+seed+'\0'+value).encode()).hexdigest()


def evidence_band(row: dict) -> str:
    """Stratify by declared reference count, without using answer or score text."""
    count = len(set(row['expected_doc_ids']))
    return 'none' if not count else 'one' if count == 1 else 'two-three' if count <= 3 else 'four-plus'


def stratified_sample(rows: list[dict], seed: str, quotas: dict[str, int] = QUOTAS) -> list[dict]:
    """Sample uniformly within each category; audit application coverage later.

    Application signatures and evidence bands are overlapping audit groups,
    not extra selection quotas. This keeps each question's inclusion
    probability exactly category_sample/category_population.
    """
    if len(seed) != 64 or any(c not in '0123456789abcdef' for c in seed):
        raise ValueError('The frozen sampling seed must contain 32 bytes of lowercase hexadecimal')
    identities = [row['question_id'] for row in rows]
    if len(set(identities)) != len(identities):
        raise ValueError('Question identities must be unique')
    categories = defaultdict(list)
    for row in rows:
        categories[row['question_type']].append(row)
    if set(categories) != set(quotas):
        raise ValueError('The declared category inventory changed')
    selected = []
    for category, count in sorted(quotas.items()):
        pool = categories[category]
        if count <= 0 or count % BLOCKS or count > len(pool):
            raise ValueError('Category quotas must fit the population and all balanced blocks')
        chosen = sorted(pool, key=lambda row: priority(seed, row['question_id']))[:count]
        chosen.sort(key=lambda row: priority(seed, 'block\0'+row['question_id']))
        for offset, row in enumerate(chosen):
            selected.append({**row, 'development_block': offset % BLOCKS,
                             'category_population': len(pool), 'category_sample': count,
                             'inclusion_probability': count/len(pool),
                             'population_to_sample_weight': len(pool)/count})
    return sorted(selected, key=lambda row: row['question_id'])


def write_new(path: Path, value) -> None:
    """Preserve a new artifact with canonical JSON and explicit line endings."""
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def prepare(questions: Path, output: Path, frozen_seed: Path | None = None) -> dict:
    """Create private replayable selection and scorer-free query blocks."""
    rows = [json.loads(line) for line in questions.read_text(encoding='utf-8').splitlines() if line.strip()]
    if len(rows) != 500 or sum(bool(row['expected_doc_ids']) for row in rows) != 470:
        raise ValueError('The pinned public 500-question population changed')
    output.mkdir(parents=True, exist_ok=False)
    seed = (json.loads(frozen_seed.read_text(encoding='utf-8'))['seed']
            if frozen_seed else secrets.token_hex(32))
    selected = stratified_sample(rows, seed)
    write_new(output/'private-sampling-seed.json', {'seed': seed})
    write_new(output/'selected.private.json', selected)
    for block in range(BLOCKS):
        subset = [row for row in selected if row['development_block'] == block]
        write_new(output/f'queries-block-{block:02d}.json',
                  [{'id': row['question_id'], 'question': row['question']} for row in subset])
    population_sources = Counter(source for row in rows for source in set(row['source_types']))
    selected_sources = Counter(source for row in selected for source in set(row['source_types']))
    if set(selected_sources) != set(population_sources):
        raise ValueError('The realized sample misses an application represented in the population')
    summary = {
        'schema_version': 'enterprise-stratified-development/2.0',
        'status': 'prepared-not-sealed', 'questions_sha256': digest(questions),
        'selection_sha256': digest(output/'selected.private.json'),
        'seed_commitment_sha256': hashlib.sha256(seed.encode()).hexdigest(),
        'population_questions': 500, 'population_reference_questions': 470,
        'development_questions': len(selected),
        'development_reference_questions': sum(bool(row['expected_doc_ids']) for row in selected),
        'blocks': BLOCKS, 'category_quotas': QUOTAS,
        'population_categories': dict(Counter(row['question_type'] for row in rows)),
        'population_source_occurrences': dict(population_sources),
        'selected_source_occurrences': dict(selected_sources),
        'selected_evidence_bands': dict(Counter(evidence_band(row) for row in selected)),
        'sampling_design': 'Simple random sampling without replacement within mutually exclusive question categories',
        'secondary_groups': 'Application signatures and evidence cardinality are coverage audits only; no rejection resampling',
        'selection_uses_measured_outcomes': False,
        'selection_uses_answers_or_fact_text': False,
        'weighting': 'Within-category sample means, weighted by original reference-bearing category sizes; N_h/n_h per observation',
        'development_independence_groups': 1,
        'final_public_workload_claim': 'Retrospective; all 500 questions have prior evaluation exposure',
        'validation': 'External independently curated source families; not provided by this sampler',
    }
    write_new(output/'summary.redacted.json', summary)
    if stratified_sample(list(reversed(rows)), seed) != selected:
        raise ValueError('Sampling changed under source enumeration reversal')
    return summary


def main() -> None:
    """Prepare one new development selection from explicit local source bytes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--questions', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--frozen-seed', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.questions, args.output, args.frozen_seed), sort_keys=True))


if __name__ == '__main__':
    main()
