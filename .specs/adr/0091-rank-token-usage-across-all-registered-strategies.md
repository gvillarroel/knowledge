# ADR 0091: Rank Token Usage Across All Registered Strategies

## Status

Accepted on 2026-07-30.

## Context

ADR 0090 separated construction tokens per generated knowledge folder from
consultation tokens per submitted query. The first report could only compare
two builder implementations and a six-family consultation pilot. Those rows
were useful diagnostics, but they did not answer which of the eight registered
Semantic OKF strategy pairs used the most or least tokens.

The repository already retained a common six-question consult-only cohort for
Adaptive, Classical, Embeddings, Ensemble, Entity Graph, Graphify, Legacy, and
Turso. Every family used the same GraphRAG corpus, question IDs, model, Pi
version, and thinking level. Repeating those 48 calls would spend quota without
adding a new comparison unit. No equivalent same-contract builder evidence
existed for all eight families.

The repository also reports 25 deterministic direct-retrieval routes. Those
helpers do not call an LLM, but a later grounded answer-generation agent may
still consume tokens. Treating the helper's zero-token cost as the cost of a
complete consultation would conflate two different units.

## Decision

Create a frozen, append-only builder token study for all eight registered
families with:

- the `graphrag-papers-40` staged input;
- Pi 0.73.1 and `openai-codex/gpt-5.3-codex-spark` with high thinking;
- one content-addressed runtime image;
- two independent agent calls per family;
- exactly one folder per call, for two generated folders per family;
- exact record identity, validation, family projection, cross-replicate
  inventory equality,
  command coverage, and workflow-safety gates; and
- no retries after a submitted cell.

Schedule the two replicates in balanced family waves. Stop new submissions
after the first execution error. Treat each call's input-plus-output tokens as
the cost of its single generated folder. Keep cached input as a reported subset
of input, not an additional term.

The superseded two-folder-per-call rehearsal was stopped when Embeddings
exceeded the Bash tool limit before completing its first folder and the agent
started a forbidden second invocation. A subsequent rehearsal showed that a
valid same-record folder did not have byte identity with the historical bundle
produced in a different environment. A single-folder call avoids hidden
orchestration amortization and permits the slowest builder a dedicated
timeout; reproducibility is established only by comparing the two independent
same-environment replicate inventories.

For consultation, reuse only the six common holdout question IDs that have
positive native token observations for all eight families. Rank submitted
query cost with runtime failures retained in the denominator. Publish a
separate zero-runtime-error comparison so an early-failing method cannot be
recommended merely because it stopped before consuming more tokens.

List all 25 deterministic retrieval routes with zero LLM calls and zero LLM
tokens per helper invocation. State explicitly that this unit excludes any
later answer-generation agent.

Do not add construction and consultation tokens into one methodology score.
Preserve the earlier cross-model builder rows, controlled consultation pilot,
and uneven GraphRAG response archive only as supplemental diagnostics.

## Consequences

- Every registered build and consult family appears in the primary token
  tables.
- The most- and least-expensive construction methods are based on equal
  builder-call and generated-folder denominators.
- The consultation table exposes both consumed tokens and reliability.
- Existing comparable consultation traces avoid 48 unnecessary model calls.
- Direct retrieval's zero LLM-token cost remains accurate without understating
  complete answer-generation cost.
- The reused consultation campaign has a weaker runtime provenance boundary
  than the new builder study because it predates campaign input-binding
  version 2; the report must retain that limitation.
