# Cost, time and quality: two native construction failures

This report accounts for the two original native measurements of the prepared
Ensemble and Entity Graph construction proposals. The
[source-bound aggregate](aggregate.json) preserves the native errors, missing
quality and usage, exact proposal identities and terminal study state.

| Strategy | Native jobs | Execution errors | Agent duration | Whole-job duration | New retrieval quality |
| --- | ---: | ---: | ---: | ---: | --- |
| Ensemble | 1 | 1 | 2,136.072 s | 2,168.332 s | Unavailable; no ranking |
| Entity Graph | 1 | 1 | 3,600.101 s | 3,631.514 s | Unavailable; no ranking |

The two jobs ran concurrently. Agent durations are contained within job
durations, so these values must not be added to estimate wall-clock elapsed
time. Dispatch through both original reports and qualifications took
**4,278.810 seconds**. The separate complete preallocation callback took
**482.132 seconds** and passed within its declared 900-second control limit.
This callback measurement is not the total of every later host-control call.

| Accounting item | Observed value |
| --- | --- |
| Exclusive dispatcher invocations | 1; terminal exit 1 |
| Native first measurements consumed | 2; one per already charged proposal |
| Worker / report / qualification exits | 0 / 0 / 1 for each family |
| Qualified native cases | 0 of 2 |
| Observed native retries | 0 for both jobs |
| New proposal charges in this execution | 0; cumulative claims remain 83 |
| New evaluable quality misses | 0; both outcomes are execution errors |
| Agent resources | 2 CPUs, 6 GiB, 3,600-second execution limit |
| Verifier resources declared | 2 CPUs, 2 GiB, 180 seconds; verification was not reached |
| Complete double-build duration and query latency | Unavailable |
| Per-job tokens and model cost | Unavailable in both native result records |
| Total host compute cost | Unavailable; no complete monetary telemetry |
| Private releases / skill installations | 0 / 0 |

The evaluated agent is the deterministic local retrieval runtime, not a Luna
answer-generation treatment. Missing usage records are left null, even though
the declared workflow has no answer-model call. No estimated token count,
native speedup, monetary saving or quality score substitutes for absent data.

The original resource failures and preceding
[180-second control timeout](../construction-callback-timeout-001/README.md) and
[Windows/Linux control refusal](../construction-owner-portability-001/cta.md)
remain separate historical costs. The earlier
[qualified starting CTA](../starting-terminal-001/cta.md) remains unchanged.
This checkpoint counts only the two newly executed jobs, not imported or
previously reported jobs a second time.

The organizer's terminal evidence contains twelve immutable files. The stage
is stopped at sequence 7, with both first measurements consumed and no retry
authority. A later construction mutation would be a new charged proposal;
neither failed result can be reissued under its original first-measurement ID.

[Construction results and retained comparison](README.md)
