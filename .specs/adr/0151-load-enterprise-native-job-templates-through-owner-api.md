# Load Enterprise native job templates through the owning API

Date: 2026-09-11.

Status: Accepted for prospective source correction. It does not authorize
restarting E12 or dispatching a new native job.

## Context

The [E12 terminal report](../../evaluations/reports/evolution/e12/preallocation-failure-001/README.md)
records a controller failure before any native allocation. The pinned Pareto
owner returns paths in `normalize_config`, whereas the adapter expected a
model with `model_dump`. The existing synthetic integration tests substituted
that assumed model shape and therefore did not detect the mismatch.

## Decision

Load the normalized path with the pinned owner's `load_job_template` before
serializing or signing the returned `JobConfig`. Preserve the original
normalized config and its path fields for `run_candidate_jobs`; the native
runner continues to own execution.

Test this adapter boundary against the actual pinned normalization, loader
and signature APIs. Use public declarations and explicitly synthetic execution,
admission and persistence for software checks. Exercise the private-phase
branch only with invented test input outside the sealed private portfolio.
Do not replace the actual normalization return type with an assumed test double.

Preserve the failed sealed invocation and close its stages through the native
organizer. Any corrected executable controller requires a separately versioned
continuation with the existing design and custody process. This correction
does not reopen a stopped study or alter task content, workloads, limits,
proposal counts, measurement identities, selection or acceptance rules from
[ADR 0150](0150-continue-enterprise-searches-by-family-readiness.md).

## Evidence and consequences

Nine integration tests passed with Harbor 0.18.0, including reproduction of
the original error and success of the isolated corrected adapter. The tests
preserve singleton owner calls, admission before each allocation, shared stop
behavior, one attempt and zero automatic retries. The native executor was
replaced with a test spy, so this evidence establishes software compatibility
at the checked boundary, not benchmark quality or execution admission.

All cumulative family opportunities and unopened private gates remain intact.
E12 generated no score, quality miss, new proposal claim or consumed first
measurement. Its failure cannot count as an unsuccessful retrieval strategy.
