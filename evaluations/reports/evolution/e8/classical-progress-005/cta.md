# Cost, time and quality

[Family report](README.md)

Two CPU threads and 6 GiB per agent, with at most two concurrent trials. These original jobs have zero LLM calls, evidence integrity 1, no execution errors and zero retries. CPU inference and host costs are unpriced; provider cost is N/A. Historical jobs keep their original timing across the host restart.

| Candidate | Native job s | Agent s | Double build s | Knowledge MiB | Primary query P95 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 1639.79 | 1589.73 | 579.06 | 532.05 | 2189.65 |
| continuation-002 | 1444.72 | 1395.89 | 538.60 | 532.05 | 1864.58 |
| continuation-005 | 1451.66 | 1399.99 | 535.58 | 532.05 | 1918.68 |

Timings exclude staging and supervisor overhead. The displayed jobs are selected measurement references, not the total campaign workload. Incomplete historical attempts are not assigned zero time.
