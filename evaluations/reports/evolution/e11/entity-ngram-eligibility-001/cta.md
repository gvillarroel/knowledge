# Entity n-gram candidate: cost, time and scope

Seven software commands passed; four integration cells account for 192 child
commands. The realizer does not record validation wall time. Missing timing,
host price, peak memory and model usage remain unavailable.

The separate pinned runtime attempted exactly three commands in one container:

| Operation | Elapsed seconds | Extraction seconds | Extraction calls |
| --- | ---: | ---: | ---: |
| build | 38.638 | 8.908 | 3 |
| validate | 11.456 | 2.962 | 1 |
| consult-deep | 9.205 | 4.263 | 1 |

Each command had a 300-second limit; the container had a 960-second limit,
2 CPU, 6 GiB and no network. Configured memory is not measured peak memory.
cProfile overhead is included; nested extraction times are part of command
times and cannot be added to them. Staging, hash checks and export are outside
the command profiles. The parent and its historical reference were not rerun.
No contemporaneous paired timing or native speedup is claimed.

One new nonrefundable proposal was charged, bringing the total to 87. No native
Harbor trial, retry or quality miss was added. Full EnterpriseRAG resource fit,
retrieval quality, official Overall and public ranking remain unavailable for
this candidate. [Outcome](README.md) · [Aggregate](aggregate.json).
