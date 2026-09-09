# E7 development CTA: completed execution effort and measurement gaps

This snapshot covers all **54 completed native jobs** bound by [status022](../status-022/README.md), observed at 2026-09-09T00:28:13.373166+00:00: four baselines and 50 candidate attempts. Forty-eight jobs produced qualified retrieval measurements; six Embeddings attempts failed during construction. In-flight trials and families without a completed baseline are outside the measured workload.

Completed native job durations sum to **17.82 hours**. The six failed jobs account for **4.05 hours** of that sum. Two family lanes can overlap, so this is accumulated job time, not campaign wall time, CPU-hours or billed time. It excludes preparation outside native job timestamps and the uncompleted portion of the campaign.

## Execution and retained development quality

| Family | Completed native jobs | Qualified / errors | Native job hours | Hours in failed jobs | Retained nDCG@10 | Gain over its initial baseline |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | 17 | 17 / 0 | 0.62 | 0.00 | 72.38% | +11.27 pp |
| embeddings | 7 | 1 / 6 | 4.35 | 4.05 | 63.51% | +0.00 pp |
| classical | 17 | 17 / 0 | 7.84 | 0.00 | 60.10% | +5.06 pp |
| adaptive | 13 | 13 / 0 | 5.01 | 0.00 | 65.36% | +5.33 pp |
| entity-graph | 0 | 0 / 0 | 0.00 | 0.00 | N/A | N/A |
| ensemble | 0 | 0 / 0 | 0.00 | 0.00 | N/A | N/A |
| graphify | 0 | 0 / 0 | 0.00 | 0.00 | N/A | N/A |
| turso | 0 | 0 / 0 | 0.00 | 0.00 | N/A | N/A |

Native job counts include the baseline. Legacy and Embeddings searches are terminal at this snapshot; Classical and Adaptive are incomplete, and the other four families have not started. Zero accumulated time for an unstarted family is not evidence of efficiency. The retained Embeddings quality belongs only to its qualified baseline; failed candidates have null retrieval scores and do not become zero-quality measurements.

Each completed successful job includes the required repeated construction, verification and its registered retrieval routes. The number of routes differs by family. Cumulative effort also depends on how many candidates have finished, so this table does not rank family efficiency or compute a cost-to-quality composite. Native timestamps establish duration, not actual CPU utilization or a causal speedup from one profile.

## Token and financial telemetry

| Measurement | Jobs with a recorded value | Sum of recorded values | Jobs with missing values | Complete total |
| --- | ---: | ---: | ---: | --- |
| Native agent input plus output tokens | 48 | 0 | 6 | N/A |
| Native job cost in USD | 48 | 0.00 | 6 | N/A |

Input tokens already include cached input; cached input is not added a second time. The six errored jobs have absent token and cost fields in the original native results. Those fields remain null. They cannot be converted to zero to manufacture complete telemetry. All 54 jobs have recorded native and agent execution durations; the source observations retain both.

The frozen benchmark agent/judge model-call budget is zero and retrieval is deterministic. That execution contract is distinct from observed accounting fields. Orchestration model usage, local machine charges and electricity were not measured by this report. The complete financial cost remains unavailable; neither the partial recorded USD sum nor the declared benchmark model-call budget establishes that the campaign is free.

## Evidence and remaining scope

Every job result and lock was checked against the published snapshot and owning native archive. All 54 original jobs were normalized together as an inventory at diagnostic threshold 0.8, without a cross-family paired-comparison claim. Qualification here means the native evidence and mechanical gates passed; it is distinct from that diagnostic reward threshold. All jobs have zero retries. No trial was rerun for this report.

Quality uses the same 120 stratified questions, 112 eligible questions, population weight 470 and 6,000 reference-enriched full-text documents as the [retained-profile comparison](../retained-cross-family-004/README.md). This is development retrieval relevance, not answer accuracy or an official public leaderboard result. All eight searches, the final all-500 comparison and the private acceptance gate must complete before final campaign accounting or profile promotion can be reported.

[Exact totals, missing fields and per-job source hashes](aggregate.json) · [Embeddings failure evidence](../embeddings-complete-001/README.md) · [Campaign](../README.md) · [CTA hub](../../../cta/README.md)
