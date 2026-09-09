# E11 Entity Graph: agent timeout without a ranking

The original Entity Graph starting job finished on September 9, 2026 with an
`AgentTimeoutError` after the declared **3,600-second agent limit**. It produced
no ranking artifact. The settled native owner rejected qualification, so this
attempt supplies no measured retrieval nDCG and cannot qualify the common
starting reference.

| Observation | Original result |
| --- | --- |
| Completed trials / execution errors | 1 / 1 |
| Native job elapsed time | 3,649.14 seconds |
| Agent execution time | 3,600.09 seconds |
| Required ranking artifact | Missing |
| Verifier diagnostic | FileNotFoundError for the ranking artifact |
| Verifier phase timing | Unavailable |
| Native reward field | 0.0, associated with the failed attempt |
| Measured retrieval nDCG@10 | Unavailable |
| Automatic retries | 0 |
| Tokens and native cost | Unavailable |

The maintained Harbor reporter validates the completed original artifacts and
reports one agent error and zero ordinary verifier-failed trials. It also
preserves the supplied reward field of zero. The archive retains that zero in
its mean and observed-mean fields. Those values do not establish a measured
zero retrieval score: the verifier diagnostic explicitly says the required
ranking was missing, and qualification fails.

Absent verifier phase timing does not mean the verifier never ran. Its
diagnostic and reward files are preserved. The agent execution log and inner
build progress are unavailable, so this evidence does not identify the last
completed construction or query phase. The timeout alone does not establish a
memory failure or external outage.

The [source-bound aggregate](aggregate.json) preserves the original job,
trial, maintained report, missing-ranking diagnostic and settled owner archive
through 13 exact file hashes. This report launches no job, changes no timeout,
retries no result and assigns no new variant or native allowance.

## Remaining work

Seven earlier starting roles remain qualified. Entity Graph and
[Ensemble](../ensemble-memory-001/README.md) now have distinct completed
execution failures. The remaining original Graphify and Turso measurements
continue under the unchanged controller. A valid all-eight reference, five
remaining family searches, joint replay, all-500 comparison and independent
acceptance remain unfinished.

Any efficiency correction needs its own prospective construction treatment,
complete original inputs and validation, preserved historical charges and
explicit accounting within the existing limits. Keep these errors separate
from semantic misses and preserve the eventual starting-gate failure.

[E11 continuation](../README.md) ·
[Family evidence index](../../../../../docs/enterprise-family-report-index.md) ·
[Earlier qualified starting comparisons](../starting-progress-002/README.md)
