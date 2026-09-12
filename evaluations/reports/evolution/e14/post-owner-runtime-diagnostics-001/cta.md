# EnterpriseRAG E14 post-owner diagnostics: cost, time and quality

The two diagnostics used the previously pinned image with one container, two
CPUs, 6 GiB memory, no network and a read-only root filesystem. Provider cost
is zero because neither diagnostic called a model. Host compute remains
unpriced.

| Family | Container seconds | Declared whole-run cap | Child commands | Complete builds | Independent validations | Corruption rejections | Harbor jobs | Model calls | Retrieval quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Entity Graph | 173.453 | 900 s | 22 | 4 | 2 | 4 | 0 | 0 | Not scored |
| Ensemble | 88.390 | 240 s | 16 | 4 | 2 | 4 | 0 | 0 | Not scored |

Both executions used one attempt and zero automatic retries. Both exited zero,
reported no runner failure and were not killed for memory. The elapsed values
describe these public parity fixtures and do not establish a full-corpus
speedup, peak memory reduction, retrieval gain or service-level guarantee.

[Result and scope](README.md) · [Full-precision aggregate](aggregate.json)
