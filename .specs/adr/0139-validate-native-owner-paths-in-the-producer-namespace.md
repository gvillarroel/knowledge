# ADR 0139: Validate native owner paths in the producer namespace

Date: 2026-09-10 UTC

Status: Accepted for the narrow prospective control correction. Actual
successor execution still requires its registered design and current admission.

## Context

The ordinary construction evaluation passed its complete pre-allocation
callback, then both workers were refused before reserving native attempts.
The callback and worker paths reached different metadata states: the first
had no dispatch record; the later controls imported the worker's complete
dispatch validator into Windows and read the persisted Linux owner.

The shared validator used `Path(executable).is_absolute()`. Windows therefore
rejected the actual Linux executable. The identical persisted owner and batch
passed under Linux. The original refusals retain a generic code, so the
specific defect is a later source-bound reproduction rather than recovered
original exception text.

## Decision

Validate native Linux executable syntax with `PurePosixPath`, independently of
the reviewing host. Change only that check and its import. Do not resolve the
native executable against the Windows filesystem, normalize the persisted
string, rewrite an identity or add a fallback. Preserve the original Linux
absolute-syntax policy and the separate `/proc` identity comparisons for PID,
UID, process start, executable and command digest.

Exercise the same shared validator from complete dispatch, attempt and terminal
control paths on both actual host runtimes. Include a persisted post-dispatch
case, since a successful pre-allocation callback cannot test a branch that
returns early until the dispatch record exists. Synthetic lifecycle metadata
tests establish comparison behavior; actual runtime identity and native
qualification still require their original controls.

Preserve the stopped predecessor, original generic refusals and consumed
dispatcher. Its two native first measurements remain unconsumed because both
workers failed before attempt creation. A separately versioned ordinary
successor retains the same candidate bytes, task paths, resource limits,
qualification rules and first-measurement identities. Bind the old terminal
state and reject later old allocations. Reuse unchanged correctness evidence
by digest instead of repeating candidate or historical benchmark work.

This follows the prospective preservation rules in
[ADR 0136](0136-read-native-trial-configurations-with-authenticated-defaults.md)
and construction accounting in
[ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md).
The correction creates no new proposal, retry entitlement, semantic miss,
private release or permission to change selection from private feedback.

## Evidence and limits

The isolated implementation has two changed lines and exact full-source
reverse parity. Its 76 Windows and 95 Linux checks cover the persisted batch,
both families' synthetic attempt and terminal records, protected-field
refusals and original Linux-policy parity. An independent review authenticated
those checks and the stopped predecessor without rerunning them. Its directory
digest is `d08be004c1c2d40588bc9dbc474e18b316135eeda793a0a4944450f5d68fa559`.

The [published construction report](../../evaluations/reports/evolution/e11/construction-owner-portability-001/README.md)
preserves the measured 363.287-second callback, failed workers, zero native
allocation, seven-event terminal ledger and unchanged 83-of-585 accounting.
Neither the metadata correction nor its tests establish a new EnterpriseRAG
score, full-workload feasibility, final all-family ranking or skill promotion.
