---
adr: "0026"
title: "ADR 0026: Bootstrap the Definitive Skill Through a Digest-Bound MCP Tool"
summary: "Load the frozen treatment skill through one profile-gated MCP call, disable the general shell for that treatment, and attest the complete five-tool sequence."
status: "Accepted"
date: "2026-07-15"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - skill-bootstrap
  - mcp
  - runtime-isolation
  - quality-gates
  - skill-arena
---

# ADR 0026: Bootstrap the Definitive Skill Through a Digest-Bound MCP Tool

## Status

Accepted.

This decision extends ADR 0015, ADR 0023, ADR 0024, and ADR 0025. It changes only
how the isolated treatment receives its frozen consultation instructions and how
general-purpose shell access is constrained. The authoritative Semantic OKF core,
retrieval policy, reviewed benchmark, evidence-coverage gate, prepared-answer
envelope, digest confirmation, and exact host publication remain unchanged.

## Context

Skill Arena installs each selected skill and tells Codex its identity and path, but
does not inject the complete `SKILL.md` body into the model context. A faithful Codex
run therefore normally reads that file through the shell before following it.

The first complete MCP v1.4.0 comparison attempt reached 16 of 90 planned answers.
One treatment row performed exactly that bootstrap read before using the governed
MCP workflow. The read was successful and the subsequent inspect, coverage,
prepare, confirmation, and publication transaction succeeded, but the frozen trace
attestor correctly rejected every treatment shell command. The runner was stopped.
That partial execution is a rejected isolation diagnostic and contributes no answer
quality or causal metric.

Allowing an arbitrary shell merely to read one fixed file would widen the treatment
surface. Disabling the shell from process start without another instruction channel
would also prevent faithful skill activation. Skill Arena V1 has no per-profile
agent override in one Cartesian compare, so a global `features.shell_tool: false`
setting would alter both controls as well.

## Decision

Use MCP runtime v1.5.0 and make skill activation an explicit part of the definitive
consultation capability:

1. Add `semantic_okf_bootstrap_skill` as the first public treatment tool. It accepts
   no arguments and resolves only
   `$CODEX_HOME/skills/consult-semantic-okf-ensemble/SKILL.md`.
2. Require that path to remain inside the resolved `CODEX_HOME`, identify a regular
   non-link file, decode as strict UTF-8, and match the manifest-bound raw-byte
   SHA-256 and byte count. The server returns the exact body in the closed
   `semantic-okf-skill-bootstrap/1.0` envelope with ordered keys `schema`,
   `skill_id`, `skill_sha256`, `byte_count`, and `skill_markdown`.
3. Permit exactly one successful bootstrap per treatment session. It must be the
   first Semantic OKF call. Replay, binding failure, or any consultation call before
   bootstrap fails closed and poisons that session.
4. After bootstrap, retain the accepted sequence: one successful inspect, every
   required coverage page in order, one or more clean preparations, and exactly one
   terminal digest confirmation.
5. The shared host wrapper detects only the exact ensemble-treatment skill identity
   from the closed `SKILL_ARENA_ALLOWED_SKILLS` environment contract and starts Codex
   with its general shell tool disabled. Knowledge-only and adaptive controls retain
   the shared baseline command behavior.
6. The independent trace attestor requires the bootstrap envelope and frozen skill
   binding, the full five-tool order, zero treatment command-execution events, zero
   Semantic OKF calls in controls, exact confirmation receipts, and byte-identical
   host publication. No quality score compensates for a failed isolation gate.

The isolated comparison estimates the effect of the complete definitive consultation
capability—frozen skill body, digest-bound bootstrap, profile-gated retrieval tools,
coverage and publication gates, and treatment runtime policy—not the effect of skill
prose alone. That estimand must be stated beside every causal result.

## Alternatives rejected

- Allow one broadly matched `Get-Content` shell command. Command-string allowlists
  remain more permissive and harder to bind than a pathless MCP operation.
- Disable shell globally in the shared variant. This changes the active controls and
  still gives the treatment no channel through which to load its skill body.
- Treat the skill catalog metadata as the full skill. Inspection showed that the
  catalog supplies identity and path, not the complete instructions.
- Inject the skill body by modifying the Skill Arena provider. That could be a future
  harness feature, but it expands the external evaluator and is unnecessary for this
  standalone package.
- Accept the partial v1.4.0 run after manually classifying its read as harmless. The
  frozen protocol did not authorize it, and post-hoc acceptance would weaken the
  isolation contract.

## Consequences

Positive:

- the treatment can load its exact instructions without a general filesystem tool;
- the skill bytes, runtime behavior, trace, manifest, and evaluation contract share
  one closed identity;
- every later treatment action remains inside the read-only Semantic OKF interface;
- controls remain operationally usable and expose no Semantic OKF tools; and
- rejected partial runs remain useful diagnostics without entering quality metrics.

Negative:

- a skill-body edit now requires coordinated regeneration of the bootstrap digest,
  runtime hashes, config manifest, trace attestor, and evaluation contract;
- the treatment includes a stricter tool policy than the controls, so results cannot
  be described as a pure skill-text ablation; and
- the added one-shot state and path checks require their own failure and replay tests.

## Acceptance boundary

Only a fresh 90-answer run created after this decision may supply definitive answer
metrics. It must pass deterministic config regeneration, runtime and publication
tests, independent five-tool trace attestation, evidence-valid answer preparation,
blinded semantic review, compact aggregation, scaffold validation, repository tests,
and the application coverage gate. The rejected 16-row v1.4.0 attempt is retained as
an append-only diagnostic with zero accepted benchmark rows.

Run `2026-07-15T15-24-19-159Z-compare` subsequently satisfied this runtime boundary:
90/90 answers were produced, all 30 treatments bootstrapped and confirmed exactly,
all 30 treatment traces contained zero shell or command calls, and the independent
schema-1.7 attestation passed. The attestor also records one control-only superseded
command start followed by an exact successful retry, 16 treatment publication
corrections, and three clean treatment recoveries after failed protocol attempts.
Those observations are explicit runtime diagnostics; none weakens the treatment
bootstrap, isolation, confirmation, or exact-publication gates.
