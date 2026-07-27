# Tika/MALLET/Tantivy consultation trace-distillation status

Date: 2026-07-23

## Outcome

No candidate was promoted. The source
`consult-semantic-okf-tika-mallet-tantivy` skill remains unchanged at
`sha256:263701cf37b49448b76413bd58fe7f5ee129ec01c264c89f70b1bb67392504ba`.

The v1 Harbor job yielded four complete, evaluable semantic observations before
the provider stopped emitting first events for later concurrent trials:

- q001 and q004 exhausted the 600-second agent budget after 38 and 36 tool
  calls;
- q002 and q003 emitted exact, contract-valid answers but failed the minimum
  document gate with seven and six evidence rows.

The job was stopped with 15 tasks still pending because two further trials
timed out with zero tokens. Since schema 2 requires a complete whole-job
zero-retry artifact, the partial job is not promotion evidence.

## Analyze-only distillation

A schema-1, analyze-only import of the four completed semantic trials accepted
two trace-backed patches:

- `seal-bounded-evaluation-workflow`
- `map-required-coverage-to-facet-diverse-queries`

The staged candidate digest is
`sha256:17e3f8b26c3d12d2ea6b1558d35909fb565582ea4c7e3d7f2de54d3bee63ba8a`.
It passed skill-package validation and runtime preflight. Analyze-only excludes
candidate development and holdout, so this is a proposal artifact, not a
publishable winner.

## External blocker

The original OpenAI Codex profile returned `usage_limit_reached` before a token,
with reset reported for 2026-07-29. A separate GitHub Copilot profile initially
completed one qualified preflight, then later returned `429 quota exceeded`
across both GPT and Claude model families. The round-2 two-task preflight was
cancelled without evidence, and all temporary authentication staging was
removed.

The next permissible action is a new append-only provider preflight. If it
succeeds, run a complete schema-2 discovery job, independently replay the
candidate on the exact same tasks, and open the disjoint holdout only after
candidate development passes.
