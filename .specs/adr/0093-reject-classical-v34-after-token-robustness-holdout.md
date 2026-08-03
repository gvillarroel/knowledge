# ADR 0093: Reject Classical v34 After the Token-Robustness Holdout

## Status

Accepted on 2026-07-31.

## Context

ADR 0092 rejected three Classical compact-navigation candidates because their
token savings came with case-level quality regressions. A new one-way study
used six clause-diverse quantum-error-correction development tasks and six
disjoint holdout tasks. The baseline and every candidate used Pi 0.73.1,
`openai-codex/gpt-5.3-codex-spark`, high thinking, and the same frozen Classical
snapshot.

The study tested query-focused dual evidence, a smaller candidate pool,
rank-budgeted paper-wide detail, compact guardrailed guidance, and two minimal
role-distinction prompts. The frozen automatic policy required zero candidate
errors, no case-level metric regressions, a lower median, an acceptable mean,
and strict token reduction in at least five of six cases. Every isolated answer
was also reviewed against its paired baseline answer.

Version 34 was the only development candidate to pass the automatic gate and
the pairwise semantic non-regression review. It reduced development mean tokens
from 16,670.5 to 13,214.8 (-20.73%), reduced the median by 21.43%, and used
fewer tokens in five of six cases. It improved strict semantic completeness
from three to five cases and introduced no pairwise semantic regression.

Versions 35 and 36 attempted to repair the remaining role distinction. Version
35 retained the omission. Version 36 produced one-character summary and claim
placeholders after repeated invalid submissions; the mechanical verifier still
awarded a perfect score because its evidence references were valid.

On the untouched holdout, v34 preserved answer quality in all six manual pairs
and had no registered mechanical quality regressions. It reduced mean usage
from 23,614.8 to 21,499.8 (-8.96%) and the median from 13,168.5 to 11,305.5
(-14.15%), but reduced tokens in only four of six cases. Its q027 trajectory
spent 72,473 tokens after listing skills and reading the query and terminal
extension implementations before issuing the bounded query. The baseline
showed the same exploration failure mode on q030 at 67,202 tokens.

## Decision

Do not promote v34 or any later prompt-only candidate to
`skills/consult-semantic-okf-classical`.

The holdout result fails the frozen five-of-six token-reduction requirement.
Aggregate mean and median savings and complete semantic non-regression do not
override a predeclared failed gate. Preserve v34 as experimental evidence and
leave the canonical Classical skill unchanged.

Do not continue prompt-only mutation on the released holdout. A future study
may test a structurally constrained consultation runtime that:

- preloads the selected consultation instructions before the first model turn;
- exposes dedicated bounded query and terminal-submission tools only;
- makes implementation discovery unavailable rather than merely prohibited;
- rejects semantically empty one-character summaries and claims; and
- uses a new one-way development and holdout split.

## Consequences

- Bounded paper sections and compact guidance are supported as useful token
  reductions, but they are not yet reliable enough for production promotion.
- The best candidate preserved semantic quality, so the remaining blocker is
  tool-path robustness rather than evidence sufficiency.
- Manual answer review remains mandatory because evidence-valid structural
  metrics accepted a semantically empty v36 response.
- No post-hoc policy relaxation, failed-run deletion, holdout reuse, or
  canonical skill mutation is allowed.
- Aggregate results are published in
  `evaluations/semantic-okf-classical-token-efficiency-study-v4/publication/tables/classical-token-efficiency-v34.table.md`.
