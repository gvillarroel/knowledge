# Traversal adjacency reuse: cost, time and quality scope

| Observation | Retained parent | Adjacency-reuse candidate |
| --- | ---: | ---: |
| Public synthetic records | 1,024 | 1,024 |
| Queries / routes / calls | 12 / 4 / 48 | 12 / 4 / 48 |
| Query wall time with profiling | 15.726573 s | 7.784849 s |
| Query computations | 48 | 48 |
| Full-query-cache hits | 0 | 0 |
| Traversal-index construction | Rebuilt inside every traversal call | 1 profiled index build |
| Candidate responses equal to retained references | Reference | 48 / 48 |

The observed sequential query-time ratio is **2.020x**. cProfile
overhead is included. Both observations used Python 3.12.13, rdflib 7.6.0,
pyshacl 0.40.0 and PyYAML 6.0.3 in the same pinned image, with two CPUs, 6 GiB,
no network, read-only consultant/knowledge mounts and an empty read-only
`/dataset`. The parent was not rerun. These observations do not establish a
causal or native speedup, uncertainty interval or peak-memory improvement.

Candidate deep loading took 5.264690 seconds and is
outside the query profile. Its whole subject command took
14.787410 seconds, including the load,
queries and replay checks. These durations overlap and must not be summed.
Nested cumulative function times must not be added either.

The replay used one container and one subject command, with zero automatic
retries, zero builder commands, zero model calls and zero native Harbor jobs.
Host compute was not priced; no USD figure is inferred. It adds no retrieval
quality score, answer-quality result or evaluable quality miss. Cumulative
proposal accounting is 90 / 585; the new native first measurement is unassigned.

[Software/runtime result](README.md) · [Source-bound aggregate](aggregate.json)
