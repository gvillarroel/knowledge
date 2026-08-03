# Post-v51 GraphRAG Generalization Study

This study evaluates frozen GraphRAG expert retrieval strategies on questions
authored after the v51 supervised profile had been sealed. The questions and
review material remain private under the organizer-managed study directory.
Only reviewed aggregate tables are publishable.

The current reusable ranking boundary is
`graphrag-papers-parallel-eval-60-v1`: a sixty-question evaluation-only
extension over the same fifteen papers. It contains thirty hard single-paper
audits, twenty two-paper comparisons, and ten three-paper syntheses. Each
question binds five to twelve previously reviewed claims to exact PDF pages.

The comparison uses:

- the same fifteen-paper GraphRAG corpus and authoritative ledger;
- one fixed Top-10 paper-identity contract;
- seven pre-existing immutable expert packages;
- twenty new questions with source-paper qrels;
- source-derived expected answers bound to reviewed claims and PDF pages; and
- three independent process repetitions per strategy, with ranking stability
  reported explicitly.

The exhaustive general comparison extends that protocol to every compatible
row in the pre-existing twenty-five-strategy table. Its freeze, private runs,
and aggregate evidence live under `study-v4-general/`; its append-only study
ledger and publication surface live under `study-v4-general-organized/`.
Graphify and Turso remain outside the ranked table because neither exposes the
same authoritative-paper Top-10 route.

The contradiction-search extension is
`graphrag-papers-contradiction-eval-40-v1`. It adds forty new questions over
the same fifteen papers: fifteen require two papers, twenty require three, and
five require four. Each question asks whether apparently conflicting claims
are a direct contradiction, a scope-conditioned tension, an
evidence-incommensurable result, or a compatible trade-off. Its primary
retrieval metric is Full evidence@10: every paper needed to adjudicate the
question must appear in the first ten distinct papers. The organizer study,
private evidence, and public aggregate table live under
`study-v5-contradictions/`.

The direct-retrieval evaluator uses an explicit
`--expected-question-count 20` holdout contract. Its default remains the
canonical 40-question benchmark.

The parallel extension uses `--expected-question-count 60`. Its public digest
is registered in `evaluations/evaluation-only-registry.json`. It may be used
only for sealed final evaluation and aggregate reporting. It must never be
used for construction, supervised profile forging, evolution, trace
distillation, candidate selection, or optimizer-visible fitness.

This is an unseen-query evaluation for the already frozen experts. It is not
an unseen-corpus evaluation, and the question author had access to the corpus.
The expected answers are mechanically bound to the repository's previously
reviewed claim ledger, but they are not a new independent human adjudication.

## Private inputs

The post-v51 organizer study lives at `study-v2/`. The earlier `study/` ledger
is retained as a superseded audit trail because its original stage typing
prevented holdout release. The current parallel evaluation study lives at
`study-v3-parallel/`. Each deny-by-default `.gitignore` keeps questions,
answers, task trees, candidate artifacts, and raw reports private. The safe
post-v51 publication surface is:

```text
study-v2/publication/index.json
study-v2/publication/index.md
study-v2/publication/tables/*.table.md
```

The parallel evaluation study lives at `study-v3-parallel/`; its safe
publication table is
`publication/tables/three-cohort-generalization.table.md`.

The exhaustive strategy study publishes
`study-v4-general-organized/publication/tables/general-strategy-ranking.table.md`.
Its question-level rankings remain private.

The contradiction-search study publishes
`study-v5-contradictions/publication/tables/contradiction-strategy-ranking.table.md`.
The questions, qrels, source-derived adjudications, exact claim anchors, raw
rankings, and per-question diagnostics remain private.

The operational interpretation is documented in
`STRATEGY-RECOMMENDATION.md`. It recommends the matched classical association
pair for maximum quality and the measured Tantivy consultation route as the
provisional quality/latency runtime default. A fresh Tantivy builder/consult
pair still requires a new sealed validation cohort. The metric-only Pareto frontier is published at
`study-v4-general-organized/publication/tables/quality-latency-frontier.table.md`.
These are post-evaluation recommendations, not formal promotions, and must not
be used to tune candidates against the evaluation-only questions.

## Reproduction

Build or check the private benchmark:

```powershell
python evaluations/graphrag-unseen-generalization/scripts/build_benchmark.py `
  --blueprint evaluations/graphrag-unseen-generalization/study/private/benchmark-blueprint.json `
  --output-dir evaluations/graphrag-unseen-generalization/study/private/benchmark-v2

python evaluations/graphrag-unseen-generalization/scripts/build_benchmark.py `
  --blueprint evaluations/graphrag-unseen-generalization/study/private/benchmark-blueprint.json `
  --output-dir evaluations/graphrag-unseen-generalization/study/private/benchmark-v2 `
  --check
```

Raw direct-retrieval runs are written below `study-v2/private/runs/`. Aggregate
them with `scripts/aggregate_reports.py`, then review the resulting Markdown
before copying only its metric table into the organizer publication directory.

Build and validate the parallel extension:

```powershell
python evaluations/graphrag-unseen-generalization/scripts/build_parallel_benchmark.py `
  --parent-questions evaluations/graphrag-unseen-generalization/study/private/benchmark-v2/retrieval-questions.jsonl `
  --output-dir evaluations/graphrag-unseen-generalization/study-v3-parallel/private/parallel-benchmark `
  --check

python evaluations/graphrag-unseen-generalization/scripts/validate_evaluation_only.py `
  --dataset-dir evaluations/graphrag-unseen-generalization/study-v3-parallel/private/parallel-benchmark `
  --questions evaluations/graphrag-unseen-generalization/study-v3-parallel/private/parallel-benchmark/retrieval-questions.jsonl `
  --purpose evaluation
```

Before any future profile-forging or evolution run, validate the intended
question file with the same script using the actual purpose. A registered
evaluation-only digest fails closed for every optimizer-visible purpose.

Freeze and aggregate the exhaustive strategy population with:

```powershell
python evaluations/graphrag-unseen-generalization/scripts/freeze_general_strategies.py `
  --output evaluations/graphrag-unseen-generalization/study-v4-general/private/strategy-selection.json

python evaluations/graphrag-unseen-generalization/scripts/aggregate_general_strategies.py `
  --selection evaluations/graphrag-unseen-generalization/study-v4-general/private/strategy-selection.json `
  --adaptive-report <adaptive-repetition-1.json> `
  --adaptive-report <adaptive-repetition-2.json> `
  --adaptive-report <adaptive-repetition-3.json> `
  --ensemble-report <ensemble-report.json> `
  --rust-report <rust-repetition-1.json> `
  --rust-report <rust-repetition-2.json> `
  --rust-report <rust-repetition-3.json> `
  --tantivy-report <tantivy-repetition-1.json> `
  --tantivy-report <tantivy-repetition-2.json> `
  --tantivy-report <tantivy-repetition-3.json> `
  --tika-report <tika-repetition-1.json> `
  --tika-report <tika-repetition-2.json> `
  --tika-report <tika-repetition-3.json> `
  --tika-tantivy-report <combined-repetition-1.json> `
  --tika-tantivy-report <combined-repetition-2.json> `
  --tika-tantivy-report <combined-repetition-3.json> `
  --specialized-comparison evaluations/graphrag-unseen-generalization/study-v3-parallel/private/reports/parallel60/comparison.json `
  --output-json <private-report.json> `
  --output-markdown <publication-table.md> `
  --output-companion <publication-comparison.json>
```

Build, verify, and policy-check the contradiction-search extension with:

```powershell
python evaluations/graphrag-unseen-generalization/scripts/build_contradiction_benchmark.py `
  --output-dir evaluations/graphrag-unseen-generalization/study-v5-contradictions/private/benchmark `
  --tasks-dir evaluations/graphrag-unseen-generalization/study-v5-contradictions/private/tasks

python evaluations/graphrag-unseen-generalization/scripts/build_contradiction_benchmark.py `
  --output-dir evaluations/graphrag-unseen-generalization/study-v5-contradictions/private/benchmark `
  --tasks-dir evaluations/graphrag-unseen-generalization/study-v5-contradictions/private/tasks `
  --check

python evaluations/graphrag-unseen-generalization/scripts/validate_evaluation_only.py `
  --dataset-dir evaluations/graphrag-unseen-generalization/study-v5-contradictions/private/benchmark `
  --questions evaluations/graphrag-unseen-generalization/study-v5-contradictions/private/benchmark/retrieval-questions.jsonl `
  --purpose evaluation
```

Freeze the compatible population with
`scripts/freeze_contradiction_population.py` and aggregate the completed raw
reports with `scripts/aggregate_contradiction_strategies.py`. The latter
recomputes every ranking metric from the returned hits and the frozen qrels;
it does not trust evaluator summary metrics. The evaluation-only registry
must reject the contradiction question digest for construction, supervised
profile forging, evolution, trace distillation, candidate selection, and any
other optimizer-visible purpose.
