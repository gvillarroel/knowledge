# EnterpriseRAG E14: Turso and Adaptive pending variants did not improve

Date: 2026-09-11. **Turso retains 72.08 and Adaptive retains 66.21 nDCG@10 x100.** Their first pending measurements produced 69.31 and 64.53 respectively. Both results are qualified, with zero execution errors and zero retries.

| Family | Treatment | Tested parameters | Retained nDCG x100 | Candidate nDCG x100 | Delta points | Improved / regressed / tied cases |
| --- | --- | --- | --- | --- | --- | --- |
| Turso | consultation | `{"engine": "bm25", "k1": 0.6}` | 72.08 | 69.31 | -2.77 | 7 / 26 / 79 |
| Adaptive | construction | `{"bm25.b": 0.25}` | 66.21 | 64.53 | -1.68 | 14 / 26 / 72 |

The paired case counts cover 112 retrieval-eligible questions; eight additional questions have no retrieval references. Scores use the frozen category population weights, so case counts alone do not determine the aggregate delta. The shared workload contains 120 stratified questions and 6,000 complete documents, with eligible population weight 470.

## Search accounting

Both observations consume their exact, already-charged pending identities: `continuation-002` for Turso and `continuation-001` for Adaptive. They add **zero proposal charges**, one unique evaluable miss per active mechanism, and no retry. Turso remains at 2 / 55 inherited claims; Adaptive at 20 / 100. Each mechanism remains open under the three-consecutive-miss rule and the five-round ceiling. Turso changes consultation parameters with its builder frozen. Adaptive changes the construction plan with its consultation implementation frozen. The two treatment types remain separate.

The reconciled prefixes contain six native records: one original Turso reference and five E14 records. Only two of those records are new generation-one observations. Normalization and reporting executed no new trial. Native job locks, 252-file evaluated packages, imported consultation modules, output routes, case order and owner retention were reconciled against their source commitments.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| legacy | 72.38 | Qualified starting profile |
| turso | 72.08 | Qualified starting profile |
| adaptive | 66.21 | Qualified starting profile |
| embeddings | 63.51 | Qualified starting profile |
| classical | 62.10 | Qualified starting profile |
| graphify | 8.12 | Qualified starting profile |
| ensemble | Unavailable | Starting execution error |
| entity-graph | Unavailable | Starting execution error |

The ranking is unchanged. Legacy leads this development snapshot. The [application/category leaders](../qualified-starts-comparison-001/README.md) remain a descriptive comparison among six qualified profiles. The [Entity Graph and Ensemble errors](../starting-execution-errors-001/README.md) remain consumed and unqualified, with outstanding hypotheses.

## Verification and remaining work

Current application gate 052 passed 1,643 tests and 373 subtests with 90.5% total application coverage. These pages export existing reconciled measurements; they add no scoring or skill implementation. Private validation remains unopened. All eight opportunity obligations, paired joint development replay, one frozen whole bundle, the all-500 comparison and independent acceptance are still required. This is an internal retrieval result, not an answer-quality score or public leaderboard rank.

[Applications and categories](groups.md) · [Cost, time and quality](cta.md) · [Full-precision aggregate and source commitments](aggregate.json) · [E14 overview](../README.md)
