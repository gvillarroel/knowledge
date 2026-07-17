---
adr: "0027"
title: "ADR 0027: Retire MCP from Active Definitive Consultation"
summary: "Operate the definitive Semantic OKF consultant through its deterministic local CLI and retain the MCP implementation and evaluation only as historical experiment evidence."
status: "Accepted"
date: "2026-07-15"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - cli
  - mcp-retirement
  - offline
  - quality-gates
---

# ADR 0027: Retire MCP from Active Definitive Consultation

## Status

Accepted.

This decision supersedes ADR 0026 for current operation of
`consult-semantic-okf-ensemble`. It does not invalidate or rewrite ADRs 0023 through
0026. Those records, the historical MCP artifacts, and repository commit
`3a5df66baf99c6c34ef6ff96d35aa44740b906c6` remain immutable evidence of the
completed MCP experiment and the conditions under which its metrics were obtained.

## Context

The definitive ensemble's retrieval and evidence checks are implemented by local,
deterministic Python runners. They can deep-validate the bundle, execute the
`quality`, `fast`, or `robust` retrieval policy, assemble bounded coverage, and
resolve every selected claim to an authoritative path, locator, and text hash
without an MCP transport.

MCP v1.5.0 was introduced to create a particularly strict Skill Arena treatment:
digest-bound skill bootstrap, a profile-gated five-tool sequence, treatment shell
isolation, terminal confirmation, and byte-identical host publication. That design
supplied useful causal and runtime evidence, but it is not required by the
underlying read-only consultation algorithm. Keeping it in the active skill would
make a transport and host wrapper operational dependencies even when the local CLI
already provides the required retrieval and evidence-validity gates.

A direct CLI-only trial on the hard question
`q031-graph-routing-boundary` established that the non-MCP path is operational. It
passed deep validation, ran the `quality` policy with adaptive, BM25, embedding, and
entity-graph participation, read five coverage pages of `[48, 48, 48, 48, 14]`
claims, and produced 206 unique reviewed claims. The trial recorded coverage
SHA-256 `881dec7d573003631c7ee5bb6c55ba4568393df1f911c26dbaa7bfa5c0619ac7`
and priority-order SHA-256
`9ec21df4d02d0e1fba2a9dac3555c68e424968d347ff4d48d8df768351e1b25b`.
It satisfied 4/4 atomic answer groups, 1/1 important-negative group, 3/3 required
papers, and four authoritative evidence bindings, with zero MCP calls. The complete
validation, coverage, and answer-preparation path took approximately 66.23 seconds
in that environment; the captured final output SHA-256 was
`e052575835024481527ed7f07c80242a2ab414370f8868323861945931e43d50`.

A subsequent isolated one-question Skill Arena diagnostic separated the CLI core
from host-agent publication. A first attempt was rejected after the treatment hit
the adapter's 240-second timeout. With that limit aligned to the declared
600-second evaluation timeout, the CLI-skill treatment passed four of five
mechanical gates (`0.8`): format, contract, atomic completeness, and the important
negative. It failed evidence validity only because the agent's final message
changed two authoritative `2506.05690v3.jsonl` paths to nonexistent
`2506-05690v3.jsonl` paths. The direct deterministic finalizer output retained the
correct paths and passed all five gates (`1.0`). This is diagnostic evidence from
one question, not an aggregate quality estimate.

## Decision

The active `consult-semantic-okf-ensemble` package is CLI-only:

1. Consultation invokes the packaged Python runner directly. MCP discovery,
   bootstrap, preparation, confirmation, and host-publication tools are not active
   dependencies or fallback routes.
2. The CLI must deep-validate the selected snapshot before consultation and retain
   the existing closed schemas, bundle hashes, deterministic route policy, bounded
   coverage pagination, authoritative evidence resolution, and read-only behavior.
3. The active consultant may use `quality`, `fast`, or `robust` according to the
   documented policy contract. `quality` remains the default best-observed policy
   on the frozen benchmark.
4. Evidence selected for an answer must continue to resolve to authoritative
   records, paths, locators, and text hashes. Derived adaptive, graph, lexical, and
   embedding artifacts remain non-authoritative discovery aids.
5. Historical MCP reports, trace attestations, evaluation outputs, hashes, and
   metrics remain unchanged. They must be labeled as historical MCP experiment
   evidence and must not be represented as measurements of the current CLI-only
   runtime.
6. Any future causal comparison of the CLI-only consultant requires a new frozen
   configuration, fresh runs, and a runtime contract that measures the CLI path
   actually shipped at that time. The historical 90-answer MCP experiment may
   remain a comparator but cannot substitute for that new run.

## Alternatives rejected

- Keep MCP mandatory for every consultation. This adds transport and host-wrapper
  requirements that the retrieval and evidence-validation algorithms do not need.
- Keep MCP as an automatic fallback. A hidden change between CLI and MCP would make
  the active runtime and its guarantees ambiguous and would weaken reproducibility.
- Delete or rewrite the MCP ADRs and reports. They are durable evidence of a valid
  historical experiment and explain the stronger publication guarantees behind
  its reported answer metrics.
- Transfer the historical MCP answer-output metrics directly to the CLI-only
  runtime. The two paths have different publication boundaries, so that attribution
  would exceed the evidence.

## Consequences

Positive:

- definitive consultation has no MCP server, session, or host-wrapper dependency;
- local and offline execution is simpler to install, diagnose, and reproduce;
- the active behavior is explicit rather than silently switching transports; and
- retrieval, coverage, and authoritative evidence gates remain available through
  the deterministic CLI.

Negative:

- the CLI-only path does not provide MCP v1.5.0's terminal digest confirmation,
  treatment shell isolation, or byte-identical host-publication gate;
- a host agent can still alter otherwise valid finalizer bytes, as the fresh q031
  diagnostic demonstrated with two source-path mutations;
- historical answer-output metrics characterize the completed MCP treatment, not a
  fresh aggregate evaluation of the CLI-only runtime; and
- a new causal answer-quality claim requires a new CLI-only Skill Arena experiment
  rather than reusing the old treatment label.

## Acceptance boundary

The active skill is accepted when it contains no MCP requirement or fallback,
deep-validates the frozen bundle, executes its declared local routes, preserves
read-only authoritative evidence resolution, and passes package validation,
repository tests, and the coverage gate. The verified q031 CLI-only trial is the
manual end-to-end operational check for this transition. It is one difficult case,
not an aggregate answer-quality benchmark.

For response-contract-critical use, acceptance applies to the deterministic CLI
stdout. A surrounding agent's re-authored message is not covered by that guarantee
unless the caller independently validates the returned contract and bindings.

The historical MCP experiment remains accepted within its own frozen boundary:
90/90 generated answers, 90 blinded reviews, and the independent 90-trace
attestation. Its files and metrics are preserved exactly; only their operational
status changes from active design to historical evidence.
