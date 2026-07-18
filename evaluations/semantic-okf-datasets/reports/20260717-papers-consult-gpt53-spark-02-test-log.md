# GraphRAG Papers Consult Campaign 02 Test Log

## Purpose

Campaign `20260717-papers-consult-gpt53-spark-02` is the first live retry after
the evaluator audit invalidated campaign 01. It uses the corrected prompts,
hidden semantic rubric, provider-aware terminal classifier, and mechanical
grader. The intended matrix remains 40 questions by eight consult families.

This campaign is **not an evaluation result and is not ranking-eligible**. Its
counted preflight reached the provider's account usage limit, and the fair
scheduler stopped before submitting any additional cell.

## Frozen preparation evidence

| Check | Result |
|---|---|
| Schedule cells | 320 unique question/family cells |
| Schedule SHA-256 | `f202c3c8744cc8259fddce586826768c90e896c8c180a0b2e96a0a88aaf70f7d` |
| Corrected generated tasks | 40 per family, 320 total |
| Copied family bundles | 8 of 8 |
| Bundle-to-task-manifest bindings | 8 of 8 matched |
| Windows campaign dry run | Passed |
| WSL campaign dry run | Passed |
| Focused evaluator/runner/dataset tests | 27 passed |

The immutable bundle tree hashes used for the retry were:

| Family | Bundle tree SHA-256 |
|---|---|
| `adaptive` | `4305743103e3a2de5d80f3c74edb34f90fcf7a4a795fd7ba5d43289b75d133d6` |
| `classical` | `832a84d16df88546bb87b4114a6dc79cb87ba57bc540992ed6b25e7b9151dea1` |
| `embeddings` | `c1a70bee4acacdc11628d37abb4afeab34995b99ca06b3d1291ea43f6ae02420` |
| `ensemble` | `264acd347230b3a713da14ed208a28bb610157dc7c95d467e14512430332c6fa` |
| `entity-graph` | `c203e5d4ccd0ca94859c6b1bd3d8c529134d7405214396463cd5e95464cc88d1` |
| `graphify` | `8bf748d947b105a1f786b0f4c1df2dc5552260b290cf9960600fc55454828bf5` |
| `legacy` | `8f127d26cacded575478b7871e1031f73a849f98f92297631b93fc3f17b3d405` |
| `turso` | `b50a439dacac90517038124695339a6ee053d6b0a03bebe57c751b96f99f7dbd` |

## Counted live preflight

The scheduler launched only sequence 1, `adaptive/discovery/q001`, at
`2026-07-17T22:18:31.306416+00:00`. Harbor itself exited zero, but the raw Pi
trace ended with provider code `usage_limit_reached`. The provider-aware run
receipt therefore correctly recorded `run_status=provider-failure`, an
effective runner exit of 2, and terminal outcome `provider-quota`.

The scheduler wrote its aborted checkpoint at
`2026-07-17T22:20:02.778407+00:00` with exactly one completed cell. No second
cell was submitted. The provider supplied a reset instant of
`2026-07-23T14:24:32+00:00` (`2026-07-23T10:24:32-04:00`) with `489909`
seconds remaining when the terminal error was emitted. The durable trigger
uses the allowlisted shape `provider_reset.at` and
`provider_reset.remaining_seconds`. Raw provider error text, headers,
credentials, answers, and unrelated provider metadata are intentionally not
reproduced here.

| Outcome | Count |
|---|---:|
| `provider-quota` | 1 |
| Evaluable final responses | 0 |
| Unsubmitted scheduled cells | 319 |

## Provider reset metadata hardening

The terminal classifier now derives the reset only from the structured
`usage_limit_reached` error body. It ignores reset-like headers and persists
only the canonical nested `provider_reset.at` and
`provider_reset.remaining_seconds` fields. Campaign outcomes use an explicit
field allowlist, and aborted checkpoint triggers copy the same sanitized
object. The original ignored campaign outcome and checkpoint remain immutable;
the tracked checkpoint above records the newly standardized representation.

The immutable campaign 02 trace was reclassified successfully, and the
forensic campaign summarizer continued to accept the historical generated
outcome and checkpoint that predate this optional field. Focused reset,
runner, grader, dataset, and campaign-summary tests passed `38/38`. The
repository coverage gate passed `718` tests with `90.9%` application coverage,
and both pinned dataset descriptors validated across all eight strategy
families.

The current-grader rescore is preserved in the
[`forensic Markdown report`](20260717-papers-consult-gpt53-spark-02-forensic.md)
and [`forensic JSON report`](20260717-papers-consult-gpt53-spark-02-forensic.json).
It records one provider-quota attempt, zero evaluable responses, 319 missing
cells, no ranking, and no winner. The same campaign exits nonzero under strict
summarization with the explicit incomplete-campaign diagnostic.

## Interpretation and next retry

This attempt validates the corrected abort behavior, not any consult family.
It must not be merged with campaign 01 or used to compute a winner. The local
Codex and Pi credentials resolve to the same account, so refreshing or
translating the newer local token cannot change this account-level reset.

Create campaign 03 only after the campaign input-binding hardening is in place.
At or after the provider reset, run one counted synchronous preflight under the
same pinned model. If it succeeds, continue the complete balanced 320-cell
schedule; if it fails, preserve the new aborted campaign append-only and do not
combine its cell with another attempt.
