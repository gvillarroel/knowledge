# EnterpriseRAG E14: Graphify depth zero did not improve retrieval

Date: 2026-09-11. **The qualified `depth=0` consultation variant scored 7.03 nDCG@10 x100, below the retained 8.12 reference.** The native owner keeps `baseline`. Both original measurements completed with zero execution errors and zero retries.

The workload remains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. The builder is frozen; the tested change is the consultation traversal-depth parameter.

| Metric (x100) | Retained baseline | Depth-zero candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 8.12 | 7.03 | -1.08369 |
| Recall@10 | 14.85 | 11.17 | -3.67908 |
| MRR@10 | 6.71 | 6.62 | -0.09161 |
| Full-reference coverage@10 | 12.53 | 8.85 | -3.67908 |

At question level, **7 improve, 4 regress and 101 tie**; eight more questions have no retrieval references. The size of each change and the frozen population weights determine the aggregate loss, rather than the count of improved questions alone. Displayed values and deltas are rounded independently from full precision.

## Opportunity accounting

This is Graphify's first new catalog proposal and first unique evaluable miss in the traversal-depth mechanism: **1 / 65 claims** and **1 / 3 consecutive misses**. The mechanism remains open under the inherited three-miss rule and five-round ceiling. This loss does not close the family's other evolution opportunities. The original candidate identity and measurement are consumed; there is no retry, additional charge or candidate promotion.

The two native records were reconciled against their job locks, trial results, all 252 evaluated skill files, imported consultation modules and output routes. Normalization used both completed native jobs; the later owner receipt and progress confirmed the same qualification and retention. Reporting dispatched no new job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| legacy | 72.38 | Qualified |
| turso | 72.13 | Qualified |
| adaptive | 66.21 | Qualified |
| embeddings | 63.51 | Qualified |
| classical | 62.10 | Qualified |
| graphify | 8.12 | Qualified |
| ensemble | Unavailable | Execution error; not qualified |
| entity-graph | Unavailable | Execution error; not qualified |

The ranking is unchanged. [Turso's latest 72.13 incumbent and the six-family application/category comparison](../turso-generation-002-001/comparison.md) remain current. Entity Graph and Ensemble retain unavailable quality after their original execution errors, with outstanding hypotheses.

## Verification and remaining work

Current application gate 052 passed 1,643 tests and 373 subtests with 90.5% total application coverage. This publication exports existing reconciled evidence and changes no application, skill or dataset. Private gates remain unopened. All eight opportunity obligations, the joint development replay, whole-bundle freeze, all-500 comparison and independent acceptance remain required. These are internal retrieval results, not answer-generation scores or public leaderboard ranks.

[Applications and categories](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
