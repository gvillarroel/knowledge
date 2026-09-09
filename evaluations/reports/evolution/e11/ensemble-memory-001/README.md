# E11 Ensemble: construction exceeded the 6 GiB memory limit

The original Ensemble starting job completed with one execution error before
producing a ranking. Preserved Docker events and kernel logs identify a memory
cgroup OOM at **20:59:19 UTC on September 9, 2026**. The kernel recorded memory
usage equal to the **6 GiB limit** and killed a Python process in that exact
job's container. This is a failure under the declared memory contract.

The [aggregate](aggregate.json) binds the native result, maintained Harbor
report, original execution log, settled owner archive and captured operating
system evidence to their exact source hashes.

| Observation | Original result |
| --- | --- |
| Completed trials | 1 |
| Execution errors | 1 |
| Verifier execution | Did not run |
| Retrieval nDCG@10 | Unavailable |
| Native job elapsed time | 484.69 seconds |
| Agent execution time | 455.54 seconds |
| Memory usage and limit at OOM | 6,291,456 KiB each |
| Automatic retries | 0 |
| Tokens and native cost | Unavailable |

The maintained Harbor reporter records reward as unavailable and classifies
the outcome as an execution error. The Pareto archive retains its native
error-accounting fallback mean of zero, but its observed reward is null and
its qualification fails. That fallback is **not a measured zero nDCG score**
and must not enter a quality ranking.

The preserved agent traceback locates the failure in the first
`build_semantic_okf_ensemble.py` command. The inner `knowledge-build.log` was
not collected, and the original container was subsequently removed. The exact
component and allocation site responsible for the memory peak remain unknown.
The kernel's `CONSTRAINT_MEMCG` record establishes the container memory limit
as the constraint; it does not establish an external provider outage or a
transient global-host-only failure that would justify an automatic retry.

## Effect on the study

The seven previously qualified starting roles and their
[reproduced Classical/Adaptive results](../starting-progress-002/README.md)
remain intact. The other preallocated starting jobs continue to settle.
The unchanged common starting gate cannot accept the failed Ensemble role,
so it cannot authorize new family variants or the final all-500 comparison.
The eventual gate result must be retained alongside this original failure.

The full 6,000-document workload, resource limits, inherited claims and
585-cumulative-variant cap remain unchanged. This report reruns no job,
authorizes no extra evaluation, releases no private data and installs no skill.
Host compute remains unpriced; unavailable telemetry is not zero cost.

## Next construction work

A source audit found that the ensemble runs core construction, three derived
projections and repeated validations in one Python process. Reclaiming
completed-stage state or isolating stages are hypotheses to investigate, not
proven fixes. A repair must preserve complete inputs, artifact identities,
ranking behavior, all validation checks and atomic publication while operating
within the same memory limit.

Any candidate and live measurement require a separately declared construction
treatment and reconciled use of the existing budgets. The sealed E11 attempt
must remain unchanged. The remaining searches, joint bundle replay, all-500
recalculation and independent acceptance are unfinished.

[E11 continuation](../README.md) ·
[Family evidence index](../../../../../docs/enterprise-family-report-index.md) ·
[Original startup checkpoint](../startup-001/README.md)
