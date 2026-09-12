# Distinguish catalog stops from historical hypothesis coverage

Status: Accepted

Date: 2026-09-12

## Context

A native family can finish after its last scored progress record. The
controller may skip duplicate profiles and close a full round without
dispatching another evaluation. Reading only the last progress file can
therefore misreport a completed catalog as open.

A terminal catalog can also retain an unavailable historical hypothesis.
A recorded stop, a qualified retrieval reference, and complete historical
measurement coverage are separate facts.

[ADR 0157](0157-normalize-complete-enterprise-native-prefixes.md) requires
complete native histories before metric publication. This decision extends
that reporting boundary to terminal catalog accounting; it changes no
evolution controller, scorer, candidate, or admission policy.

## Decision

1. Bind a terminal family record to its original owner, frozen runtime,
   complete normalized native prefix, common reconciliation, and published
   metrics. Check the final archive, config, retained winner and exact state.
2. For callback-only closure, replay the existing scheduler in memory from
   the last verified prefix. Permit only already-seen duplicate skips and
   terminal transitions. Reject an unseen profile, pending or failed attempt,
   changed state schema, different stop reason, or changed native winner.
   This reporting replay must not issue a claim, evaluate a candidate or
   mutate native artifacts.
3. Publish separate counts for catalog stops, qualified references and
   historical measurement limitations. Preserve unavailable fitness and
   explicit no-reissue decisions. Do not infer complete hypothesis coverage
   or promotion from a terminal status.
4. Count closed unused allowances from verified terminal family states.
   Preserve older snapshots and their original denominators. Never transfer
   closed allowances or interpret a reservation as a completed quality trial.
5. Distinguish already-issued historical pending measurements from actual
   outstanding work. The owner's legacy `pending_first_measurements` summary
   counts issued identities; the terminal state's `pending` and `active`
   fields determine whether an attempt remains unresolved.

## Evidence and limits

The [five-family inventory](../../evaluations/reports/evolution/e14/opportunity-accounting-002/README.md)
binds 461 sources. It verifies three duplicate skips after Turso's last native
observation and six after Adaptive's; each closure adds zero proposals and
zero native observations. Adaptive and Classical each preserve one historical
hypothesis with unavailable fitness.

Seven focused tests passed, including original terminal-state equality and
rejection of premature closure, unresolved attempts, budget mislabeling and
schema drift. Application gate 057 passed 1,643 tests and 373 subtests at
90.5% total coverage with process exit zero.

The fixed audit, verification receipt and source commitments remain in ignored
local evaluation storage. The repository keeps the reviewed aggregate and
documentation. Five catalog stops do not complete the eight-family study,
all-500 comparison, independent acceptance, or any promotion gate.
