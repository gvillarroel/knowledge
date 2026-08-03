# GraphRAG retrieval skill-group recommendation

## Conclusion

Use two operational profiles rather than one universal retrieval stack:

1. **Quality-first, fully measured:** `build-semantic-okf-classical` with
   `consult-semantic-okf-classical` in `association` mode.
2. **Balanced runtime, measured:** `consult-semantic-okf-tantivy` over the
   frozen validated classical projection.

The classical association pair is the evidence-backed choice when retrieval
quality is the primary constraint. The measured Tantivy consultation route is
the evidence-backed runtime default when response time matters: it is 5.18 times faster at P95 while
giving up 3.35 nDCG percentage points and retaining 100% Recall@10.

For a new Tantivy construction, `build-semantic-okf-tantivy` is the intended
matched builder, but the current holdout did not rebuild or evaluate that
builder. Treat the complete new-build pair as a validation candidate, not as
an already proven pair.

Keep `build-semantic-okf-tika-mallet` with
`consult-semantic-okf-tika-mallet` in `fusion` mode as an experimental
ultra-fast option only. Its P95 is lower than Tantivy, but it gives up another
4.97 nDCG percentage points and its builder depends on preview Tika software.

## Evidence and decision rules

The recommendation derives from the sealed
`graphrag-papers-parallel-eval-60-v1` comparison:

- sixty evaluation-only questions over the frozen fifteen-paper corpus;
- authoritative-paper Top-10 identity;
- three process repetitions per strategy;
- exact evidence validity;
- median repetition P95; and
- no construction, tuning, or evolution from the evaluation-only payload.

Only strategies with 100% evidence validity and 100% query-ranking stability
are eligible for the operational recommendation.

| Objective | Selection rule | Selected strategy |
| --- | --- | --- |
| Maximum quality | Maximize nDCG@10, then MRR@10, Recall@10, and lower P95 | Classical association |
| Balanced default | Minimize P95 among strategies with at least 95% nDCG@10 and 95% Recall@10 | Tantivy BM25 |
| Ultra-fast experimental | Minimize P95 among strategies with at least 90% nDCG@10 and 95% Recall@10 | Tika/MALLET fusion |

These thresholds are explicit operational rules documented after evaluation.
They support a provisional recommendation, not holdout-qualified promotion.

## Contradiction-search profile

The separate
`graphrag-papers-contradiction-eval-40-v1` study changes the quality-first
choice for workloads that must retrieve every side of an apparent
contradiction. Its primary metric is Full evidence@10, not nDCG@10.

| Contradiction-search objective | Strategy | Full evidence@10 | nDCG@10 | P95 |
| --- | --- | ---: | ---: | ---: |
| Maximum source coverage | Specialized expert v45 early confidence-gated hybrid | 92.50% | 85.11% | 941.60 ms |
| Near-maximum, lower latency | RustMallet association | 90.00% | 87.09% | 492.97 ms |
| Classical matched pair | Classical association | 87.50% | 86.83% | 454.25 ms |
| Low-latency compromise | Tantivy BM25 | 82.50% | 81.28% | 122.69 ms |

Use v45 only for the scoped contradiction-search workload when maximum
complete-source coverage justifies its latency. RustMallet association is the
strongest measured compromise within 2.50 Full evidence points of v45.
Classical association remains the simpler matched build/consult pair. Tantivy
is substantially faster but misses at least one required contradiction side
on seven of forty questions.

This scoped result does not replace the broader general-retrieval default.
The v51 supervised-profile expert is not eligible for contradiction search:
it reaches 52.50% Full evidence@10 and only 50.00% Top-10 stability.

## Recommended skill groups

| Profile | Evaluated construction | Consultant | Mode | Recall@10 | MRR@10 | nDCG@10 | P95 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| Quality-first | `build-semantic-okf-classical` | `consult-semantic-okf-classical` | `association` | 100.00% | 100.00% | 99.60% | 664.65 ms |
| Balanced runtime | Frozen classical-builder lineage | `consult-semantic-okf-tantivy` | native BM25 | 100.00% | 96.25% | 96.25% | 128.27 ms |
| Ultra-fast experimental | `build-semantic-okf-tika-mallet` | `consult-semantic-okf-tika-mallet` | `fusion` | 99.44% | 90.85% | 91.28% | 99.48 ms |

The two classical projections used by classical association and Tantivy share
the same authoritative records and classical plan but have different
projection tree digests. The evaluation therefore does not establish one
shared bundle, a query-level cascade, a cross-family fusion result, or the
quality of a fresh `build-semantic-okf-tantivy` output.

## Quality-latency interpretation

The deterministic, evidence-valid Pareto frontier contains five strategies:

| Strategy | nDCG@10 | P95 | Interpretation |
| --- | ---: | ---: | --- |
| Classical association | 99.60% | 664.65 ms | Best measured quality |
| RustMallet BM25 | 98.11% | 650.81 ms | Near-ceiling, but only 2.08% faster than the quality winner |
| Tantivy BM25 | 96.25% | 128.27 ms | Best practical quality/latency point |
| Tika/MALLET fusion | 91.28% | 99.48 ms | Ultra-fast experimental point |
| Legacy lexical | 60.54% | 9.96 ms | Lowest latency, insufficient ranking quality |

Tantivy is the strongest knee of the frontier. Compared with classical
association, it reduces P95 by 80.70%, is 5.18 times faster, preserves 100%
Recall@10 and deterministic rankings, and loses 3.35 nDCG percentage points.

Tika/MALLET saves only 28.79 ms beyond Tantivy while losing 4.97 additional
nDCG percentage points. That trade is justified only under a strict
approximately 100 ms P95 budget and acceptance of an experimental builder.

## Strategies not selected

- Classical fusion, adaptive fusion, ensemble robust, and classical topic are
  dominated by classical association on both nDCG@10 and P95.
- Ensemble fast and v48 add substantial latency without improving over the
  selected quality-first group.
- RustMallet BM25 remains on the Pareto frontier, but its 650.81 ms P95 is too
  close to classical association to justify the 1.49-point nDCG loss.
- Legacy lexical is useful only when latency dominates retrieval order and
  quality.
- Supervised profiles v51 is not eligible: it reached only 41.03% nDCG@10 and
  reproduced 43.33% of query rankings.

## Operating policy

- Choose the measured Tantivy consultant over its frozen validated classical
  projection as the provisional runtime default for latency-sensitive direct
  retrieval.
- Choose the classical association pair when the workload permits an
  approximately 665 ms P95 and quality is the overriding objective.
- For new construction, realize `build-semantic-okf-tantivy` plus
  `consult-semantic-okf-tantivy` as a matched candidate and validate it on a
  new sealed cohort before changing the default.
- Select the profile at workload or SLA configuration time. Do not build a
  query-level cascade from this dataset.
- Continue to verify returned concepts and locators in the authoritative OKF
  layer; retrieval scores remain non-authoritative.
- Use `harbor-organize-evaluations` and `harbor-run-results` to validate any
  proposed default change on a newly sealed cohort.
- Do not tune, fuse, repair, or evolve candidates from the current
  evaluation-only questions or rankings.

## Scope and limitations

This study measures same-corpus unseen-question direct retrieval. It does not
measure generated-answer correctness, unseen-corpus transfer, build time,
storage cost, tokens, or end-to-end agent latency. P95 is an operational
diagnostic because family setup boundaries differ.

The complete
[general ranking](study-v4-general-organized/publication/tables/general-strategy-ranking.table.md)
and
[quality-latency frontier](study-v4-general-organized/publication/tables/quality-latency-frontier.table.md)
are the general evidence surfaces. The
[contradiction-search ranking](study-v5-contradictions/publication/tables/contradiction-strategy-ranking.table.md)
is the scoped evidence surface. A production promotion requires a different,
newly sealed validation cohort.
