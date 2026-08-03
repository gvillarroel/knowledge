---
adr: "0097"
title: "ADR 0097: Retain Classical Token-Efficiency Learning Without Promoting Failed Candidates"
summary: "Merge the comparative learning and safe aggregates while keeping rejected candidates, traces, and detailed local metrics under an ignored evaluation boundary."
status: "Accepted"
date: "2026-08-03"
product: "knowledge"
owner: "Platform Architecture"
area: "Evaluation Operations"
tags: [knowledge, classical, consultation, tokens, harbor, negative-evidence]
---

# ADR 0097: Retain Classical Token-Efficiency Learning Without Promoting Failed Candidates

## Status

Accepted. No lower-token Classical consultation candidate is accepted or
promoted by this decision.

## Context

The Classical token-efficiency lineage tested compact navigation, bounded
reading, prompt-only controls, terminal compilation, lossless source blocks,
one-shot complete-record hydration, exact terminology policies, and
claim-local semantic guards.

Some complete runs reduced native tokens by approximately 77% to 99% against
their matched canonical controls. Those savings were real, but the candidates
failed required mechanical, semantic, robustness, or cross-case gates. Other
attempts stopped before provider use or produced no assistant response. The
final V30 development search stopped without a winner at ledger sequence 298;
validation and holdout remained sealed and unreleased.

The raw candidate bundles, jobs, traces, responses, diagnostics, and detailed
failure evidence are useful for future work but are not safe or appropriate
repository publication artifacts. Losing them would encourage repeated failed
experiments, while committing them would violate the evaluation privacy and
Git-boundary contract.

## Decision

Merge only the following durable learning to `main`:

- the reviewed complete attempt ledger;
- a concise lessons document that distinguishes token leadership from
  acceptance and ranks future reuse priorities;
- the V30 study `.gitignore`, generated publication indexes, and one reviewed
  aggregate token table; and
- this decision record.

Keep every rejected candidate bundle, native job, trace, response, diagnostic,
and local machine-readable failure archive outside Git. Store the consolidated
R15-R25 pointer archive under the shared ignored `processed/` boundary. Bind
each pointer to the exact candidate tree, candidate manifest, and decisive
audit SHA-256 instead of duplicating the candidate bundle.

Use R21 as the first semantic hypothesis in a future study, R17 as the
lowest-token comparator, and R23 as the literal-pair stress case. Treat R20,
R18, and R16 as secondary ablations. Do not retry R15, R19, R22, R24, or R25
as-is.

Any future implementation requires a new organized study with a newly
precommitted development design and fresh sealed validation. V30 may not be
resumed, retried, or used to open its sealed validation or holdout.

Do not modify `skills/consult-semantic-okf-classical` as part of this merge.
The canonical skill remains the production baseline until one frozen candidate
passes token, mechanical, independent semantic, validation, and holdout gates.

## Consequences

Positive:

- future work can begin from the strongest observed hypotheses instead of
  repeating the complete failed search;
- the repository exposes why the token leaders were rejected;
- the ignored local archive preserves exact reusable identities without
  publishing raw evaluation artifacts; and
- the production skill and sealed evaluation boundaries remain unchanged.

Negative:

- a fresh clone receives the learning and safe aggregates, but not the local
  rejected bundles or raw evidence;
- V30 establishes only a one-case token ordering for R16-R23, not a
  multi-query average; and
- the most promising next treatment remains a hypothesis until a new study
  completes every gate.

## Evidence

- `docs/classical-consultation-token-efficiency-lessons.md`
- `evaluations/semantic-okf-datasets/reports/20260802-classical-token-optimization-attempts.md`
- `evaluations/semantic-okf-classical-token-efficiency-study-v30/publication/index.md`
- `evaluations/semantic-okf-classical-token-efficiency-study-v30/publication/tables/v30-development-token-screen.table.md`
- local ignored archive:
  `evaluations/semantic-okf-datasets/processed/classical-token-efficiency-failed-options-v30/`
