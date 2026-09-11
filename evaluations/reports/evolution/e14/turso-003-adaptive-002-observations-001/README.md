# EnterpriseRAG E14: Turso k1=3.0 and Adaptive b=0.0 did not improve

Date: 2026-09-11. **Turso retains 72.13 and Adaptive retains 66.21 nDCG@10 x100.** Their latest qualified candidates scored 71.13 and 62.31 respectively, with zero errors and retries.

| Family | Treatment | Tested parameters | Retained nDCG | Candidate nDCG | Delta points | Improved / regressed / tied |
| --- | --- | --- | --- | --- | --- | --- |
| Turso | consultation | `{"engine": "bm25", "k1": 3.0}` | 72.13 | 71.13 | -0.99664 | 16 / 10 / 86 |
| Adaptive | construction | `{"bm25.b": 0.0}` | 66.21 | 62.31 | -3.89975 | 13 / 31 / 68 |

The fixed development workload is 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. Eight questions have no retrieval references. Aggregate deltas reflect magnitude and frozen population weights; counts alone do not determine improvement. Displayed values are rounded independently from full precision.

## Search accounting

| Family | Cumulative claims / cap | Measured mechanism | Round | Consecutive evaluable misses | Variant cursor / declared count |
| --- | --- | --- | --- | --- | --- |
| Turso | 4 / 55 | bm25-saturation | 1 | 1 | 4 / 4 |
| Adaptive | 21 / 100 | length-normalization | 2 | 2 | 2 / 4 |

Both latest observations are new catalog claims, adding one proposal each. The original pending identities from earlier generations remain consumed and are not charged again. Turso's preceding k1=2.0 gain reset its miss counter; the k1=3.0 result therefore records one consecutive miss. Its four declared saturation variants have now all been issued, so the controller may advance to the next mechanism without claiming three consecutive misses occurred. Adaptive has two consecutive misses in the current length-normalization mechanism. Family searches remain open under their inherited caps, three-miss rule and five-round ceiling.

Turso changes consultation parameters with its builder frozen. Adaptive changes construction-plan parameters with its consultation implementation frozen. The two treatment types remain separate. No candidate is promoted.

## Native evidence and retained comparison

The reconciled prefixes contain nine original native observations: one preserved E13 Turso reference and eight E14 records. Only two are the newly reported observations. Complete prefix inventories preserve earlier measured candidates even when the latest Pareto archive omits them. Job locks, evaluated 252-file packages, imported consultation modules, output routes and owner retention were verified. Reporting executed no new native job.

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

The [current six-family application/category comparison](../turso-generation-002-001/comparison.md) is unchanged. Graphify retains 8.12 after its first depth-zero miss. Entity Graph and Ensemble remain unavailable after their original execution errors, with outstanding hypotheses.

## Verification and remaining work

Current application gate 052 passed 1,643 tests and 373 subtests with 90.5% total application coverage. These pages export existing reconciled evidence and change no application, skill package, dataset or private gate. All eight opportunity obligations, joint paired development replay, one whole-bundle freeze, all-500 comparison and independent acceptance remain required. These internal retrieval results are not answer-quality scores or public leaderboard ranks.

[Application/category groups](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
