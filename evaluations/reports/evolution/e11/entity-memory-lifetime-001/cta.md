# Entity builder lifetime transfer: cost, time and scope

The [software report](README.md) and [source-bound aggregate](aggregate.json)
keep this public fixture separate from native EnterpriseRAG scoring.

| Quantity | Observed value | Scope |
| --- | ---: | --- |
| Realization commands passed | 9 | Includes four integration cells and two paired probes |
| Integration CLI commands | 192 | Nested in the four cells; not native trials |
| Additional paired probe processes | 4 | Lifetime and atomic-failure observations |
| Pinned-runtime containers | 1 | Python 3.12.13, 2 CPUs, 6 GiB, network disabled |
| Pinned-runtime records | 1,024 | One synthetic JSON source family |
| Runtime build | 38.185 seconds | One complete build; profiling overhead included |
| Runtime standalone validation | 11.220 seconds | Same constructed snapshot |
| Runtime deep consultation | 10.012 seconds | Same snapshot; no retrieval benchmark score |
| Exact reference output files | 19 | Existing reference read without a new execution |
| New native EnterpriseRAG trials | 0 | Future first measurement is unassigned |
| New proposal charges | 1 | Entity 5/80; cumulative 88/585 |
| New retrieval gain | Unavailable | No native ranking from this candidate |
| Native speedup / peak-memory reduction | Unavailable / Unavailable | Software observations do not establish either |
| Model / host cost | Unavailable / Unavailable | No priced native workload |

The deterministic fixtures call no language model. No token usage or host cost
is inferred from absence of a native run. Collection can add overhead; the
single runtime cell is not a contemporaneous paired performance experiment.
The [previous native timeout](../entity-ngram-eligibility-native-001/cta.md)
retains its original costs and status.
