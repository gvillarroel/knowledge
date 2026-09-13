# ADR 0164: Close E15 after independent preparation rejection

Status: Accepted for terminal closure and reporting only.

Date: 2026-09-13.

## Context

[ADR 0162](0162-terminate-e14-and-register-e15-before-prospective-qualification.md)
requires an independent eligibility review before E15 may execute. Registering
the previously unreleased private portfolio did not establish its nonexposure
or access isolation. The independent curator found that the private source
inherits workspace permissions that permit access by the optimizer's host
identity. Historical custody receipts describe a trusted-host convention and
container probes; they do not establish the required host access boundary.

This is a failed preparation review. It is neither a private quality-gate
failure nor evidence that private questions were scored or consumed. E15 has
not been sealed, started a native measurement, or released validation.

The maintained `harbor-organize-evaluations` reference,
`references/study-design-and-leakage.md`, requires an isolated evaluator context
or service and states: "`.gitignore`, SHA-256 locks, and a reviewer's name do not
implement filesystem permissions or prove that an optimizer has not seen the
data." The existing environment does not satisfy that requirement.

Public source review also narrowed the earlier preflight claim. The prepared
runtime has ledger primitives and a two-family first-measurement adapter, but
does not implement the remaining search and finalization driver. Its native
concurrency bound is process-local, and admission does not hold a lease through
allocation. Dry-run configuration checks and 18 passing unit tests do not prove
that the complete execution contract is implemented.

## Decision

Stop all four planned E15 stages through the maintained organizer's legal
`planned -> stopped` transition. Bind the independent safe rejection receipt
and closure decision by path and SHA-256 in each transition note. Do not start
a stage merely to attach evidence: the evidence API requires a running or
blocked stage, while E15 has no authority to run. Preserve the original ledger
prefix, datasets, candidate trees, preflight sources, and historical receipts.

Verify the terminal ledger and publish a closure receipt with no next action,
no release, and no new native allocation. The stopped publication stage refers
to the planned accepted-candidate result; it does not prohibit publishing this
administrative failure report and already reviewed historical aggregates.

Keep six qualified development results and both unavailable families visible.
Report the original workload, exact metric, original evidence bindings, and
descriptive application and cost/time comparisons. Do not interpret catalog
stops as proof that every possible strategy was exhausted. Do not turn timeout
or memory failures into zero scores or quality misses.

The paired all-500 recalculation remains unexecuted: its declared prerequisites
were all-eight qualification, joint replay, and one whole-bundle freeze. Do not
substitute a new six-family run or a report-only operation for those gates.
The earlier complete Classical full-corpus retrieval and Luna answer evaluation
remain separate historical treatments with their own metric and corpus labels.

Supersede current-facing preflight and registration status with this terminal
outcome. Preserve their dated aggregate bytes and actual passing diagnostics;
correct the inference that those diagnostics established complete execution.
No E15 candidate is promoted to canonical skills or installed by this closure.

## Consequences

This campaign ends with a partial measured comparison and an explicit failed
preparation outcome. It does not satisfy the requested final eight-family
all-500 evaluation. There is no pending E15 activation or automatic restart.

A later attempt needs an operationally isolated evaluator and optimizer,
denied-access evidence from the actual contexts, and a new study with fresh
private data where historical nonexposure cannot be established. Its public
runtime must implement and verify the complete finite search, cross-process
allocation, joint replay, freeze, comparison, and one-way acceptance path before
independent review and sealing. Changing permissions after this rejection
cannot retrospectively establish that the old portfolio was unseen.

The [terminal report](../../evaluations/reports/evolution/e15/terminal-001/README.md)
and [machine-readable aggregate](../../evaluations/reports/evolution/e15/terminal-001/aggregate.json)
own the final evidence bindings, measured tables, and completion limitations.
