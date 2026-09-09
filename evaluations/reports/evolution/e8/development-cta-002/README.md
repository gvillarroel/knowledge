# E7/E8 cumulative development CTA through Classical012

This fixed inventory contains **81 completed native jobs**: all 66 completed E7 originals and fifteen E8 jobs through Classical continuation012. It was observed at 2026-09-09T11:44:47.419011+00:00. Six baselines and 75 candidate trials are included; 74 jobs produced qualified retrieval measurements and seven failed during construction.

Completed native job durations sum to **28.42 hours**, including **4.73 hours** in failed jobs. This is accumulated job time. Concurrent family lanes overlap, so the sum is not campaign wall time, CPU usage, billed time or an efficiency ranking.

## Execution and retained development quality

| Family | Completed jobs | Qualified / errors | Native job hours | Failed job hours | Retained nDCG@10 | Gain over initial baseline |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | 17 | 17 / 0 | 0.62 | 0.00 | 72.38% | +11.27 pp |
| embeddings | 7 | 1 / 6 | 4.35 | 4.05 | 63.51% | +0.00 pp |
| classical | 35 | 35 / 0 | 15.30 | 0.00 | 62.10% | +7.06 pp |
| adaptive | 19 | 19 / 0 | 7.29 | 0.00 | 66.21% | +6.17 pp |
| entity-graph | 0 | 0 / 0 | 0.00 | 0.00 | N/A | N/A |
| ensemble | 0 | 0 / 0 | 0.00 | 0.00 | N/A | N/A |
| graphify | 1 | 0 / 1 | 0.68 | 0.68 | N/A | N/A |
| turso | 2 | 2 / 0 | 0.19 | 0.00 | 72.08% | +26.65 pp |

The historical jobs are counted once; E8's import and revalidation of them add no native trial. The 75 jobs in the earlier [E7/E8 CTA checkpoint](../development-cta-001/README.md) retain exactly the same durations, usage, qualification and quality here. Its original denominator remains unchanged.

Legacy and Embeddings retain their completed searches. Classical remains active. Adaptive and Turso have unfinished opportunities after E8 admission refusals. Entity Graph and Ensemble have no started native trial. Graphify has one failed original baseline and no retrieval score. Missing quality remains null; a zero job count does not establish efficiency.

## Coverage and excluded effort

This cutoff excludes Classical013 and every later job, even if they finish after publication. It also excludes the two permanently unavailable E7 originals: Classical023 and Adaptive019 were interrupted without terminal results, so their complete durations remain unavailable. Their consumed attempts and unavailable profile bindings remain in the campaign history.

Four E8 refusals before dispatch created no native job: Entity Graph and Ensemble baselines, Turso's next candidate and Adaptive's first continuation candidate. They contribute no native trial or quality result. Setup effort, host fixtures, Docker probes, prospective implementation reviews, other earlier studies and the separate full-corpus Classical/Luna experiment are outside this native-job total. The Graphify host fixture reports preserve their own consumed counts and time.

Successful jobs include their required repeated construction, validation and declared routes. Family route counts and completed candidate counts differ, so this report does not compute a cost-to-quality composite or a causal speedup.

## Token and financial telemetry

| Measurement | Jobs with a value | Recorded sum | Jobs with missing values | Complete total |
| --- | ---: | ---: | ---: | --- |
| Native input plus output tokens | 74 | 0 | 7 | N/A |
| Native reported USD cost | 74 | 0.00 | 7 | N/A |

The seven construction failures have absent native token and cost fields. Their fields stay null. Input tokens include cached input, so the cached field is not added again. All 81 jobs have native and agent execution durations.

The benchmark adapter's declared model-call budget is zero. Orchestration usage, machine charges and electricity were not measured. Recorded zero values in the successful jobs therefore do not establish a complete financial cost or a free campaign.

## Evidence and interpretation

The unchanged maintained Harbor reporter normalized all 81 original job directories as one inventory, with diagnostic threshold 0.8 and no cross-family paired-comparison claim. Exact job identities, native source hashes, locks, owning archives and all historical job/skill inventories were checked. No job, verifier or model was rerun. Qualification means native provenance and required mechanical gates passed; it is distinct from the reporter's 0.8 diagnostic cutoff.

Retained quality is transcribed from the [five-family matrix](../retained-cross-family-002/README.md) and checked against each exact native observation. It covers the same 120 stratified questions, 112 eligible cases, category population weight 470 and 6,000 reference-enriched full-text documents. The all-eight selection, paired all-500 comparison and one-way private acceptance remain pending. These are development retrieval results, not answer Overall or an official public rank.

[Exact totals and per-job commitments](aggregate.json) · [Current campaign](../README.md) · [Family evidence index](../../../../../docs/enterprise-family-report-index.md) · [CTA hub](../../../cta/README.md)
