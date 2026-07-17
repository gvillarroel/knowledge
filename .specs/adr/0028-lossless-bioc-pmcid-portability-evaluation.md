---
adr: "0028"
title: "ADR 0028: Preserve BioC JSON Losslessly and Measure PMCID Portability Without Identity Substitution"
summary: "Keep NCBI BioC passages and reviewed PMCID claims authoritative, bind acquisition to an ignored append-only Know export, and report unchanged Semantic OKF alternatives as incompatible rather than fabricating PDF or arXiv identities."
status: "Accepted"
date: "2026-07-15"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - know
  - okf
  - bioc
  - pmcid
  - portability
  - evaluation
---

# ADR 0028: Preserve BioC JSON Losslessly and Measure PMCID Portability Without Identity Substitution

## Status

Accepted.

This decision applies the authority and derived-index boundaries from ADRs 0017,
0019, 0020, 0021, and 0023 to a new NCBI PubMed Central corpus. It also follows
ADR 0027 for deterministic direct builds and consultations by using local CLI and
Python runtimes only. Those direct executions are offline after the accepted corpus
and pinned embedding model are present. The separate paired Skill Arena diagnostic
uses a remote PI model with network access. MCP is neither required nor used by
either path.

## Context

The endocrine-hygiene evaluation needed a domain-shifted corpus acquired through
Know rather than a copy of the earlier arXiv/PDF benchmark. Fifteen PubMed Central
papers were selected from NCBI's BioC JSON service. The source responses contain
JSON string values with characters that are meaningful to an HTML parser. The
previous site-source path treated every successful HTTP response as HTML, so an
initial integrity audit rejected the synchronized corpus: HTML extraction had
altered BioC JSON instead of preserving the response body.

This corpus also exposes assumptions that were harmless on the earlier benchmark:

- BioC supplies numbered passages, not PDF-page sections.
- The real paper identities are PMCIDs such as `PMC6504186`, not canonical
  versioned arXiv IDs.
- The entity-section graph in ADR 0020 requires literal PDF-page headings.
- The adaptive answer-binding contract in ADR 0021 accepts canonical versioned
  arXiv identity mappings, and the definitive ensemble in ADR 0023 requires those
  mappings to be complete.

Changing the old packages or inventing compatible-looking identities during the
evaluation would erase the portability evidence the corpus was designed to reveal.

## Decision

### Preserve JSON HTTP representations before any document extraction

The Know site adapter recognizes `application/json` and structured syntax suffixes
such as `application/problem+json`. For those media types it:

1. obtains the exact response bytes;
2. decodes them as UTF-8 and rejects an invalid encoding;
3. parses the decoded value as JSON and rejects invalid JSON;
4. stores the decoded response text as the page body without HTML extraction or
   link discovery; and
5. records `content_format: json`, the HTTP content type and status, raw byte count,
   and raw SHA-256.

The normalized corpus generator independently rechecks the Know page hash, raw
BioC byte count and digest, collection/document cardinality, PMCID, metadata, and
every passage before publication. The accepted Know export is append-only and
ignored because it is large. Its compact checked-in binding is:

- key: `endocrine-hygiene-bioc-2026-07`;
- file: `exports/knowledge-export-20260715T220149Z.zip` under the isolated Know
  store;
- bytes: `1952464`; and
- SHA-256: `73ae75e7cf024bb338ab1c7580e4766c0eb05b12ccd33a8e564f917da35d575f`.

A new download is not automatically the accepted input. It must satisfy the same
closed acquisition manifest and raw-response hashes, or be published as a new
versioned corpus.

### Keep BioC passage text and reviewed claims authoritative

The authority boundary is:

- the normalized NCBI BioC passage text and its exact passage hash are the
  authoritative paper evidence;
- the 93 manually reviewed claim rows are authoritative interpretations only within
  their explicit passage bindings and review metadata;
- the Semantic OKF ledger, concepts, RDF, provenance, shapes, and validation report
  are authoritative projections of those declared sources; and
- vocabulary statistics, chunks, embeddings, BM25 statistics, topic communities,
  term associations, adaptive signals, rankings, qrels, benchmark aggregates, and
  extractive answer packs are derived and non-authoritative.

The five hard-question ground truths contain 60 question-specific exact evidence
bindings across 34 distinct authoritative passages. Their separate closed exact-claim
ledger contains 128 requirement occurrences across 37 distinct reviewed claim IDs.
Each evidence binding records a path, one-based `BioC-passage-NNNN` locator, and
exact text SHA-256. Benchmark labels, exact claim requirements, derivations,
negatives, and answers remain evaluator-only; a consultant receives only the
question string.

Validation joins every required claim to the evidence declared for its exact atomic
answer or negative by `(paper_id, evidence_text_sha256)`, then independently resolves
and rehashes the authoritative passage. The claim ID remains part of scoring because
one passage can support several distinct reviewed interpretations. Every one of the
60 evidence bindings must also have at least one reviewed-claim projection.

### Preserve real identities and source namespaces

Paper identities use canonical uppercase PMCIDs, for example `PMC6504186`.
Manifest source IDs remain lowercase and source-scoped, for example
`paper-pmc6504186` and `claims-pmc6504186`; the isolated Know source ID is
`pmc6504186`. These are deliberately distinct identifiers.

BioC headings remain `## BioC passage NNNN`. They must not be relabeled as PDF
pages. PMCIDs must not be replaced by fabricated arXiv IDs. The evaluator may use
the checked `source-combination.json` map to collapse source-level hits to their
real PMCID for scoring, but that derived map does not rewrite bundle identities or
grant an unchanged package a capability it does not expose.

### Evaluate unchanged alternatives and retain incompatibility as a result

All six existing builder families run twice from the same 15 paper sources, 15
claim sources, and one auxiliary vocabulary. Successful candidates must pass their
own validators, preserve the authoritative core, and reproduce an LF-normalized
logical tree. Expected incompatibilities must reproduce the same bounded diagnostic
on both attempts.

The accepted run, `20260715-endocrine-builds-05`, produced four successful
deterministic builders: legacy, embeddings, classical, and adaptive. Each has
authoritative core logical-tree SHA-256
`a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262`
and byte-identical `semantic/records.jsonl` SHA-256
`5bb09f5b4a7eb86c9f9e69c2e78c77d04a9530c5b305f3725c7ec3ef859913f5`.

The preceding append-only run, `20260715-endocrine-builds-04`, is rejected history.
Its second embeddings attempt encountered a missing Windows staging path, so the
run-level core-parity gate failed and no retrieval output from that run was accepted.
Run `-05` rebuilt the same frozen inputs and passed both attempts. The failed run is
retained for auditability rather than overwritten.

The unchanged entity-graph builder is not applicable because the records have no
PDF-page headings. The unchanged ensemble builder is not applicable because its
adaptive component requires canonical versioned arXiv identity mappings. These are
N/A portability results, not zero retrieval scores. The standalone adaptive build
can publish its search projection with an empty paper-identity map, but consequently
has zero packaged answer bindings; evaluator-side ledger extraction does not change
that product limitation.

Retrieval quality, answer completeness, grounding, evidence validity, response
contract, latency, build integrity, and portability remain separate measures. A
high retrieval score cannot compensate for invalid evidence, and a structurally
grounded extractive pack cannot be described as a complete answer.

### Separate the direct benchmark from the Skill Arena causal diagnostic

The deterministic 30-question direct benchmark compares retrieval algorithms and
extractive claim selection over frozen bundles. It runs locally and offline after
inputs are available, and it does not estimate the causal effect of giving a skill
to an agent.

The Skill Arena configuration is a separate paired five-question diagnostic. Its
`knowledge-only-control` and `classical-cli-consult-treatment` profiles receive the
same published snapshot and vary only the consultation skill surface. It uses one
request per cell, exact claim-fidelity and ledger-evidence assertions, a remote PI
model with network access, and no MCP. Its result must be reported per assertion and
as paired control/treatment differences. Five prompts with one request per cell are
not a stable aggregate estimate and must not be combined with an all-skills
portfolio to claim general superiority.

Accepted eval `eval-v8v-2026-07-15T23:49:40` completed all `10/10` cells with `0`
runtime errors. Control and treatment each passed 0 of 5 compound cells. Mean score
was `0.657` for control and `0.543` for treatment (treatment minus control `-0.114`);
mean latency was `72.6 s` and `117.6 s`, respectively (`+45.0 s`). Control/treatment
component pass rates were: response format `100%/100%`, response contract
`100%/80%`, evidence validity `40%/20%`, exact reviewed-claim fidelity `100%/100%`,
atomic answer completeness `20%/0%`, important-negative coverage `20%/0%`, and
required-paper coverage `80%/80%`.

This single run provides no evidence of treatment improvement. It shows that exact
claim wording can pass while evidence identity and complete positive/negative claim
sets still fail. The strict claim/evidence response contract remains the principal
bottleneck. The compact evidence is recorded in
[`skill-arena-hard5-diagnostic.md`](../../evaluations/semantic-okf-endocrine-hygiene/reports/skill-arena-hard5-diagnostic.md)
and
[`skill-arena-hard5-diagnostic.json`](../../evaluations/semantic-okf-endocrine-hygiene/reports/skill-arena-hard5-diagnostic.json).

## Relationship to earlier decisions

- ADR 0017 remains unchanged: embedding chunks and vectors are optional,
  hash-bound discovery artifacts. In this evaluation, its lexical route outperformed
  its vector and hybrid routes; that observation is corpus-specific.
- ADR 0019 remains unchanged: BM25, topics, associations, and fusion stay derived,
  deterministic classical signals. This evaluation also retains its distinction
  between optional `rg` guidance and the evaluator's in-memory lexical baseline.
- ADR 0020 remains valid for its declared PDF-page corpus. This evaluation records
  that the unchanged entity-section graph does not accept honest BioC passage
  headings.
- ADR 0021 remains valid for its canonical versioned arXiv answer-binding contract.
  Its general search projection builds on this corpus only without PMCID answer
  bindings.
- ADR 0023 remains valid for the frozen definitive ensemble and its complete
  adaptive identity contract. This evaluation does not weaken that gate to make a
  PMCID run succeed.
- ADR 0027 governs active definitive consultation. Every compatible direct route
  here runs through a local CLI or local Python runtime, offline and with no MCP
  dependency or fallback. The separate Skill Arena control/treatment run is remote,
  network-enabled, and still uses no MCP.

## Alternatives rejected

- Continue passing JSON through HTML extraction. This changes authoritative source
  bytes and can silently remove or reorder evidence.
- Rename BioC passages as PDF pages. This creates false locators and would make the
  entity graph appear compatible by corrupting provenance.
- Map PMCIDs to invented versioned arXiv IDs. This creates false paper identity and
  invalidates joins, qrels, and citations.
- Patch legacy packages during the comparison. That would confound portability with
  a new implementation and invalidate the frozen-baseline claim.
- Report incompatible families as zero. Zero means an executed route failed to
  retrieve relevant evidence; these routes could not be built under their closed
  input contracts.
- Treat rankings or extractive answer packs as authoritative facts. Their role is
  discovery and evaluation, not domain authority.
- Check large exports, bundles, or detailed runs into Git. Compact hashes, manifests,
  reports, ground truth, plans, and documentation are sufficient; raw artifacts stay
  append-only and ignored.

## Consequences

Positive:

- JSON acquisition is byte-auditable and no longer depends on HTML-parser behavior;
- honest PMCIDs and BioC locators preserve citation and provenance meaning;
- the same authoritative core can be compared across four independently validated
  builder families;
- portability failures are reproducible evidence rather than hidden by adapters;
  and
- compact checked artifacts bind an ignored raw acquisition and append-only runs.

Negative:

- the entity-graph and definitive ensemble alternatives cannot be scored on this
  corpus without a separately versioned generalization of their schemas;
- the standalone adaptive bundle has no PMCID answer bindings even though its search
  routes execute;
- retaining the accepted ignored Know export is operationally necessary for exact
  offline reconstruction; and
- BioC passage numbers are stable corpus locators, not printed-page citations.

## Acceptance boundary

This decision is accepted for corpus and benchmark version 1.0 when:

- the 15-paper acquisition contains 2,010 BioC passages and 604,905 passage-text
  characters with every raw and normalized hash valid;
- all 93 reviewed claims bind to authoritative passages;
- all 30 questions validate, including five hard questions with 60 question-specific
  exact evidence bindings across 34 distinct authoritative passages;
- all 128 exact claim requirement occurrences resolve to 37 distinct reviewed claim
  IDs and join to the evidence declared for their atomic answer or negative;
- successful builders reproduce the same authoritative core across two attempts;
- the two expected incompatibilities reproduce their declared diagnostics;
- every executed retrieval hit passes independent ledger evidence validation; and
- all consulted bundles remain byte-identical under read-only evaluation.

The accepted direct benchmark is an algorithm comparison on one frozen corpus. It
is not a causal treatment result, a general claim that one method is universally
superior, or proof that the deterministic extractive packs are complete
natural-language answers. The separate paired Skill Arena diagnostic can estimate a
skill-surface effect for its five prompts, but its single request per cell does not
support a stable general superiority claim.
