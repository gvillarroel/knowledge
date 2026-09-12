# Normalize complete Enterprise native histories before publication

Status: Accepted. Date: 2026-09-12.

## Context

Enterprise E14 publishes successive completed development observations while
the original controller continues its finite search. Handwritten reporting
commands repeatedly enumerate each family's native job history. Omitting a
dominated candidate or importing a different baseline would change the evidence
behind the comparison even if the newest result looked plausible.

[ADR 0116](0116-local-enterprise-rag-dataset-and-aggregate-report-hub.md)
keeps native artifacts local and publishes reviewed aggregates. The existing
prefix loader and common reconciler remain responsible for owner accounting,
metric reconciliation and source binding. This decision concerns the native
reporting step between them; it introduces no evolution controller or scorer.

## Decision

1. Wait for the original completed archive, dispatch receipt and progress
   record. Use the existing loader to replay accounting and capture the exact
   completed prefix. Pass its explicit SHA-256 to the reporting helper.
2. Require contiguous generation history, unique candidate and job identities,
   complete candidate order, all original starting roles and exact cumulative
   counts. Preserve dominated candidates. Permit only the family's E14 jobs
   and the already registered original E13 Turso baseline at its original
   position. Never rerun or remap that baseline.
3. Check the bound execution contract, owner records, native configs, locks,
   results and reporter implementation before execution. Reject digest drift,
   path escapes, links, cross-family jobs and previously used output paths.
   A read-only check must create no output or subprocess.
4. Invoke the pinned `harbor-run-results` reporter once, using an explicit
   argument vector, a 300-second timeout and zero retries. Preserve the full
   native job order. Check report completeness and comparison compatibility,
   then recheck source and reporter digests. Its reporting threshold does not
   replace the study's family qualification rule.
5. Preserve an append-only start receipt, output streams and either a success
   or failure receipt. A failed output path stays consumed. No reporting error
   authorizes a native rerun, a candidate change or a quality-miss charge.
6. Continue through the unchanged common reconciler and publication audit.
   Normalization alone does not publish, select or promote a skill, establish
   producer authorship, or prove that an independently supplied prefix is
   authentic. The witnessed loader operation and original owner evidence
   remain necessary.

The first implementation and its evidence remain in ignored local preparation
storage under `tmp/enterprise-next-preparation/e14-native-normalization-001/`.
It is specific to the frozen E14 contract. Reuse its verified bytes for later
completed prefixes; changes require a new version and fresh verification.
Do not modify the running controller, consume private validation, reset
budgets, or copy this study-specific helper into a knowledge skill.

## Verification

The helper passed 18 unit tests on Windows and the same 18 on WSL. Checks cover
omitted dominated history even when totals are adjusted, duplicate identities,
reordered generations, invalid generation values, missing locks and owner
records, source and reporter drift, path scope, output preservation, failed
subprocess evidence and successful artifact verification.

The unchanged implementation normalized two complete native histories:

| Completed prefix | Original native records | Historical imports | Newly dispatched native jobs |
| --- | --- | --- | --- |
| [Turso generation 11](../../evaluations/reports/evolution/e14/turso-generation-011-001/README.md) | 13 | 1 original E13 baseline | 0 |
| [Adaptive generation 9](../../evaluations/reports/evolution/e14/adaptive-generation-009-001/README.md) | 11 | 0 | 0 |

Both common reconciliations passed, each retained comparison reproduced all
20 application/category/overall groups, and both publication audits passed.
These are artifact-processing integrations over previously completed native
records, not new task executions or independent quality samples.

Application coverage gate 056 ran
`python scripts/check_coverage.py --threshold 80`: 1,643 tests and 373 subtests
passed, the process exited zero, and total application coverage was 90.5%.
The test summary and coverage result were both reviewed as required by
[ADR 0146](0146-preserve-pytest-exit-status-in-coverage-checks.md).

## Consequences

Later observations use the same tested normalization procedure while keeping
the original reporter, accounting replay and reconciliation boundaries.
Reporting becomes less dependent on manually assembled job lists. This change
establishes no retrieval gain, runtime speedup, all-500 result, generated-answer
score or skill promotion. Native histories and operational receipts remain
local; the linked reviewed reports remain the repository's public evidence.
