# E12 controller failure: cost, time and quality scope

This checkpoint executed **zero native jobs and zero model calls**. Native
agent latency, memory, usage and retrieval quality are therefore unavailable
for E12. The controller's failure is not a zero-quality retrieval result.

| Evidence | Observed result | Interpretation |
| --- | --- | --- |
| Original development invocation | Controller error before allocation | No native retrieval measurement |
| Native jobs and model calls from this invocation | 0 / 0 | No new native or model workload |
| New measured quality or native speedup | Unavailable | No attributable improvement |
| Native API integration tests | 9 passed in 14.092 seconds | Software-test time; execution and persistence replaced with test doubles |
| E12 stage closure | Four stages stopped; verification passed | Factual terminal bookkeeping |

Software-test duration includes test setup and configuration loading. It is
not an EnterpriseRAG task time, agent latency, resource improvement or cost
estimate. Total engineering effort and host energy were not measured.

The [prior EnterpriseRAG CTA](../../e11/entity-traversal-adjacency-reuse-native-001/cta.md)
retains the earlier native outcomes and missing telemetry. The
[prior Entity software CTA](../../e11/entity-evidence-index-reuse-001/cta.md)
has a separate workload and must not be pooled with this integration test.

[Terminal report](README.md) · [Aggregate](aggregate.json)
