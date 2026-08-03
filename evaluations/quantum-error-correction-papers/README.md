# Quantum Error Correction Paper Evaluation

This evaluation tests whether a retrieval technique learned on earlier
knowledge domains can transfer to new source bytes and a different technical
domain. It freezes fifteen exact arXiv paper versions, builds one immutable
Semantic OKF snapshot, defines forty reviewed retrieval questions, and compares
two standalone expert skills.

The study is retrospective. Every question and qrel is exposed to the
supervised profile, no untouched holdout exists, and no artifact from this
study is promotion-eligible.

## Corpus

The corpus covers four complementary areas:

- surface-code architecture, biased-noise variants, and experimental scaling;
- belief-propagation, ordered-statistics, guided-decimation, and learned
  decoders;
- qLDPC construction milestones and explicit quantum Tanner code instances;
  and
- binomial, cat, and Gottesman-Kitaev-Preskill bosonic codes.

[`paper-selection.json`](paper-selection.json) is the authority for all fifteen
versioned IDs, expected titles, and selection dimensions. The acquisition
script verifies each official arXiv abstract page, downloads or reuses the
exact versioned PDF, records its digest, extracts text by PDF page, normalizes
it to NFC to match the Semantic OKF ledger, and binds every generated file in
[`sources/inventory.json`](sources/inventory.json).

```bash
python evaluations/quantum-error-correction-papers/scripts/acquire_papers.py \
  --check
```

`--refresh` rebuilds metadata and Markdown from the already accepted local
PDFs. It is an explicit source-tree replacement operation; use it only when the
acquisition implementation changes, then rebuild all downstream artifacts.

## Benchmark contract

[`benchmark/benchmark-blueprint.json`](benchmark/benchmark-blueprint.json)
defines thirty development questions and ten evidence-first hard questions.
Each question has a non-exhaustive paper focus set, minimum document count,
required semantic points, and, where applicable, important negatives.

The deterministic generator owns the source manifest, questions, hard truth,
cohorts, evaluation crosswalk, five plan-backed family plans, and expert
guidance.

```bash
python evaluations/quantum-error-correction-papers/scripts/generate_benchmark.py \
  --check
```

The checked bundle at [`bundle/`](bundle/) contains fifteen records and passes
the OKF, SHACL, and Semantic OKF validators. A fresh second build produced the
same twenty-five regular files byte for byte.

## Harbor isolation

The dataset descriptor is
[`quantum-error-correction-papers-40.json`](../semantic-okf-datasets/datasets/quantum-error-correction-papers-40.json).
It registers all eight build/consult skill pairs even though this transfer
study exercises the legacy pair.

Both execution modes were regenerated and validated:

- `build-consult` exposes only evaluator-free raw Markdown at `/dataset`; and
- `consult-only` exposes only the exact processed snapshot at `/knowledge`.

The two task trees pass deterministic regeneration, leakage checks, and all
eighty mechanical qualification oracles. Redacted dry runs were inspected on
Windows. No live Harbor model campaign was run because live execution is
restricted to Linux or WSL.

## Builder transfer treatment

The default treatment uses `build-specialized-skill` with its ordinary lexical
helper. The candidate uses the same builder and immutable snapshot with:

```bash
--retrieval-profile retrospective-supervised-ngram
--profile-dataset-id quantum-error-correction-papers-40
--profile-questions evaluations/quantum-error-correction-papers/benchmark/retrieval-questions.jsonl
--profile-qrel-key paper_ids
--profile-identity-mode arxiv-id
--acknowledge-exposed-qrels
```

The candidate embeds no exact question lookup or answers. It stores
one-to-five-token routing features, binds the exact question and ledger
digests, uses an authoritative lexical fallback, deduplicates exact versioned
arXiv identities, and returns only immutable ledger records.

## Results

The complete machine-readable evidence is in
[`retrospective-supervised-expert-evaluation.json`](reports/retrospective-supervised-expert-evaluation.json);
the concise audit is
[`retrospective-supervised-expert-evaluation.md`](reports/retrospective-supervised-expert-evaluation.md).

| Rank | Treatment | Recall@10 | MRR@10 | nDCG@10 | Exact evidence | Representative P95 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Retrospective supervised n-gram | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 34.006 ms |
| 2 | Default lexical baseline | 74.5833% | 27.4018% | 36.6713% | 100.0000% | 123.550 ms |

The candidate repeated the 100% quality and exact-evidence result in all three
all-question replicates. This establishes fixed-workload retrieval transfer,
not semantic answer correctness or unseen-query generalization.

The candidate also passes the native Harbor retrieval grader on one
development case and one evidence-first hard case, including manifest binding,
ten-result qualification, canonical arXiv deduplication, exact ledger evidence,
and perfect per-case Recall, MRR, and nDCG. The machine-readable smoke evidence
is in
[`native-harbor-retrieval-smoke.json`](reports/native-harbor-retrieval-smoke.json).
This two-case compatibility smoke does not replace the replicated all-forty
evaluation above.

## Reproduce the expert comparison

Build the two experts into distinct new directories, validate each package,
and repeat each build with `--check`. Then run:

```bash
python evaluations/quantum-error-correction-papers/scripts/evaluate_expert_retrieval.py \
  --baseline PATH_TO_DEFAULT_EXPERT \
  --candidate PATH_TO_SUPERVISED_EXPERT \
  --questions evaluations/quantum-error-correction-papers/benchmark/retrieval-questions.jsonl \
  --output-json evaluations/quantum-error-correction-papers/reports/retrospective-supervised-expert-evaluation.json \
  --output-markdown evaluations/quantum-error-correction-papers/reports/retrospective-supervised-expert-evaluation.md \
  --replicates 3 --top-k 10 --p95-limit-ms 250

python evaluations/quantum-error-correction-papers/scripts/validate_native_harbor_retrieval.py \
  --expert PATH_TO_SUPERVISED_EXPERT \
  --output evaluations/quantum-error-correction-papers/reports/native-harbor-retrieval-smoke.json
```

Latency is operational and will vary by host. The gate requires every
replicate to retain perfect Top-10 quality and exact evidence, strictly improve
at least one quality metric over the same-snapshot baseline, and remain below
the declared P95 ceiling.
