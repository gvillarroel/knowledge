# Adaptive Facet-Coverage Evaluation

This report measures the union of a top-30 primary pack and bounded per-facet candidate lists. The union has a larger variable budget and is not Recall@30.

| Metric | Value |
| --- | ---: |
| Primary answer-claim Recall@30 | 60.0% |
| Facet-union answer-claim coverage | 76.5% |
| Facet-union important-negative coverage | 88.3% |
| Facet-union required-paper coverage | 100.0% |
| Mean unique candidate claims | 81.0 |
| Mean facet count | 7.1 |
| Mean latency | 1338.1 ms |

| Question | Primary claims | Union claims | Union negatives | Papers | Unique candidates | Facets |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| q031-graph-routing-boundary | 50.0% | 75.0% | 100.0% | 100.0% | 96 | 8 |
| q032-incremental-update-maturity | 60.0% | 80.0% | 100.0% | 100.0% | 71 | 7 |
| q033-corruption-specific-defenses | 50.0% | 50.0% | 100.0% | 100.0% | 76 | 6 |
| q034-nonmonotonic-context-budget | 50.0% | 50.0% | 50.0% | 100.0% | 62 | 6 |
| q035-lossless-enough-evidence-organization | 50.0% | 75.0% | 66.7% | 100.0% | 73 | 7 |
| q036-evaluation-leakage-and-stage-separation | 80.0% | 80.0% | 100.0% | 100.0% | 72 | 6 |
| q037-domain-construction-under-constraints | 80.0% | 80.0% | 100.0% | 100.0% | 97 | 9 |
| q038-failure-aware-query-router | 75.0% | 75.0% | 66.7% | 100.0% | 85 | 7 |
| q039-baseline-bound-efficiency-claims | 80.0% | 100.0% | 100.0% | 100.0% | 96 | 8 |
| q040-answer-source-control | 25.0% | 100.0% | 100.0% | 100.0% | 82 | 7 |

Every primary and facet candidate was rechecked against the independently derived answer bindings. The snapshot remained byte-identical and the runtime contained no frozen question IDs.
