# Software Architecture Books Private Evaluation

This study builds a deterministic, page-addressable Semantic OKF snapshot from
the eighteen PDFs supplied by the user and evaluates classical retrieval on
forty reviewed questions.

The books are commercial, private, and marked against redistribution. Raw
PDFs, extracted text, bundles, generated Harbor tasks, and execution results
therefore remain in the repository's ignored `raw/`, `processed/`,
`generated/`, and `results/` directories. The checked files contain only
source hashes and metadata, reproducible scripts, paraphrased questions and
adjudications, hash-only evidence locators, aggregate metrics, and
documentation.

## Corpus contract

[`book-selection.json`](book-selection.json) pins every filename, byte count,
PDF page count, title, author, and SHA-256. The accepted corpus contains:

- 18 separate logical book sources;
- 6,170 PDF pages;
- 133,882,359 raw PDF bytes; and
- 12,271,467 extracted characters after NFC/LF normalization and removal of
  the repeated distribution watermark.

Stage the exact private PDFs under `raw/pdfs/`, then create and independently
regenerate the derived corpus:

```bash
python evaluations/software-architecture-books/scripts/prepare_corpus.py
python evaluations/software-architecture-books/scripts/prepare_corpus.py --check
```

The preparation script rejects extra or missing files, symlinks, byte or hash
drift, metadata drift, page-count drift, failed empty-password decryption, and
suspiciously incomplete text extraction. It writes one Markdown record per
book with stable `## PDF page N` evidence boundaries.

## Semantic OKF snapshot

[`manifest.json`](manifest.json) keeps all eighteen authorities separate in one
atomic bundle. [`source-combination.json`](source-combination.json) records the
source-scoped identity policy and the document crosswalk.

Build and validate the model-free classical projection:

```bash
python skills/build-semantic-okf-classical/scripts/runtime_smoke.py
python skills/build-semantic-okf-classical/scripts/build_semantic_okf_classical.py \
  evaluations/software-architecture-books/manifest.json \
  evaluations/software-architecture-books/plans/classical-plan.json \
  evaluations/software-architecture-books/processed/bundle \
  --output-format json
python skills/build-semantic-okf-classical/scripts/validate_semantic_okf_classical.py \
  evaluations/software-architecture-books/processed/bundle \
  --output-format json
python skills/consult-semantic-okf-classical/scripts/query_semantic_okf_classical.py \
  evaluations/software-architecture-books/processed/bundle \
  inspect --deep-validation
```

The accepted snapshot contains 18 authoritative records, 6,170 exact page
passages, 712,289 lexical terms, 6,000 bounded PPMI association rows, and 24
deterministic topic communities. Validation and independent deep rederivation
pass without warnings. A clean second build produced the same 34 regular files
byte for byte.

## Benchmark

[`retrieval-questions.jsonl`](benchmark/retrieval-questions.jsonl) contains
thirty development questions and ten hard synthesis questions. Qrels are
reviewed, non-exhaustive book focus sets. The hard cohort is backed by 28
question-specific evidence bindings over 23 distinct exact book pages.
[`evaluation-contract.json`](benchmark/evaluation-contract.json) freezes the
input hashes, Top-10 source identity contract, route set, metric order, and
qrel-blind policy used before ranking.

[`hard-ground-truth-blueprint.json`](benchmark/hard-ground-truth-blueprint.json)
contains only paraphrased interpretations and answer requirements. The freezer
resolves those reviewed pages against the private corpus and produces
[`hard-ground-truth.jsonl`](benchmark/hard-ground-truth.jsonl) with exact
character offsets and SHA-256 identities, but no book excerpts:

```bash
python evaluations/software-architecture-books/scripts/freeze_benchmark.py
python evaluations/software-architecture-books/scripts/freeze_benchmark.py --check
```

## Direct retrieval evaluation

The direct comparison uses one immutable snapshot, the same Top-10 cutoff, and
four frozen routes: `bm25`, `topic`, `association`, and `fusion`. Metrics use
the first returned page for each distinct book so repeated pages cannot inflate
Recall, MRR, nDCG, precision, or full-qrel coverage. Reviewed-locator recall is
a stricter diagnostic over the exact hard-question pages.

Run:

```bash
python evaluations/software-architecture-books/scripts/evaluate_retrieval.py
```

The concise metric-only result is
[`direct-retrieval-evaluation.md`](reports/direct-retrieval-evaluation.md).
Its JSON companion contains aggregate and per-question book identities,
locators, and hashes while deliberately excluding all private passage text.
The evaluation measures retrieval, not generated-answer quality.

| Rank | Route | Recall@10 | nDCG@10 | Full qrel coverage | Reviewed locator recall | P95 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Fusion | 97.29% | 92.58% | 92.50% | 6.67% | 1,863.9 ms |
| 2 | Association | 97.29% | 92.56% | 92.50% | 6.67% | 1,901.4 ms |
| 3 | Topic | 97.29% | 92.56% | 92.50% | 6.67% | 1,902.3 ms |
| 4 | BM25 | 83.75% | 81.39% | 65.00% | 16.67% | 1,815.4 ms |

Fusion, association, and topic are effectively tied on source discovery;
fusion wins the frozen ordering by a small nDCG advantage. Their diversity cap
finds substantially more relevant books than BM25, but it returns at most one
page per book. BM25 therefore has higher exact-page recall while missing more
required books.

## All-route comparison

The follow-up [shared strategy workflow](../private-book-strategy-comparison/README.md)
rebuilds seven source-generic projections over the same authoritative 18-book
ledger and evaluates all 18 compatible retrieval routes across the eight
registered families. Every route uses the same frozen 40 questions, Top-10
cutoff, and three repetitions. The metric-only result is
[`all-route-comparison.md`](reports/all-route-comparison.md). This record-level
comparison is separate from the page-level direct evaluation above and does
not measure generated-answer quality.

The follow-up
[`evidence-drilldown-evaluation.md`](reports/evidence-drilldown-evaluation.md)
tests a qrel-blind two-stage workflow: fusion selects books, then source-filtered
BM25 opens one, three, five, or ten pages inside each selected book. At ten
pages per selected book, mean reviewed-locator recall rises from 6.67% to
30.00%, with at least one exact reviewed page found for 60% of hard questions.
The cost is an average of 59 opened pages, and no hard question retrieves every
preselected exact page. The result supports fusion for book discovery but shows
that evidence localization still needs a stronger second-stage ranker.

## Local Harbor isolation

ADR 0088 keeps this private corpus out of the canonical checked descriptor
registry. The local orchestration script creates an ignored hash-pinned
descriptor, stages evaluator-free raw Markdown, generates both isolated modes,
checks deterministic regeneration, validates all mechanical oracles, and
creates redacted development and hard-cohort dry runs:

```bash
python evaluations/software-architecture-books/scripts/private_harbor.py all
python evaluations/software-architecture-books/scripts/private_harbor.py \
  descriptor --check-descriptor
```

- `build-consult` mounts only staged raw input at `/dataset`, installs the
  matched build and consult skills, and builds `/workspace/knowledge`.
- `consult-only` mounts only the exact processed snapshot at `/knowledge` and
  installs only the consultation skill.

Live Harbor execution is intentionally not run from Windows. The cross-platform
dry-run receipts prove configuration and isolation, not model answer quality.
The publishable hash-and-count evidence is recorded in
[`harbor-rehearsal-summary.json`](reports/harbor-rehearsal-summary.json).
