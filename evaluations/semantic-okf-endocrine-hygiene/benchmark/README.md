# Endocrine-Hygiene Retrieval Benchmark

This benchmark evaluates retrieval over the same fifteen-paper Semantic OKF corpus.
It contains thirty evidence-first questions:

- fifteen direct questions, one for each selected paper;
- ten cross-paper synthesis questions; and
- five hard questions requiring joins, contrasts, exclusions, normalization,
  conditional reasoning, or explicit causal-boundary analysis.

## Evidence-first construction

The hard questions were written only after the relevant BioC passages had been
reviewed and the answers had been derived. Their evaluator-only ground truth records
atomic answer claims, required papers and sources, acceptable variants, explicit
derivation steps, important negatives, failure conditions, and exact authoritative
evidence bindings. Each binding names the normalized Markdown path, a one-based
`BioC-passage-NNNN` locator, and the SHA-256 of the exact BioC passage text.

The frozen hard subset contains 27 atomic answer claims, 15 important negatives,
and 60 question-specific evidence bindings across 34 distinct authoritative
passages. The separate exact-claim ledger contains 128 claim requirement occurrences
across 37 distinct reviewed claim IDs. Repetition is intentional: one reviewed
claim may be required by several answer or negative groups.

Question prompts contain no PMCIDs, source IDs, paths, locators, hashes, or complete
answer claims. A consultation run receives only the `question` value. Qrels and
ground truth remain private to the evaluator.

## Files

- `retrieval-questions.jsonl` is the complete benchmark. Each closed-schema row
  contains `id`, `question`, `question_type`, and `qrels`.
- `hard-questions.jsonl` is the exact hard-question subset with the same row schema.
- `hard-ground-truth.jsonl` stores the reviewed evaluator-only records for the hard
  subset.
- `hard-claim-requirements.json` maps every atomic answer and important negative to
  the exact reviewed claim IDs required for complete credit.
- `benchmark-manifest.json` freezes contracts, counts, paths, row counts, and file
  hashes.

Paper qrels use canonical uppercase PMCIDs such as `PMC6504186`. Source qrels use
the lowercase IDs required by the corpus manifest, such as `paper-pmc6504186` and
`claims-pmc6504186`; every qrel paper contributes both source IDs.

## Exact-claim and evidence-digest join

The exact-claim ledger prevents a passage hash from standing in for a claim. Several
reviewed claim records can legitimately cite the same passage while expressing
different findings, caveats, or normalizations. Passage-only scoring would treat
those interpretations as interchangeable.

For every atomic answer and important negative, validation therefore performs this
closed join:

1. resolve each required claim ID against the 93-row reviewed claim corpus;
2. derive the claim's `(paper_id, evidence_text_sha256)` signature;
3. require that signature to match at least one evidence ID declared by that exact
   answer or negative; and
4. independently resolve the evidence locator and recompute its exact passage-text
   SHA-256 from the authoritative Markdown.

This validates all 128 claim requirement occurrences and all 60 evidence bindings.
It also requires every evidence binding to have at least one reviewed-claim
projection. The join proves identity and declared support; it does not by itself
prove that a generated free-form answer is semantically correct.

## Validation

Run the count-agnostic validator after generating the corpus:

```powershell
python evaluations/semantic-okf-endocrine-hygiene/scripts/validate_ground_truth.py --json
```

The validator applies closed schemas, checks direct-paper coverage and the hard
subset relationship, rejects identity or locator leakage, binds qrels to manifest
sources, verifies every hard-ground-truth reference, validates exact-claim
requirements, and recomputes all cited passage hashes from authoritative corpus
files. The expected compact counts are:

| Item | Count |
| --- | ---: |
| Questions | 30 |
| Direct | 15 |
| Cross-paper | 10 |
| Hard | 5 |
| Hard atomic answer claims | 27 |
| Hard important negatives | 15 |
| Hard evidence bindings | 60 |
| Distinct authoritative passages | 34 |
| Exact reviewed-claim requirement occurrences | 128 |
| Distinct required reviewed claims | 37 |

## Accepted Skill Arena use

The five hard prompts also drive the isolated paired Skill Arena diagnostic. Accepted
eval `eval-v8v-2026-07-15T23:49:40` completed all `10/10` control/treatment cells
with `0` runtime errors and zero compound passes in either profile. Mean score was
`0.657` for the knowledge-only control and `0.543` for the classical consultation
treatment; mean latency was `72.6 s` and `117.6 s`, respectively. Treatment minus
control was therefore `-0.114` score and `+45.0 s` latency.

Component control/treatment pass rates were response format `100%/100%`, response
contract `100%/80%`, evidence validity `40%/20%`, exact reviewed-claim fidelity
`100%/100%`, atomic answer completeness `20%/0%`, important-negative coverage
`20%/0%`, and required-paper coverage `80%/80%`.

With one request per cell, these are descriptive paired results only. They provide
no evidence of treatment improvement and show that the strict evidence and complete
claim-set requirements remain the bottleneck even when claim wording is exact. See
the [compact accepted report](../reports/skill-arena-hard5-diagnostic.md) and
[machine-readable result](../reports/skill-arena-hard5-diagnostic.json) for binding
metadata, per-question cells, and actual Q030 answers.
