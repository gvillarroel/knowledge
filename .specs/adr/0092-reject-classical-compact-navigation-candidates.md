# ADR 0092: Reject Classical Compact-Navigation Candidates That Regress Case Quality

## Status

Accepted on 2026-07-31.

## Context

ADR 0091 showed that Classical consultation consumed a mean of more than one
million native tokens per query in the historical common cohort, while its
builder used only a few thousand tokens per generated folder. A trace audit
found that repeated Classical searches emitted full passage text and ranking
diagnostics many times. Direct whole-file reads contributed additional
context, but were not the primary source of tool output.

The Classical builder and its deterministic retrieval ranking were frozen.
Three consultation-only candidates were realized from sealed parents and
evaluated on the same six GraphRAG development questions with Pi 0.73.1,
`openai-codex/gpt-5.3-codex-spark`, high thinking, the same bundle, and the same
verifier. The predeclared policy required zero candidate errors, no decrease
in any of thirteen case-level quality metrics, at least a 20% mean native-token
reduction, a lower median, and strict token reductions in at least five of six
cases. Cached input remained a reported subset of input and was not added
twice.

The candidates preserved the legacy full search payload byte-for-byte and
kept the ranking implementation unchanged. Compact search reduced one
representative 51,150-character payload by about 70% and bounded reads emitted
only selected validated sections.

## Decision

Do not promote any compact-navigation candidate to
`skills/consult-semantic-okf-classical`.

- Version 1 reduced mean native tokens by 52.0% and removed the baseline
  timeout, but regressed seven case metrics, including evidence precision,
  ranking quality, reference validity, and response contract.
- Version 2 reduced mean native tokens by 69.8% with zero execution errors, but
  still regressed seven case metrics. Its failures exposed identifier
  normalization and insufficient document coverage despite exact local
  evidence-export support.
- Version 3 added snapshot-bound answer validation. It reduced mean native
  tokens by only 34.0%, timed out on one case, reduced tokens in only three of
  six cases, and regressed twenty-two case metrics.

Retain the canonical Classical build and consultation skills unchanged. Keep
all three sealed candidates, native Harbor jobs, reports, and decisions as
negative development evidence. Do not release or run the registered holdout
cohort because no candidate passed development selection.

A future treatment may reuse compact discovery and bounded reading only if it
can enforce exact evidence output without inducing correction loops. It must
start as a new sealed candidate and pass the same or stricter predeclared
quality non-regression gate before holdout.

## Consequences

- The user's large-file hypothesis is partly validated: limiting emitted
  sections materially lowers tokens, but tool-output reduction alone does not
  guarantee answer quality.
- No lower-token strategy is presented as accepted while any measured quality
  regression remains.
- The production builder, ranking implementation, and consultation skill do
  not change.
- The unreleased holdout remains uncontaminated by candidate selection.
- The evaluation now records mean, median, per-case input, cached input,
  output, total tokens, errors, and case-level quality regressions in reusable
  JSON and Markdown reports.
