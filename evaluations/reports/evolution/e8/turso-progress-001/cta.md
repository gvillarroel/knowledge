# Cost, time and quality

[Family report](README.md)

Two CPU threads and 6 GiB per agent, with at most two concurrent trials. These original jobs have zero LLM calls, evidence integrity 1, no execution errors and zero retries. CPU inference and host costs are unpriced; provider cost is N/A. Historical jobs keep their original timing across the host restart.

| Candidate | Native job s | Agent s | Double build s | Knowledge MiB | Primary query P95 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 422.18 | 372.25 | 177.41 | 803.06 | 2461.20 |
| continuation-001 | 243.92 | 194.24 | 172.64 | 803.06 | 105.46 |

Timings exclude staging and supervisor overhead. The displayed jobs are selected measurement references, not the total campaign workload. Incomplete historical attempts are not assigned zero time.
