# EnterpriseRAG: primary-route observations and strategy catalog

The new two-original job completed with **1/2 qualified retrieval outcomes**. The combined catalog has **7/8 qualified strategy observations**. Native execution errors: 1; verifier failures: 0. Unavailable quality is never shown as zero.

All rows use the same 500 public questions, 470 retrieval-eligible questions and 6,000 complete documents. Quality is native nDCG@10 multiplied by 100. Entity Graph and Ensemble execute only their primary outer route; the other six rows retain the earlier all-declared-routes treatment. These are source-linked observations across three jobs, with different mode exposure, cache history and observation times.

| Strategy | nDCG@10 x100 | Outcome | Runtime treatment | Source study |
| --- | ---: | --- | --- | --- |
| [legacy](skills/legacy.md) | 70.72 | Qualified | all-declared-routes | enterprise-all500-descriptive-001 |
| [turso](skills/turso.md) | 70.72 | Qualified | all-declared-routes | enterprise-all500-first-executions-001 |
| [embeddings](skills/embeddings.md) | 64.04 | Qualified | all-declared-routes | enterprise-all500-descriptive-001 |
| [adaptive](skills/adaptive.md) | 63.61 | Qualified | all-declared-routes | enterprise-all500-descriptive-001 |
| [graphify](skills/graphify.md) | 60.50 | Qualified | all-declared-routes | enterprise-all500-first-executions-001 |
| [classical](skills/classical.md) | 56.16 | Qualified | all-declared-routes | enterprise-all500-descriptive-001 |
| [entity-graph](skills/entity-graph.md) | 34.96 | Qualified | primary-route-only | enterprise-primary-route-001 |
| [ensemble](skills/ensemble.md) | Unavailable | Execution error | primary-route-only | enterprise-primary-route-001 |

The complete reference bundle, corpus, ordered questions, scoring code and resource envelope are preserved. The new treatment removes the extra outer mode sweeps. Planned work is 500 fusion calls for Entity Graph and 500 quality calls for Ensemble, preserving each policy's internal searches and two reproducibility builds. Observed starts and completions are reported separately in the phase table.

This catalog is descriptive. It is not a matched eight-strategy run, a causal speedup comparison, a newly improved or promoted skill, a Luna evaluation, or an official answer-quality leaderboard rank. The original interrupted job and E16 remain closed with their previous outcomes.

[Application/category tables](groups.md) · [Cost, time and quality](cta.md) · [Phase observations](phases.md) · [Dataset scopes](datasets.md) · [Aggregate data](aggregate.json) · [Methodology](../../../../docs/enterprise-primary-route-observation.md)

[Previous six-strategy catalog](../enterprise-all500-first-executions-001/README.md) · [Original interrupted study](../enterprise-all500-descriptive-001/README.md)
