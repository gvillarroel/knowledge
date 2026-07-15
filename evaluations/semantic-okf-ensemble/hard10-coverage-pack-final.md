# Definitive Ensemble Hard-10 Coverage-Pack Evaluation

> Historical final-02 two-route report (schema 1.0). It is preserved append-only
> for comparison and is not the accepted final-03 multisignal coverage result.

Status: **pass**. The report is bound to the frozen benchmark and the exact published final plan.

This evaluates the evidence candidates available to answer synthesis, not just the direct entity-graph section route. The union is variable-budget and therefore must not be labeled Recall@30.

Coverage percentages below are macro averages across the ten questions, so every question has equal weight.

## Route comparison

| Route | Answer claim IDs | Answer groups | Negative claim IDs | Negative groups | Required papers | Mean candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Adaptive facets | 76.5% | 76.5% | 88.3% | 100.0% | 100.0% | 81.0 |
| Reviewed claim graph | 47.5% | 47.5% | 57.5% | 80.0% | 100.0% | 50.6 |
| Gated union | 78.5% | 78.5% | 88.3% | 100.0% | 100.0% | 100.3 |

## Per question

| Question | Adaptive/graph/union candidates | Answer groups A/G/U | Negative groups A/G/U | Papers A/G/U |
| --- | ---: | ---: | ---: | ---: |
| `q031-graph-routing-boundary` | 96/57/121 | 75.0%/25.0%/75.0% | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| `q032-incremental-update-maturity` | 71/54/94 | 80.0%/60.0%/80.0% | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| `q033-corruption-specific-defenses` | 76/43/90 | 50.0%/50.0%/50.0% | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| `q034-nonmonotonic-context-budget` | 62/44/79 | 50.0%/25.0%/50.0% | 100.0%/0.0%/100.0% | 100.0%/100.0%/100.0% |
| `q035-lossless-enough-evidence-organization` | 73/51/86 | 75.0%/75.0%/75.0% | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| `q036-evaluation-leakage-and-stage-separation` | 72/44/86 | 80.0%/40.0%/80.0% | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| `q037-domain-construction-under-constraints` | 97/58/120 | 80.0%/80.0%/100.0% | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| `q038-failure-aware-query-router` | 85/52/96 | 75.0%/25.0%/75.0% | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |
| `q039-baseline-bound-efficiency-claims` | 96/58/137 | 100.0%/20.0%/100.0% | 100.0%/0.0%/100.0% | 100.0%/100.0%/100.0% |
| `q040-answer-source-control` | 82/45/94 | 100.0%/75.0%/100.0% | 100.0%/100.0%/100.0% | 100.0%/100.0%/100.0% |

## Interpretation

The graph route adds **1** answer group and **0** important-negative groups that adaptive facets alone missed. Because the final set is a union, this gain does not remove adaptive candidates.

As raw totals, adaptive covers **34/44** answer groups, the graph route covers **21/44**, and the union covers **35/44**. The union covers **13/13** important-negative groups.

Every one of the **590** distinct returned bindings passed independent record, source path, concept path, PDF-page locator, reviewed text, and SHA-256 checks. The bundle remained byte-identical.

Uncovered answer groups:

- `q031-a2`: GraphRAG has its clearest reported advantages on complex reasoning, contextual summarization, and creative generation.
- `q032-a2`: HippoRAG argues that new knowledge can be added as graph associations instead of recomputing a summary hierarchy.
- `q033-a2`: GraphRAG-FI's filtering recovered part of the performance lost after 30 irrelevant and incorrect paths were injected.
- `q033-a4`: KAG uses original chunks to supplement structured results when graph facts omit detail or generation context.
- `q034-a3`: CommunityKG-RAG reports non-monotonic accuracy as sentence inclusion changes at a fixed community threshold.
- `q034-a4`: ROGRAG reports lower accuracy at a 64k maximum context than at 32k, attributing the decline to harder extraction of subtle information.
- `q035-a4`: Community summaries can lose specific examples, quotations, and citations that matter to answer quality.
- `q036-a1`: Evaluation should measure graph quality, retrieval recall and relevance, and generation accuracy, faithfulness, and coverage as separate stages.
- `q038-a2`: PolyG selects traversal behavior from which subject, predicate, or object components are missing instead of applying one policy to every graph question.

All important failure conditions are covered by the gated union.

The JSON companion retains each ground-truth option group, its acceptable claim IDs, route-specific matches, candidate-set hashes, and all reproducibility bindings.
