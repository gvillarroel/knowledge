# Entity Graph token automaton: cost, time and evidence scope

| Evidence | Work measured | Result |
| --- | --- | --- |
| Sealed software validation | Seven declared commands; four integration cells with 152 child commands | Passed |
| Ordered mention comparisons | 1,120 comparisons, including 1,066 nonempty cases | Exact parity |
| Independent count oracles | Duplicate/overlap and suffix counts | Both passed |
| New public runtime fixture | One container; one 128-record build and one standalone validation | Passed; 145 identical files |
| New EnterpriseRAG jobs | 0 | Full native qualification pending |
| New proposal charge | 1 | 85 cumulative of 585; Entity Graph 2 of 80 |
| New evaluable quality misses | 0 | Software correctness is separate from retrieval fitness |
| Model calls in software checks | 0 | Deterministic local execution |
| Host compute cost | Unavailable | Local CPU/memory use was not priced |
| Application coverage | 90.7% | 1,631 tests and 373 subtests passed; 80% gate passed |

| Operation | Frozen parent | Token automaton |
| --- | ---: | ---: |
| Complete build | 9.608 s | 9.507 s |
| Mention matching within build | 0.835 s | 0.748 s |
| Standalone validation | 3.178 s | 3.076 s |
| Mention matching within validate | 0.274 s | 0.245 s |

All times above include profiling overhead. Parent and candidate each have one
observation per operation. Mention time is nested, so these rows must not be
summed. The historical parent measurement is reused as evidence, not dispatched
again. The earlier host-storage profiles and rejected title-metadata fixture
remain separate artifacts with their consumed work preserved.

There is no measured EnterpriseRAG quality, official Overall, public rank,
all-500 comparison or independent acceptance for this candidate. Missing quality
and cost values remain null in the [aggregate](aggregate.json).

[Candidate evidence](README.md) · [Retained native comparison](../ensemble-semantic-return-native-001/README.md)
