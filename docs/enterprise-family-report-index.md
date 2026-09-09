# EnterpriseRAG reports by retrieval family

Use this index to find a family's native evidence and its supporting audits
without scanning every campaign checkpoint. The [campaign overview](../evaluations/reports/evolution/e7/README.md)
owns the latest live status. This page adds navigation, not an evaluation,
selection, score or promotion decision.

## Native family evidence

E7 measures deterministic retrieval on a stratified development subset of
120 questions, 112 with references, and 6,000 reference-enriched full-text
documents. Its four currently measured family routes share those questions and
the frozen category weights. The all-500 paired comparison remains pending.

| Family | Fixed primary route | Native result and development evidence | Supporting function or delivery evidence |
| --- | --- | --- | --- |
| Legacy | `lexical` | [Completed search and stopping history](../evaluations/reports/evolution/e7/legacy-complete-001/README.md); [category and application breakdown](../evaluations/reports/evolution/e7/legacy-subgroups-001/README.md) | [Declared opportunities and treatment boundaries](../evaluations/reports/evolution/e7/strategy-coverage.md) |
| Embeddings | `hybrid` | [Completed search, baseline and six construction timeouts](../evaluations/reports/evolution/e7/embeddings-complete-001/README.md) | [Original completed-job time and missing usage](../evaluations/reports/evolution/e7/development-cta-001/README.md) |
| Classical | `fusion` | [Seventh retained development gain](../evaluations/reports/evolution/e7/classical-progress-007/README.md); [category and application breakdown](../evaluations/reports/evolution/e7/classical-progress-007/subgroups.md) | [Application-group cap and untested follow-up](../evaluations/reports/evolution/e7/classical-source-cap-001/README.md) |
| Adaptive | `adaptive` | [Fifth retained development gain](../evaluations/reports/evolution/e7/adaptive-progress-005/README.md); [category and application breakdown](../evaluations/reports/evolution/e7/adaptive-progress-005/subgroups.md) | [First native aspect trial and exact payload parity](../evaluations/reports/evolution/e7/adaptive-aspect-001/README.md) |
| Entity Graph | `fusion` | No completed native family trial yet; see the campaign overview for current execution. | [Synthetic graph reach, rank fusion and document grouping](../evaluations/reports/evolution/e7/entity-graph-opportunity-001/README.md) |
| Ensemble | `quality` | No completed native family trial yet; see the campaign overview for current execution. | [Synthetic protected-set and allocation audit](../evaluations/reports/evolution/e7/ensemble-protection-001/README.md) |
| Graphify | `search` | No completed native family trial yet; see the campaign overview for current execution. | [Synthetic traversal depth and exact fusion treatments](../evaluations/reports/evolution/e7/graphify-opportunity-001/README.md) |
| Turso | `lexical-sql` | No completed native family trial yet; see the campaign overview for current execution. | [Native synthetic databases and SQL/BM25 ranking treatments](../evaluations/reports/evolution/e7/turso-opportunity-001/README.md); [generated-expert delivery boundary](../evaluations/reports/evolution/e7/turso-generated-expert-001/README.md) |

Legacy and Embeddings have terminal searches. Classical and Adaptive remain in
development. An error has no retrieval measurement; it is not a measured zero.
The synthetic audits for the four queued families do not replace their native
baselines or consume development attempts.

## Mechanism evidence

| Family | Mechanism | Focused evidence |
| --- | --- | --- |
| Classical | Expansion strength | [Three misses after an expansion gain](../evaluations/reports/evolution/e7/classical-expansion-002/README.md) |
| Classical | Relevance and diversity | [Three native ties and completion of the first improving round](../evaluations/reports/evolution/e7/classical-diversity-001/README.md) |
| Classical | Length normalization in the second round | [Gain after two misses; counter reset and duplicate-profile skip](../evaluations/reports/evolution/e7/classical-progress-007/README.md) |
| Adaptive | Length normalization | [Initial native length trials](../evaluations/reports/evolution/e7/adaptive-length-001/README.md) |
| Adaptive | Expansion strength | [Coverage/ranking tradeoff and catalog exhaustion](../evaluations/reports/evolution/e7/adaptive-expansion-002/README.md) |
| Adaptive | Relevance and diversity | [Retained gain and application regressions](../evaluations/reports/evolution/e7/adaptive-progress-005/README.md) |
| Adaptive | Aspect allocation | [First native miss with 120 identical ordered payloads](../evaluations/reports/evolution/e7/adaptive-aspect-001/README.md) |

These are selected explanatory reports. The campaign's checkpoint history
retains every completed attempt, including later misses that do not change a
retained profile. Only the original controller determines retention, stopping
and the next mutation; descriptive subgroup leaders never select a different
profile for each application.

## Shared views and dataset contracts

| View | Report | Scope |
| --- | --- | --- |
| Current native execution and opportunity counts | [Campaign overview](../evaluations/reports/evolution/e7/README.md) | Latest checkpoint for all eight families, including queued families and execution errors |
| Retained profiles by category and application | [Four-family matrix, revision 006](../evaluations/reports/evolution/e7/retained-cross-family-006/README.md) | Legacy009, Embeddings baseline, Classical020 and Adaptive014 on the stratified development subset |
| Cost, time and quality accounting | [Development CTA checkpoint 001](../evaluations/reports/evolution/e7/development-cta-001/README.md) | The 54 completed original jobs at checkpoint022; its denominator is fixed and does not expand with later trials |
| Complete declared evolution catalog | [Strategy coverage](../evaluations/reports/evolution/e7/strategy-coverage.md) | Eight families and 117 predeclared variants per catalog round; declared options are not completed attempts |
| Full-corpus Classical and Luna answers | [Separate full-corpus experiment](../evaluations/reports/enterprise-classical-full/README.md) | 511,962 physical documents and 500 questions under a distinct retrieval and answer/judge contract |
| Reports across repository datasets | [Comparison catalog](../evaluations/COMPARISON-REPORTS.md) | Source-linked reports with their own dataset, cohort and metric contracts |

The matrix is descriptive development evidence. Final E7 publication must still
include the exact baseline/frozen all-500 comparison, all eighteen routes per
arm, the joint acceptance result and a separate receipt for any permitted
repository installation. The [study guide](enterprise-stratified-evolution.md)
defines those boundaries; the [documentation index](README.md) links the broader
repository workflow.
