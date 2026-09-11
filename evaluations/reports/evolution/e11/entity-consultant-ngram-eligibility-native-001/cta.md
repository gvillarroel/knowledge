# Entity Graph consultant n-gram eligibility transfer: cost, time and scope

The [native outcome](README.md) and [aggregate](aggregate.json) bind these observations to the original attempt.

| Quantity | Observed value | Interpretation |
| --- | ---: | --- |
| Native trials | 1 | Original fixed measurement only |
| Qualified trials | 0 | Execution, provenance and task qualification |
| Native execution errors | 1 | An error is not a zero quality score |
| Native retries | 0 | First-attempt policy |
| Observed build and standalone validation logs | 4 / 4 reported valid | Dated phase evidence; no extra execution or phase timing |
| Native job duration | 3,636.132 seconds | Complete original job interval |
| Agent duration | 3,600.099 seconds | Nested in native job duration |
| Both builds | Unavailable seconds | Existing verifier observation; nested in agent duration |
| Primary query p95 | Unavailable ms | Fixed fusion route |
| Knowledge size | Unavailable bytes | Existing verifier observation |
| Complete preallocation callback | 481.446 seconds | Timed before the dispatcher; not a native trial |
| Dispatch reservation to terminal outcomes | 4,170.887 seconds | Starts after admission; includes native work and reporting. Do not add nested durations |
| Agent CPU / memory caps | 2 / 6 GiB | Configured limits; no peak-memory estimate |
| Agent time limit | 3,600 seconds | Unchanged execution limit |
| Native input / cached / output tokens | Unavailable / Unavailable / Unavailable | Cached input is already included in total input |
| Native recorded model cost | Unavailable | USD when reported; excludes host compute |
| Host compute cost | Unavailable | Local resource use was not priced |
| New proposal charges in this measurement | 0 | Candidate was already charged |
| Cumulative proposals | 89 / 585 | Entity Graph 6 / 80; no transfer from closed catalogs |

The reservation interval starts after the dispatcher admission check. That pre-reservation admission duration was not separately measured.
The earlier timed callback is a separate observation; summing the displayed intervals does not recover total orchestration wall time.

The deterministic adapter uses no language model. Missing native usage stays unavailable; it is not inferred as zero.
The earlier 1,024-record public consultation-only fixture is separate software evidence and is not added to these native job durations.
No causal speedup or memory-reduction ratio is claimed against the previous failed measurement.

The 120-question development score, if qualified, is not official Overall, generated-answer quality or a public ranking.
The all-500 paired comparison and independent acceptance remain unfinished.
