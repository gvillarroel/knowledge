# Ensemble semantic-return correction: cost, time and scope

The new measurement is a finite public software fixture. The
[native EnterpriseRAG results](../construction-native-terminal-001/cta.md)
remain unchanged and retain their two execution failures.

| Quantity | Observed value | Interpretation |
| --- | ---: | --- |
| Public fixture records | 4 | Same records in both arms |
| Containers | 1 | Pinned Python 3.12.13 image |
| Child Python commands | 12 | Two builds, two validations, six queries, two negative validations |
| Container elapsed time | 48.42 seconds | Includes both arms; no speedup estimate |
| CPU limit | 2 | Same container for both arms |
| Memory limit | 6 GiB | Configured cap, not measured peak |
| Peak RSS | Unavailable | No memory-reduction claim |
| Network | None | Empty read-only benchmark dataset mask |
| OOM events / retries | 0 / 0 | Fixture completed successfully |
| New Harbor jobs / retrieval scores | 0 / 0 | Full workload remains unmeasured for this candidate |
| Language-model calls | 0 | Deterministic software only |
| Compute cost | Unavailable | Local resource use was not priced |
| New proposal charges | 1 | Candidate reservation; fixture itself adds none |
| Cumulative proposals | 84 / 585 | Ensemble 2 / 105; earlier consumed attempts preserved |

The five sealed Windows validation commands are separate correctness evidence.
Their raw per-command timestamps and disposable output trees were not retained,
so no duration or cost total is inferred for them. Neither their counts nor the
12 fixture commands are independent EnterpriseRAG trials. The
[aggregate](aggregate.json) records the exact retained container interval and
review commitments; the [candidate report](README.md) explains scope and limits.
