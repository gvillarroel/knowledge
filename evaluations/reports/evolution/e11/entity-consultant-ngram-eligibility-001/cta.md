# Entity consultant eligibility: cost, time and quality

| Observation | Outcome | Subject commands | Elapsed seconds |
| --- | --- | ---: | ---: |
| Original runtime preflight | Refused because image-baked dataset was visible | 0 | Not a subject timing |
| Corrected consultation-only runtime | Exact deep-validation response and unchanged snapshot | 1 | 8.909 |
| New native EnterpriseRAG first measurement | Unassigned | 0 | Unavailable |

The successful cell uses Python 3.12.13, rdflib 7.6.0, pyshacl 0.40.0 and
PyYAML 6.0.3, a pinned image, 2 CPU and 6 GiB. The child limit is 300 seconds;
the outer attach limit is 360 seconds. cProfile overhead is included and the
asynchronous traceback sampler is disabled. The snapshot is mounted read-only.
No old fixture, builder or parent is reexecuted. This single observation does
not establish a paired speedup or peak-memory reduction.

Software validation also retained seven passed checks and 192 integration
child commands. Those command counts are not native trials. Model calls are
zero; local compute cost is unmeasured. There is no new retrieval score,
generated-answer score, official Overall or public rank. The
[retained retrieval comparison](README.md#retained-enterpriserag-comparison)
and [previous native timeout CTA](../entity-memory-lifetime-native-001/cta.md)
remain the relevant EnterpriseRAG evidence.

[Report](README.md) · [Aggregate](aggregate.json) · [Groups](groups.md)
