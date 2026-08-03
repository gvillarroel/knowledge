---
adr: "0067"
title: "ADR 0067: Build Standalone Expert Skills from Validated Knowledge"
summary: "Add an optional specialization stage that binds a validated Semantic OKF snapshot and reviewed application guidance into one portable read-only expert skill."
status: "Accepted"
date: "2026-07-27"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Operations"
tags:
  - knowledge
  - skills
  - specialization
  - consultation
  - reproducibility
---

# ADR 0067: Build Standalone Expert Skills from Validated Knowledge

## Status

Accepted.

This decision extends ADRs 0010, 0012, and 0014. It does not replace the
separate `build-semantic-okf` and `consult-semantic-okf` packages or change the
two execution modes accepted by ADR 0034.

## Context

The accepted architecture builds a Semantic OKF snapshot and later gives a
generic read-only consultation skill access to that snapshot. This cleanly
separates lifecycle and consultation authority, but the consultation procedure
remains generic and the knowledge remains a separately mounted artifact.

Some domains need a portable expert artifact that contains both the exact
knowledge revision and the best reviewed instructions for applying it. Building
that artifact during snapshot construction would couple domain guidance to the
write-capable lifecycle skill. Modifying the generic consultant would either
embed one domain in a reusable package or make its behavior depend on an
untracked external prompt.

## Decision

Add `build-specialized-skill` as an optional second stage after a complete
Semantic OKF build:

1. **Build Knowledge** converts raw sources into one passing immutable Semantic
   OKF snapshot using the existing builder.
2. **Build Specialized Skill** accepts that exact snapshot plus reviewed
   domain-application guidance and emits one standalone expert skill.
3. **Consult** installs or mounts only the generated expert skill and answers
   from its embedded immutable snapshot and guidance.

The specialization builder never acquires sources, repairs or refreshes
Semantic OKF, answers the final domain question, or overwrites an existing
expert. It validates the minimum read surface, rejects symlinks and unsafe
concept paths, copies all knowledge bytes, and emits
`expert-manifest.json` under schema `semantic-okf-expert-skill/1.0`.

The manifest binds the complete knowledge tree, record count, source build
report, guidance, generated instructions, read-only query helper, and interface
metadata. It omits timestamps and absolute source paths. Identical inputs must
produce byte-identical expert skills, and `--check` must compare a temporary
rebuild without mutating the accepted artifact.

The generated expert is a standalone read-only skill. It verifies every binding
before ledger search or exact lookup, cites embedded `concept_path` values, and
stops when the snapshot does not support a conclusion. It does not depend on a
sibling consultation skill or an external knowledge mount.

## Compatibility and evaluation

The existing Build and Consult path remains accepted. Use it when one generic
consultant should consume an external immutable snapshot. The new path is an
optional artifact boundary, not a reinterpretation of `build-consult` or
`consult-only`; their skill and mount isolation rules remain unchanged.

Evaluate the specialized path as three digest-bound stages. Compare alternatives
only when dataset, cohort, candidate budget, identity grouping, and metric
contract match. Primary report tables keep alternatives in rows and aggregate
dataset metrics in columns. Artifact validity, semantic quality, latency, and
governance decisions remain distinct measurements or conclusions.

## Consequences

Positive:

- knowledge and the procedure for applying it become one portable artifact;
- consultation can reproduce the exact knowledge revision without a separate
  mount or hidden prompt;
- stage boundaries make builder, specialization, and consultation regressions
  independently attributable; and
- deterministic manifests expose drift before a query is answered.

Negative:

- embedding a full snapshot increases skill size;
- every knowledge refresh requires a newly named or newly published expert
  artifact rather than an in-place mutation; and
- domain guidance still requires review because byte-level validation cannot
  prove that instructions are the best semantic procedure.
