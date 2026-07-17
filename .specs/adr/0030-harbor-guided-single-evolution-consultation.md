---
adr: "0030"
title: "ADR 0030: Evolve Semantic OKF Consultation with Frozen Harbor Trials"
summary: "Evaluate one independently named evolution of every consultation family with Pi and GPT-5.3 Codex Spark in Harbor, using strict evidence compilers and prospective train, development, and holdout boundaries."
status: "Accepted"
date: "2026-07-16"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - harbor
  - pi
  - skill-evolution
  - evaluation
---

# ADR 0030: Evolve Semantic OKF Consultation with Frozen Harbor Trials

## Status

Accepted.

This decision extends ADRs 0027 and 0029. It does not replace any legacy,
embedding, classical, adaptive, entity-graph, or ensemble package and does not
restore MCP to the active consultation path.

## Context

The forty-question Astro benchmark established deterministic retrieval quality,
but retrieval scores alone do not test how an agent follows a consultation skill,
constructs an answer, orders citations, or survives a realistic tool-use loop.
Earlier live comparisons also exposed failures that a ranking benchmark cannot
represent: invalid JSON, invalid evidence hashes, first-use ordering mistakes,
excessive context, and timeouts.

Changing a package repeatedly after inspecting every question would make any
reported improvement difficult to interpret. Comparing a profile containing all
skills would confound routing and skill effects. The checked Astro ground truth is
historically visible and source documents overlap cohorts, so a new split can be
prospective only with respect to question use, not a claim of untouched population
secrecy.

Harbor provides a reproducible task, agent, environment, and verifier boundary.
Pi can run the same GPT-5.3 Codex Spark model against one mounted bundle and one
installed skill per trial. The local Harbor 0.18.0 egress sidecar does not start on
the current WSL Docker host, so network blocking cannot honestly be claimed for
this campaign.

## Decision

### Freeze one causal comparison per family

Create exactly one standalone consultation candidate for each of the six existing
families:

- `consult-semantic-okf-harbor-legacy`;
- `consult-semantic-okf-harbor-embeddings`;
- `consult-semantic-okf-harbor-classical`;
- `consult-semantic-okf-harbor-adaptive`;
- `consult-semantic-okf-harbor-entity-graph`; and
- `consult-semantic-okf-harbor-ensemble`.

The existing packages remain unchanged and installable. Each candidate is copied
from its reviewed parent, independently named, validated as a complete skill, and
frozen by a closed regular-file tree hash before development evaluation. Each
baseline/evolved pair uses the same accepted bundle, question, task image, Pi
version, model, thinking level, timeout, and verifier. Only the skill snapshot
changes. Skill Arena configurations preserve the same direct pairwise structure;
an all-skills profile is not used as causal evidence.

Use `q031` as the inspected training case, `q032` once as development, and `q034`
once as holdout for the live pilot. These labels were chosen and recorded before
candidate evaluation. The complete deterministic forty-question benchmark remains
the broader retrieval check. A single live case per cohort is a diagnostic pilot,
not a statistically powered estimate.

### Add bounded answer compilers without changing retrieval identity

Retain each parent's retrieval implementation byte-for-byte. Add a family-specific,
read-only answer compiler with two phases:

1. `prepare` runs the family retrieval route, projects candidate passages back to
   exact authoritative parent records, creates bounded excerpts, and binds every
   support ID to its parameters and hashes.
2. `finalize` rebuilds the support pack, rejects changed or unknown support IDs,
   enforces a closed response schema and bounded prose, and emits exact evidence
   rows in first-use order.

Graph edges, embedding vectors, topic signals, ranks, excerpts, support packs, and
answer drafts remain derived and non-authoritative. Evidence rows point to the
authoritative Semantic OKF record body and its published hashes. Publication is
unchanged, consultation is read-only, and no sibling skill, evaluator file, qrel,
or ground truth is imported by a candidate.

### Use non-compensating gates and append-only evidence

The verifier reports sixteen independent dimensions. Promotion requires zero
runtime errors and perfect response-contract, non-null answer, reference-validity,
evidence-validity, all-evidence-valid, and quality-gate results. Development reward
and hard evidence completeness may not regress. Deterministic retrieval may not
regress. A high nDCG or mean reward cannot offset invalid JSON, stale evidence, or a
timeout.

Every executed Harbor job is append-only. A checked binding ledger names accepted
job and trial paths and pins their result and lock hashes. Infrastructure failures
that occur before the model receives the task are retained but excluded explicitly;
they are never overwritten or silently relabeled as skill failures. Authentication
is copied to a private per-job directory, never serialized into configs or reports,
and deleted after execution. The runner rejects an empty OpenAI Codex credential
before starting Harbor.

### Keep evidence sufficiency separate from answer correctness

The deterministic grader validates response shape, source identity, locators,
hashes, qrel coverage, rank quality, required documents, authoritative spans,
atomic-claim evidence coverage, and important-negative evidence coverage. These
metrics establish that sufficient authoritative evidence was cited; they do not
prove that the prose states every ground-truth claim or entails it correctly.

Any semantic review of answer text must use a separately frozen atomic rubric,
retain its result bindings, and report correctness and completeness separately.
No semantic score is inferred from evidence coverage alone.

### Record the network and runtime boundary honestly

Pin Harbor `0.18.0`, Pi `0.73.1`, and
`openai-codex/gpt-5.3-codex-spark` with high thinking. MCP is absent. Agent and
verifier run in separate containers, and the verifier receives neither bundle nor
authentication mounts. Both use Harbor's `public` network mode on this host because
egress enforcement is unavailable; offline verifier code is an implementation
property, not a network-isolation claim. A compatible future host may use allowlist
and no-network modes only after a disposable smoke test passes.

## Consequences

Positive:

- live skill effects are compared directly within each retrieval family;
- every evolution is standalone and cannot silently alter a historical baseline;
- bounded support packs reduce context and expose exact evidence identities;
- invalid contracts and evidence fail independently of ranking quality; and
- compact reports can be reproduced from hash-bound append-only jobs.

Negative:

- one live question per cohort has high variance and cannot establish universal
  superiority;
- source overlap and checked ground truth prevent a claim of historical secrecy;
- strict agent compliance can still fail after a deterministic finalizer produces a
  valid answer; and
- the current host cannot enforce network isolation, so the limitation must remain
  visible in every interpretation.

## Acceptance boundary

Acceptance requires six frozen standalone skill hashes, identical parent retrieval
files, validated generated Harbor tasks, an oracle grader trial, pairwise baseline
and evolved executions, explicit infrastructure exclusions, deterministic
forty-question retrieval parity, Skill Arena configuration validation and dry runs,
manual query smokes, package validation, repository tests, and application coverage
of at least 80 percent. Raw jobs, traces, generated tasks, runtime images, model
caches, authentication, and bundle snapshots remain ignored; compact manifests,
bindings, reports, tests, and English documentation are checked in.
