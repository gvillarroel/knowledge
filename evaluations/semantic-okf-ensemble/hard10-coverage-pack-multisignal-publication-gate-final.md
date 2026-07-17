# Definitive Multisignal Ensemble Hard-10 Coverage-Pack Evaluation

Status: **pass**. The report is bound to the frozen benchmark, exact published final plan, and pinned semantic index.

This evaluates the adaptive, reviewed graph-claim, and pinned embedding-claim candidates available to answer synthesis. The gated union is variable-budget and therefore must not be labeled Recall@30.

Coverage percentages below are macro averages across the ten questions, so every question has equal weight.

## Route comparison

| Route | Answer claim IDs | Answer groups | Negative claim IDs | Negative groups | Required papers | Mean candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Adaptive facets | 77.9% | 88.0% | 80.5% | 100.0% | 100.0% | 81.0 |
| Reviewed claim graph | 46.1% | 54.0% | 49.9% | 80.0% | 100.0% | 50.6 |
| Pinned semantic claims | 86.8% | 95.0% | 85.5% | 100.0% | 100.0% | 126.1 |
| Gated union | 91.3% | 97.5% | 87.1% | 100.0% | 100.0% | 166.4 |

Mean candidate overlaps: adaptive∩graph **31.3**, adaptive∩embedding **53.4**, graph∩embedding **32.7**, and all three **26.1**.

## Per question

| Question | Adaptive/graph/embedding/union candidates | Answer groups A/G/E/U | Negative groups A/G/E/U | Papers A/G/E/U |
| --- | ---: | ---: | ---: | ---: |
| `q031-graph-routing-boundary` | 96/57/142/198 | 75.0%/50.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q032-incremental-update-maturity` | 71/54/122/148 | 100.0%/80.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q033-corruption-specific-defenses` | 76/43/122/160 | 50.0%/50.0%/75.0%/75.0% | 100.0%/100.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q034-nonmonotonic-context-budget` | 62/44/113/142 | 100.0%/25.0%/100.0%/100.0% | 100.0%/0.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q035-lossless-enough-evidence-organization` | 73/51/124/148 | 100.0%/75.0%/75.0%/100.0% | 100.0%/100.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q036-evaluation-leakage-and-stage-separation` | 72/44/107/138 | 100.0%/60.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q037-domain-construction-under-constraints` | 97/58/151/191 | 80.0%/80.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q038-failure-aware-query-router` | 85/52/114/155 | 75.0%/25.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q039-baseline-bound-efficiency-claims` | 96/58/148/220 | 100.0%/20.0%/100.0%/100.0% | 100.0%/0.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |
| `q040-answer-source-control` | 82/45/118/164 | 100.0%/75.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% | 100.0%/100.0%/100.0%/100.0% |

## Interpretation

Relative to adaptive facets, the graph route finds **1** additional answer groups and the embedding route finds **4**. Of the embedding additions, **3** remain unique after adaptive and graph candidates are combined.

For important-negative groups, graph and embedding add **0** and **0** over adaptive respectively; **0** embedding additions remain unique beyond adaptive plus graph.

As raw totals, adaptive covers **39/44** answer groups, graph covers **24/44**, embedding covers **42/44**, and the union covers **43/44**. The union covers **13/13** important-negative groups.

The semantic route used `sentence-transformers` model `sentence-transformers/all-MiniLM-L6-v2` at immutable revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Its component plan, retrieval index, chunks, and embedding artifacts are hash-bound in the JSON report.

Every one of the **713** distinct returned bindings passed independent record, source path, concept path, PDF-page locator, reviewed text, and SHA-256 checks. The bundle remained byte-identical.

Uncovered answer groups:

- `q033-a4`: KAG uses original chunks to supplement structured results when graph facts omit detail or generation context.

All important failure conditions are covered by the gated union.

The JSON companion retains each ground-truth option group, its acceptable claim IDs, route-specific matches, candidate counts and overlaps, route-set hashes, semantic provider/index bindings, and all reproducibility gates.
