---
adr: "0103"
title: "ADR 0103: Generate Canonical Multi-Family Knowledge Skills"
summary: "Generate one standalone read-only expert directly with any canonical Semantic OKF builder and its exactly matched consultant."
status: "Accepted"
date: "2026-08-13"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic OKF Expert Skills"
tags: [knowledge, semantic-okf, skills, retrieval, evaluation]
---

# ADR 0103: Generate Canonical Multi-Family Knowledge Skills

## Status

Accepted.

## Context

ADR 0102 accepted a direct classical generator because some delivery workflows
need one ready-to-install expert rather than a separately coordinated builder,
snapshot, packager, and consultant. The same operational need applies to every
canonical Semantic OKF retrieval family. Creating seven more independent
copies of the outer packaging logic would multiply manifest, citation,
validation, and security contracts while making drift likely.

A thin orchestrator over installed sibling skills would not be standalone. A
generated expert that retained builder code or rebuilt on first use would not
be read-only. A generic façade that reimplemented each native consultant would
also risk changing ranking, filters, payloads, or model policy. The design must
therefore share only the stable packaging shell while preserving each accepted
family pair exactly.

## Decision

- Add `skills/build-semantic-okf-knowledge-skill/` as one standalone direct
  generator for the eight families in the canonical evaluation registry:
  `legacy`, `embeddings`, `classical`, `adaptive`, `entity-graph`, `ensemble`,
  `graphify`, and `turso`.
- Vendor the exact accepted builder and consultant packages for every family.
  A byte-parity test binds each vendored regular file to its canonical source.
  The generator never imports or executes a sibling skill.
- Require explicit family selection, a closed source manifest, the exact
  family plan when required, reviewed guidance, generated skill metadata, a
  declared physical layout, and a new destination.
- Build the matched authoritative core and retrieval projection directly under
  the candidate expert's `references/knowledge/`, then run the matched builder
  validator and the generated expert's independent deep validator before
  atomic publication.
- Copy only the matched read-only consultant instructions, references, runtime,
  and dependency declarations into the final expert. Builder code is never
  included in the generated artifact.
- Bind the source manifest, optional plan, family contract, build report,
  complete knowledge tree, record count, reviewed guidance, and every other
  generated artifact under the closed
  `semantic-okf-family-knowledge-skill/1.0` manifest.
- Provide one stable `verify`, `inspect`, `search`, and `get` façade. Translate
  only command syntax, preserve every native payload field and rank, then add
  exact physical path, optional packed-record anchor, and citation fields.
  Advanced native commands remain available unchanged under `scripts/native/`.
- Keep construction and consultation separate. The generated expert verifies
  bindings before every operation, cannot mutate knowledge, has no repository
  dependency, and remains portable after its directory is copied.
- Preserve family-specific model boundaries. Embedding and ensemble plans may
  use only their explicit pinned local model/cache contracts and must fail
  rather than fall back silently. Other family dependency contracts remain
  exact.
- Retain the family-specific direct classical generator, all separate
  build/consult pairs, `build-specialized-skill`, and both Harbor modes. The
  universal generator is an additional direct-delivery path.

## Promotion gate

For every declared dataset and family, run the exact separate builder from the
same staged manifest, plan, layout, runtime, and model policy. Require complete
knowledge-tree byte equality. Require the generated consultant instructions,
references, and runtime to be byte-identical to the canonical consultant.

Execute at least one default-route native comparison and one public façade
query per dataset-family cell. The canonical and packaged native payloads must
match exactly; the façade payload must match before its additive citation
fields. Every retained hit must resolve to local physical evidence, and an
exact `get` operation must reproduce the authoritative ledger body. Dataset
question files must be digest-bound even when complete byte equality makes
per-question replay mechanically redundant.

This gate proves deterministic construction and consultation equivalence. It
does not claim a new model-judged answer-quality result or authorize feedback
from validation or holdout evidence into evolution.

## Validation evidence

The accepted implementation was independently built through both paths for all
eight families on `astro-40`, `graphrag-papers-40`, and
`quantum-error-correction-papers-40`. All 24 dataset-family cells passed exact
knowledge and consultant-package comparison, native query comparison, façade
projection, physical citation resolution, and exact record retrieval.

The matrix binds 960 question-family cells and verifies 10,440 authoritative
record instances across 4,079 knowledge-file instances. All 240 matched
consultant files were byte-identical. All 24 native/default-route payloads and
24 façade projections matched, and all 110 retained hits plus all 24 exact
record probes resolved to local physical evidence.

The reproducible command and machine-readable evidence are retained in
[`20260813-parity-verification.md`](../../evaluations/integrated-semantic-okf-knowledge-skill/reports/20260813-parity-verification.md)
and its adjacent JSON report. The earlier exhaustive classical evaluation
remains the stronger route-by-question replay for that family; this evaluation
adds complete canonical-family coverage.

## Alternatives considered

### Create one direct generator per remaining family

Rejected. It would duplicate the same outer security, manifest, citation, and
atomic-publication logic seven times without improving family isolation.

### Invoke sibling builders and consultants dynamically

Rejected. The generator would not be installable or reproducible by itself,
and a separately updated sibling could silently change its behavior.

### Reimplement every retrieval runtime behind one generic API

Rejected. A new shared implementation could alter ranking and payload behavior.
The stable façade therefore delegates to the exact matched native consultant
and performs only verified additive citation enrichment.

### Package all consultants into every generated expert

Rejected. It would increase artifact size and dependency surface and would make
the selected family boundary ambiguous. Each expert carries exactly one
consultant.

## Consequences

Positive:

- one command covers every canonical family while producing one immutable,
  ready-to-use expert;
- generated experts preserve exact accepted family behavior and dependency
  boundaries;
- one validated façade makes citations and exact lookup consistent across
  otherwise different native CLIs;
- byte-parity and dataset evidence detect source, vendor, or packaging drift.

Negative:

- the generator intentionally carries eight builder/consultant pairs and is
  larger than a thin wrapper;
- canonical family changes require synchronized vendor updates and parity
  tests;
- complete mechanical parity does not itself measure how a language model
  synthesizes a final domain answer.
