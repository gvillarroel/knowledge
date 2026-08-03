# Trace-Derived Specialized Expert Evaluation

This study packages two standalone GraphRAG research experts from validated
Semantic OKF knowledge and measures their deterministic retrieval behavior.
The expert guidance comes from the v39 and v42
`trace-distillation-consult-builder` proposal evidence. Both proposals remain
experimental because their historical grounded-answer development gates did
not qualify for promotion. The reviewed aggregate provenance is preserved in
the [trace-distillation report](../semantic-okf-tika-mallet-tantivy/reports/trace-distillation-consult-builder-20260727.md).

## Retrospective definitive experts

The later
[definitive-expert study](reports/definitive-experts-20260728.md) forges one
separate expert for each canonical domain. The GraphRAG v51 expert reaches the
Top-10 ceiling of 96.56% Recall with 100.00% MRR, 100.00% nDCG, and a
three-run median P95 of 47.13 ms. The Astro v3 expert reaches 100.00% on all
three quality metrics with a three-run median P95 of 211.34 ms. Exact evidence
validity is 100% for both.

The shared adapter uses one-to-five-token supervised profiles plus a cached
authoritative lexical fallback, deduplicates canonical identities, and contains
no exact-question lookup. Both results are retrospective because every
canonical qrel was exposed. They rank the frozen datasets but are explicitly
ineligible for holdout promotion.

## Builder and artifact boundary

The knowledge builder is `build-semantic-okf-tika-mallet` at the qualified v46
state accepted by ADR 0070. That is the repository's strongest causally
qualified builder: its direct development and holdout builder tasks scored
`1.0`, while the consultation proposals remained below their promotion gate.
This selection is distinct from choosing the highest-scoring direct retriever.
The supporting builder evidence is summarized in the
[reflective Pareto report](../semantic-okf-tika-mallet-tantivy/reports/reflective-pareto-consult-builder-20260727.md).
This study also performed a fresh network-disabled build and an independent
validation in the qualified Linux runtime; the compact
[reproduction receipt](reports/v46-builder-reproduction-20260728.json) binds
their logs, runtime, promoted candidate, and final knowledge tree.

`build-specialized-skill` then performs the separate packaging stage. It copies
the validated knowledge into each expert, binds the complete tree in
`expert-manifest.json`, adds reviewed guidance, and emits a read-only query
helper. The generated experts and raw runs live under the ignored, append-only
path:

```text
evaluations/semantic-okf-tika-mallet-tantivy/generated/
  specialized-experts/20260728-trace-guidance-01/
```

The two canonical expert names are:

- `graphrag-trace-expert-v39`, using a full-question anchor plus two to four
  exact, non-redundant retrieval facets;
- `graphrag-trace-expert-v42`, adding a bounded paper union and structured
  response-integrity checks.

## Ensemble-quality-derived v48 result

The exact 904-file Ensemble `quality` knowledge snapshot was first packaged as
`graphrag-ensemble-quality-expert-v46`. Its multi-file adapter reproduces the
canonical quality policy exactly: 83.82% Recall@10, 100.00% MRR@10, and 85.20%
nDCG@10.

A closed deterministic search on q001-q024 then evaluated 1,800 global
combinations of the protected quality Top-10 and the independent trace-derived
fielded-BM25 Top-10. A protocol correction excluded v47 because its selector,
unlike its executable adapter, credited trace ranks below the declared
candidate budget. The corrected schema-1.1 search selected a strict Top-10
union with quality weight 9, trace weight 5, and RRF constant 0.

The resulting `graphrag-ensemble-quality-trace-expert-v48` reaches:

| Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Selected P95 | Position |
|---:|---:|---:|---:|---:|---:|
| 85.39% | 100.00% | 86.02% | 100.00% | 2012.48 ms | 1 of 24 |

The checked
[v48 improvement audit](reports/ensemble-quality-trace-improved-retrieval-20260728.md)
replaces the evolved Ensemble `quality` row. Recall improves by 1.57
percentage points and nDCG improves by 0.82 points. The
[v48 study report](reports/v48-ensemble-quality-trace-study-20260728.md)
records the exact reproduction, excluded selector boundary, corrected search,
package bindings, all-40 result, and latency and hard-cohort trade-offs.

V48 remains retrospective because no untouched retrieval cohort exists. It is
an experimental deterministic rank, not a grounded answer-quality promotion.

## Knowledge-expertise-evolved v45 result

The Skill Arena `harbor-maximize-knowledge-expertise` planner generated four
SHA-bound, benchmark-agnostic mutation contracts for v44. Native Harbor 0.18.0
jobs evaluated all four on q031-q040. A second Pareto generation merged the
complementary early-rank and confidence-gated improvements, producing
`graphrag-trace-expert-v45`.

The checked
[v45 improvement audit](reports/expertise-improved-retrieval-20260728.md)
reports:

| Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Selected P95 | Position |
|---:|---:|---:|---:|---:|---:|
| 85.39% | 92.08% | 83.75% | 100.00% | 573.53 ms | 3 of 24 |

This replaces the v44 row. Recall@10 improves by 0.42 percentage points and
nDCG@10 by 0.29 points while the rank remains third. The
[v45 study report](reports/v45-knowledge-expertise-study-20260728.md) records
the planner contract, two sealed Pareto generations, the excluded DrvFS
diagnostic attempt, candidate realization, and final package bindings. The
result remains retrospective because no untouched holdout exists.

## Previous Pareto-evolved v44 result

Native Harbor 0.18.0 jobs replayed v43 on the previously exposed q031-q040
cohort and drove two reflective Pareto generations. The selected
`graphrag-trace-expert-v44` combines the v43 trace rank with the snapshot's
immutable passage-BM25, PPMI-association, and MALLET-topic rank through weighted
reciprocal-rank fusion.

The checked
[Pareto improvement audit](reports/pareto-improved-retrieval-20260728.md)
reports:

| Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Selected P95 | Position |
|---:|---:|---:|---:|---:|---:|
| 84.97% | 92.08% | 83.47% | 100.00% | 568.22 ms | 3 of 24 |

This replaces the v43 row and moves it from position 10 to 3. The
[v44 study report](reports/v44-reflective-pareto-study-20260728.md) records the
three sealed generations, excluded diagnostic attempts, candidate trade-offs,
and artifact bindings. This result is retrospective: every available retrieval
cohort had prior exposure, so v44 is not a holdout-qualified promotion.

## Previous trace-improved result

The v39/v42 trace evidence was revalidated with Harbor 0.18.0 dry-run, doctor,
and analyze-only controls. A single v43 retrieval candidate was selected on the
24-question discovery cohort, frozen, and then evaluated on a separate
q031-q040 confirmation cohort before the canonical all-40 run.

`graphrag-trace-expert-v43` preserves the complete question, expands exact
hyphenated facets, and fuses fielded BM25 scores from the paper and reviewed-
claims records. The checked
[improvement audit](reports/trace-improved-retrieval-20260728.md) reports:

| Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Selected P95 | Position |
|---:|---:|---:|---:|---:|---:|
| 82.88% | 87.65% | 81.76% | 100.00% | 229.86 ms | 10 of 24 |

This replaces the preceding expert row and moves it from position 19 to 10. The
full discovery, confirmation, prior-exposure holdout, and all-40 evidence
boundary is documented in the
[study report](reports/trace-improved-retrieval-study-20260728.md).

## Previous canonical result

The checked
[canonical retrieval audit](reports/canonical-retrieval-20260728.md) evaluates
all 40 frozen GraphRAG questions with the same paper identity, binary qrels,
Top-10 budget, and metric contract as the current direct-retrieval table.

The shared deterministic lexical route reached:

| Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Selected P95 | Position |
|---:|---:|---:|---:|---:|---:|
| 72.20% | 80.07% | 66.57% | 100.00% | 170.78 ms | 19 of 24 |

The audit binds four independent runs: v39 and v42 at Top 10, plus a pool-100
run for each. It requires exact rankings across guidance variants, exact
Top-10 prefixes in the pool-100 runs, identical builder and knowledge bindings,
distinct guidance bindings, zero query errors, and exact evidence validity.
The complete builder snapshot contains 30 authoritative records: 15 papers and
15 reviewed-claim collections. Retrieval keeps the first result for each
authoritative paper identity before applying the Top-10 budget.

The two guidance variants receive one shared retrieval row because guidance is
not executed by the deterministic lexical helper. Their trace-derived
instructions can affect a model's evidence selection and synthesis, but that is
a separate grounded Harbor evaluation. The historical v39 and v42 development
results failed their promotion gates and therefore do not receive a grounded
answer leaderboard position.

## Reproduction

Create new append-only output paths for every run:

```powershell
python evaluations/semantic-okf-specialized-experts/scripts/evaluate_direct_retrieval.py `
  --expert EXPERT `
  --builder-skill skills/build-semantic-okf-tika-mallet `
  --trace-evidence PROPOSAL_STATE `
  --trace-evidence DEVELOPMENT_GATE `
  --top-k 10 `
  --output-json NEW_RUN/report.json `
  --output-markdown NEW_RUN/report.md
```

Repeat for both experts with `--top-k 10` and `--top-k 100`, then run
`audit_direct_retrieval.py` over the four reports and the current comparison
contract. Validate the publication with:

```powershell
python evaluations/validate_final_report.py `
  evaluations/semantic-okf-specialized-experts/reports/canonical-retrieval-20260728.md
python evaluations/validate_comparison_contract.py `
  evaluations/semantic-okf-specialized-experts/reports/canonical-retrieval-20260728.comparison.json `
  --report evaluations/semantic-okf-specialized-experts/reports/canonical-retrieval-20260728.md
```

For v43, pass the frozen
`query_expert_knowledge_trace_bm25.py` file to both packaging commands with
`--query-template`, add `--packager-skill skills/build-specialized-skill` to the
evaluation runs, and close the Top-10/pool-100 pair with
`audit_improved_retrieval.py`.

For v44, use
`skills/build-specialized-skill/assets/expert-template/query_expert_knowledge_trace_classical_hybrid.py`
as the query template. Bind all three sealed `ep-v43-g0-03` Pareto archives to
both evaluation runs, then invoke `audit_improved_retrieval.py` with candidate
ID `specialized-expert-trace-classical-hybrid`, route
`specialized_expert_trace_classical_hybrid`, and retrieval contract
`trace-classical-hybrid-rrf-v3`.

For v45, use the exact query helper sealed in the
`early-confidence-merge` realization. Bind the expertise plan, both
`ep-v44-xg1-01` Pareto archives, and the operator realization to both direct
evaluation runs. Invoke `audit_improved_retrieval.py` with candidate ID
`specialized-expert-trace-early-confidence`, route
`specialized_expert_trace_classical_early_confidence`, and retrieval contract
`trace-classical-early-confidence-v6`.

For v48, package
`query_expert_knowledge_ensemble_quality_trace.py` as the query template and
bind the six `consult-semantic-okf-ensemble` runtime files, the pure quality
adapter, and `query_expert_knowledge_trace_bm25.py` through repeated
`--query-support` arguments. Run the schema-1.1 selector only on q001-q024,
then reproduce its metrics with the materialized expert before opening the
all-40 run. Close the Top-10/pool-100 pair with
`audit_improved_retrieval.py`, replacing `ensemble-quality` and requiring
retrieval contract `ensemble-quality-trace-union-rrf-v3`.
