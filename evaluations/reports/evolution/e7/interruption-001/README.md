# E7 Windows-update interruption

The original E7 campaign stopped when a planned Windows update restarted the
host. Windows records the new boot at 2026-09-09 03:35:46 UTC. The supervisor no
longer exists, and both active trial containers exited with code 255. Their
native root files still contain a null finish time and one stale running slot.
These files are preserved as incomplete original evidence.

There are **66 completed native jobs and two incomplete jobs**, from four
families with baselines. Sixty completed jobs qualify; six Embeddings jobs
ended in construction timeouts and have no measured retrieval quality. The
completed jobs include four baselines and 62 variants. The two incomplete jobs
are Classical023 and Adaptive019. Neither has a native TrialResult or verifier
diagnostics; Adaptive has a response artifact, which is not a measured result.

| Family | Baseline nDCG@10 | Retained development nDCG@10 | Completed variants | Incomplete jobs | Search status |
| --- | ---: | ---: | ---: | ---: | --- |
| legacy | 61.11% | 72.38% | 16 | 0 | family-complete |
| embeddings | 63.51% | 63.51% | 6 | 0 | family-complete |
| classical | 55.04% | 61.89% | 22 | 1 | interrupted |
| adaptive | 60.04% | 66.21% | 18 | 1 | interrupted |
| entity-graph | Unavailable | Unavailable | 0 | 0 | not-started |
| ensemble | Unavailable | Unavailable | 0 | 0 | not-started |
| graphify | Unavailable | Unavailable | 0 | 0 | not-started |
| turso | Unavailable | Unavailable | 0 | 0 | not-started |

All scores retain their original weighted 120-question, 112-eligible-question,
6,000-document development contract. Classical's eighth measured gain is
documented in [its report](../classical-progress-008/README.md); the
[four-family matrix](../retained-cross-family-007/README.md) preserves category
and application differences. These retained profiles are provisional development
incumbents. E7 never reached joint selection, the paired all-500 comparison,
private validation or promotion. Four families still need native opportunities.

## Recovery disposition

The native Harbor reporter normalized the two original jobs with explicit
`--allow-incomplete` and reward threshold `0.8`, without a comparison. Missing
measurements remain unavailable. Both `--doctor` and `--dry-run` of the installed
external-failure recovery tool rejected each incomplete job: no finish timestamp,
no TrialResult and a stale running slot. All four probes returned exit code 2.
The probe configuration used the tool's required positive diagnostic cap; it
does not change E7's zero-retry policy. No live recovery was called, no native
trial was dispatched and both source inventories remained unchanged.

The installed pre-agent SIGTERM exception and post-agent artifact-collection
EIO recovery contract do not match these originals. A host restart or the
presence of a response does not supply their required native evidence. The
two profiles will not be reissued under another candidate identifier or scored
as zero. Neither interruption consumes an evaluable miss.

## Continuation boundary

The independent review found no supported subset-resume entrypoint in the
frozen E7 runner. Appending an evolution stage cannot give it the already sealed
downstream validation gate. E7's missing searches cannot be marked complete.
The organizer will record this disposition and stop its executable stages
without releasing private data. The original sources, jobs and earlier reports
remain unchanged.

A prospective continuation study may import exact completed development jobs
through the native owner, preserve consumed resources and prior exposure, and
continue the remaining catalog while excluding the two unavailable profiles.
Its stopping reports must disclose those omissions. It requires its own frozen
protocol, task versions for any changed all-500 timeout, downstream gate and
independent review before dispatch. An unopened reservation may transfer only
after the curator verifies terminal E7 and the six earlier histories and binds
a new exclusive guard. No transfer or new execution is claimed by this report.

The full-corpus Classical/Luna answer experiment remains a separate result;
these development scores supply no official EnterpriseRAG Overall or public rank.

The [aggregate and source commitments](aggregate.json) bind the original
checkpoint, native interruption audit, normalized report and independent review.
See [ADR 0130](../../../../../.specs/adr/0130-continue-interrupted-enterprise-search-prospectively.md)
and the [campaign overview](../README.md).
