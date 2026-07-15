---
adr: "0023"
title: "ADR 0023: Select a Quality-Gated Ensemble for Definitive Semantic OKF Retrieval"
summary: "Ship a standalone Semantic OKF builder and read-only consultant that protect adaptive retrieval breadth, combine four independently validated signals, and permit answers only through exact authoritative evidence gates."
status: "Accepted"
date: "2026-07-15"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - ensemble-retrieval
  - quality-gates
  - entity-graph
  - evidence-binding
  - deterministic-finalization
  - skill-arena
---

# ADR 0023: Select a Quality-Gated Ensemble for Definitive Semantic OKF Retrieval

## Status

Accepted.

This decision extends ADR 0012, ADR 0014, ADR 0015, ADR 0017, ADR 0019,
ADR 0020, ADR 0021, and ADR 0022. It creates a new release candidate without
modifying or replacing the legacy, embedding, classical, entity-graph, or
adaptive packages.

ADR 0024 extends this decision and supersedes its answer-publication,
expected-ID, and answer-candidate coverage details. The direct-ranking policy,
final-03 build, and direct retrieval results in this record remain accepted.
The 41/44 coverage and 198-claim q031 transport figures below are retained as
historical pre-review/pre-diversification evidence; the accepted reviewed
coverage result is 44/44 atomic groups, 13/13 important-negative groups, all
required papers, and 713/713 valid bindings.

Here, *definitive* means the recommended quality-gated implementation for this
repository and frozen evidence contract. It does not imply universal superiority
on unseen corpora.

## Context

The completed alternatives have complementary strengths. Adaptive retrieval gives
the strongest breadth; BM25 supplies precise lexical matches; entity-section graph
routes expose reviewed claim relationships and exact source sections; and pinned
embeddings recover some paraphrases. No existing standalone pair combines these
signals while protecting the authoritative core, preserving the best candidate set,
and applying exact answer-evidence gates.

A naive portfolio is unsafe. A weak route can displace a stronger paper, extracted
entity co-mentions can be mistaken for reviewed facts, repeated embedding chunks can
distort paper rank, and answer-time reconstruction can corrupt otherwise valid claim
IDs, paths, locators, or citation pages. The repository therefore needs explicit
gates between retrieval, candidate expansion, evidence selection, and final response
serialization.

## Decision

### Ship an independently installable build and consult pair

Create these standalone packages:

1. `build-semantic-okf-ensemble` builds the unchanged authoritative Semantic OKF
   core plus closed adaptive, entity-graph, embedding, and ensemble projections.
2. `consult-semantic-okf-ensemble` validates and consults that bundle read-only.

Each package owns its runtime code, references, requirements, commands, schemas,
plans, tests, and validation. Neither imports a sibling skill or repository
evaluation helper at runtime. The builder creates every layer in a private sibling
candidate, validates the complete result, and publishes it with one atomic rename.
A failure leaves neither the requested destination nor a private candidate.

Consultation does not write caches, queries, answers, locks, repairs, downloaded
models, or derived data into the bundle. A changed source, plan, dependency lock,
model revision, or algorithm identity produces a new bundle generation rather than
mutating a published one.

The consultant must also be usable both from its own installed package root and
from a repository or Skill Arena workspace overlay. It resolves the query CLI only
from the package-local `scripts/` path or the explicit
`skills/consult-semantic-okf-ensemble/scripts/` overlay path, and resolves the
bundle from the explicit argument or the overlay's `knowledge/` directory. Failure
to resolve either location stops with a bounded diagnostic. Recursive drive, home,
root-filesystem, or outside-workspace discovery is prohibited; in particular, a
consultation must never use `find /` or an equivalent global scan to locate a
bundle or package. This portability and containment rule is covered by package tests
and by a real workspace-overlay model smoke test before the causal comparison.
The first final-03 live attempt was terminated and rejected as evidence after the
treatment tried a global filesystem lookup under the earlier instructions; no row
from that run may be aggregated. The accepted comparison must use a fresh run created
only after the bounded resolver smoke test passes. Later diagnostic smokes were also
rejected rather than repaired in place: one backend exposed no file tools and
returned a null treatment answer, a tool-capable read-only Codex sandbox blocked the
packaged Python query command, and a workspace-write smoke reached the command but
the host-default Python 3.14 runtime did not satisfy the pinned Python 3.12.13
semantic dependency contract. These runs are portability diagnostics, not answer
evidence, and none may be aggregated into the accepted comparison.

The accepted comparison supersedes the diagnostic shell-launcher route with the
profile-gated, read-only MCP 1.4.0 server packaged with the definitive consultant. The
same server configuration is present in all three profiles. It returns an empty
tool list to the knowledge-only and adaptive controls and exposes exactly
`semantic_okf_inspect`, `semantic_okf_coverage_brief`,
`semantic_okf_prepare_answer`, and `semantic_okf_confirm_answer` to the ensemble
treatment. All four tools are read-only, non-destructive, and closed-world. Inspect,
coverage, and prepare are idempotent; confirm is non-idempotent. Their closed schemas
accept no bundle path, cache path, command, or URL. Prepare has no `mode` and returns
the canonical closed `semantic-okf-prepared-answer/1.0` envelope containing exactly
`schema`, `candidate_json`, `response_sha256`, and `byte_count`; confirm accepts only
the 64-character lowercase hexadecimal `response_sha256`.

The treatment protocol is inspect, every bounded coverage page for identical query
parameters, one or more successful prepares, and exactly one successful terminal
confirm. Preparation is state-gated until the earlier steps complete and independently
recomputes the unpaged coverage pack before constructing the contracted answer. The
agent reviews the envelope's exact `candidate_json` but confirms only its short digest.
Any failed prepare or confirm publishes nothing and clears the active transaction; the
final clean suffix must start with a fresh successful prepare. An earlier successful
confirm, confirm without a fresh prepare after failure, stale or mismatched digest,
repeated confirm, or any tool call after successful confirmation is rejected. The host
wrapper verifies envelope canonicality, digest, UTF-8 length, receipt binding, and
transaction order, then publishes the exact `candidate_json` bytes rather than a
re-authored final message. The
comparison therefore estimates the full definitive consultation capability—skill
instructions, MCP workflow, and host publication gate—not skill text alone.

The MCP runtime retains two explicit host gates. `SEMANTIC_OKF_PYTHON` must resolve
to an absolute regular file matching the exact Python executable and dependency
contract recorded in the config manifest. `SEMANTIC_OKF_HF_HUB_CACHE` must resolve
to an absolute directory containing the pinned embedding-model revision. The server
maps only that cache to the model runtime, while the Skill Arena variant disables
network access and web search and sets the model libraries to offline operation.
Relative paths, an absent cache, a runtime mismatch, or a missing model fail closed;
no host-specific absolute path is persisted in the config. The adapter's ephemeral
workspace permission does not grant derived artifacts authority and does not relax
independent evidence or bundle-integrity validation.

### Preserve the authoritative boundary

The ledger, concept Markdown, and purpose-selected RDF graphs remain authoritative.
All lexical statistics, topics, associations, extracted entities, co-mentions,
graph traversal state, chunks, embeddings, rankings, answer bindings, coverage
facets, evidence packs, and quality-gate results remain derived and
non-authoritative.

Every projection has a closed schema and is hash-bound to its complete plan,
algorithm identities, source inventory, component indexes, and authoritative core
tree. Independent validation rederives artifacts and cross-layer joins. Candidate
entities and co-mention edges can guide discovery but never establish a fact or a
negative. Factual output must resolve to reviewed authoritative records and exact
authoritative sections.

### Protect breadth and rerank with four signals

The default `quality` policy uses
`protected-multisignal-paper-rerank-v2`:

1. Run adaptive retrieval and preserve its top-*k* unique paper identities as the
   protected candidate set.
2. Rank papers independently with adaptive fusion, graph fusion, BM25, and the
   exact pinned embedding hybrid route.
3. For protected paper *p*, calculate weighted reciprocal-rank fusion as:

   ```text
   score(p) =
       4 / (7 + adaptive_rank(p))
     + 1 / (7 + graph_fusion_rank(p))
     + 5 / (7 + bm25_rank(p))
     + 1 / (7 + embedding_hybrid_rank(p))
   ```

   A missing route rank contributes zero.
4. Break equal fused scores by, in order: best active route rank, sum of active
   route ranks with missing papers placed after the budget, number of active routes
   containing the paper in descending order, and canonical paper ID.
5. Consider the graph-lexical rank-one paper for promotion. Promote it to rank one
   only when it is in the protected adaptive set, is within the first three results
   of at least three of the five confirmation routes (adaptive, graph lexical,
   graph fusion, BM25, and embedding hybrid), and satisfies the persisted maximum
   protected-rank gate.

The output paper set must exactly equal the protected adaptive set. The ensemble may
improve order and evidence navigation but cannot displace a protected paper at the
fixed direct-search budget. The response exposes component ranks, fused scores,
promotion evidence, selected sections, and exact evidence bindings.

The pinned semantic provider is part of the `quality` contract. A missing or corrupt
model, wrong revision, changed dimensions, or unavailable local runtime fails closed;
it never triggers a silent lexical substitution or download.

### Provide explicit lower-cost and reproduction policies

The consultant exposes three named direct-search policies:

- `quality` is the four-route default described above;
- `fast` uses protected adaptive plus graph-lexical ranking with weights 4:1,
  reciprocal-rank constant 5, and a stricter two-of-two promotion gate; and
- `robust` reproduces the protected adaptive order without another route changing
  it.

The requested and effective policy, disabled routes, fallbacks, route rankings,
budgets, component hashes, candidate-set gate, and promotion gate are disclosed.
Neither `fast` nor `robust` is presented as the quality policy.

### Expand answer candidates only through reviewed graph paths

Direct paper retrieval and answer-claim discovery have separate budgets. For a
multi-part answer, the consultant retains adaptive full-question and facet-separated
coverage, then adds `bounded-reviewed-claim-multisignal-expansion-v2`:

1. Derive graph queries only from the question and its lexical facets. Do not pass a
   question ID, expected answer, qrel, benchmark label, or ground truth.
2. Resolve query entities and traverse an undirected view of declared edges for at
   most two hops.
3. Assign candidate edges zero answer-selection authority.
4. Accept only reviewed claim nodes with exact authoritative identities and verified
   answer bindings.
5. Retain no more than eight graph claims per facet and no more than eighty in the
   total graph expansion.
6. Run the exact pinned hybrid embedding route over the full question and the same
   facets, filtered to the fifteen declared claim sources. Intersect every hit with a
   reviewed exact answer binding, retain no more than twenty claims per facet and 240
   globally, and treat similarity only as candidate discovery.

Every requested subject, comparison axis, condition, exclusion, mechanism, and
important negative is marked `supported`, `partial`, or `unresolved`. Evidence is
then minimized to records that directly entail each atomic statement. Unsupported
facets are qualified rather than filled from model memory.

The deterministic finalizer accepts only claim IDs in the gated coverage union. It
reconstructs paper IDs, claim and source paths, canonical locator strings, numeric
citation pages, evidence rows, and sorting from validated bindings. It guarantees
response shape and evidence identity, but semantic entailment still requires review.

The semantic claim route is deliberately post-selection and non-ranking. It cannot
change direct paper routes, weights, reciprocal-rank fusion, the protected paper
set, promotion, or tie order. This keeps the completed population-selection result
valid while allowing a separately measured answer-evidence gate to improve synthesis
readiness.

### Enforce non-compensating quality gates

Build and release gates require:

- standalone package validation and package-local runtime smoke tests;
- closed plans and regular-file artifact trees without symlinks or junctions;
- complete declared-source selection or explicit exclusion;
- independent core and component validation with exact core-tree parity;
- exact source, record, concept, paper, claim, locator, text, and hash joins;
- reviewed/candidate graph-state separation and zero candidate-edge authority;
- complete answer-binding and claim-to-section crosswalk reconstruction;
- two clean builds with identical sorted path-and-byte trees;
- cleanup without publication after failure; and
- no benchmark questions, expected claims, qrels, answers, or evaluator labels in
  either package or the published bundle.

Retrieval gates require zero query errors, independently valid evidence, exact
preservation of the adaptive top-*k* paper set, filtering before scoring, one result
per paper, and no regression on the frozen adaptive recall floors.

Answer gates require complete facet accounting, reviewed bindings for every selected
claim, minimal direct support for each atomic statement, exact locator/page/path
agreement, literal output-contract compliance, qualification of unsupported facets,
and a byte-identical bundle before and after consultation.

Invalid evidence, authoritative-core drift, benchmark leakage, a semantic-provider
substitution, or a failed read-only contract cannot be offset by a better ranking
score. Retrieval quality, candidate coverage, answer correctness and completeness,
grounding, contract compliance, latency, size, and determinism remain separate
dimensions.

### Select the quality constants with reproducible population search

The frozen ranking-selection search ran four generations. Each generation contained
ten isolated candidates, and each candidate was replayed three times to require a
deterministic result. It kept the top two candidates, bred or mutated the remaining
eight, rejected gate failures, and stopped after the winner was unchanged for two
consecutive generations. This satisfied the required two-generation plateau.

The selected 4:1:5:1, *k*=7 policy with the consensus tie order and three-of-five
promotion gate achieved fitness `91.8891506056` in that search. Its frozen ranking
replay metrics were:

| Cohort | Recall@10 | MRR@10 | nDCG@10 | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| All 40 questions | 0.8381619769 | 1.0000000000 | 0.8520010048 | 1.0000000000 |
| Hard 10 questions | 0.9550000000 | 1.0000000000 | 0.8827017521 | 1.0000000000 |

These figures are replay-based ranking-selection evidence over frozen component
rankings. They demonstrate deterministic policy selection and fixed-benchmark
retrieval behavior; they are not a live-runtime measurement, a generated-answer
evaluation, or a causal Skill Arena result. The selected package must subsequently
pass real bundle execution, read-only and evidence validation, grounded-answer
assessment, and isolated Skill Arena control/treatment evaluation. Those later
results are recorded separately and must not be conflated with the population replay.

Skill Arena uses a knowledge-only control, an adaptive-consult active control, and a
single-skill ensemble treatment with identical model, task, bundle, and restrictions.
Both controls expose zero Semantic OKF MCP tools; only the treatment exposes the
four-tool inspect/coverage/prepare/confirm workflow. An all-skills portfolio can be a
routing smoke test but is not causal evidence for this decision.

### Accept final-03 after independent reproduction

The accepted `20260715-ensemble-final-03` release was built twice from the same 15
paper Markdown files, 15 reviewed claim JSONL files, and one declared vocabulary.
Both builds produced 904 files with zero path or digest differences, preserved the
874-record authoritative core at tree SHA-256
`331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`,
and produced ensemble index SHA-256
`9ce8bac88df8621fd870d718d1166e706516f4c4d56497eecc080d454453e939`.

Direct final-03 execution reproduced the selected ranking exactly. On all 40 frozen
questions, `quality` achieved Recall@10 `0.8381619769`, MRR@10 `1.0`, and nDCG@10
`0.8520010048`; on the hard 10 it achieved `0.955`, `1.0`, and `0.8827017521`.
Every one of 400 retained direct hits passed independent evidence validation.

The separately evaluated multisignal coverage gate materially improved evidence
readiness. Its accepted English and machine-readable artifacts are
`hard10-coverage-pack-multisignal-mcp-runtime-gate.md` and
`hard10-coverage-pack-multisignal-mcp-runtime-gate.json`; their SHA-256 values are
`5765f88417db965ee67d13ba6ec390694ba7077d1c3f41fe4667155ab274ef09`
and `2b5cb590f11341c5b45d31b76773eb92a3213cf0d479f14c98685f19f818f241`,
respectively.
Adaptive facets covered 34/44 hard-question answer groups, reviewed graph claims
covered 21/44, pinned semantic claims covered 38/44, and the gated union covered
41/44 (93.0%). The union covered all 13 important-negative groups and all required
papers, and all 713 distinct bindings passed exact independent validation. These
measure candidate availability and evidence identity, not correctness,
completeness, or entailment.

The historical bounded-MCP prototype smoke additionally verified that q031's complete
deduplicated union contains 198 claims and is reproducibly transported over five
`semantic_okf_coverage_brief` pages. The largest raw JSON page was 36,368 bytes; every page bound
the same full-coverage SHA-256
`76be5ecd39f99bb682bbe0b734d8df25867594411bd3b906ce15e71f85528fb2`,
and no claim was duplicated or omitted. Its then-current single-tool
`semantic_okf_finalize_answer` prototype remained unavailable until deep inspection
and every coverage page completed, then independently recomputed the unpaged pack.
ADR 0024 replaced that interface with the historical four-tool MCP v1.3.1 recoverable
transaction. ADR 0025 replaces its long-copy confirmation step with the active v1.4.0
prepared-envelope and short-digest protocol; the historical smoke remains
bounded-transport evidence only.
On manual q031 finalization, the semantic route recovered
`claim-2506-05690v3-044`, yielding 4/4 answer groups, seven supported facets, one
partial facet, and zero unresolved facets without changing the bundle.

These results accept final-03 for build integrity, deterministic direct retrieval,
and answer-evidence preparation. Generated-answer correctness, completeness,
grounding, response-contract compliance, and causal treatment effects remain pending
until a successful isolated Skill Arena run and independent blinded evaluation are
published.

## Benchmark boundary

The forty retrieval questions and hard ten answer questions have been used for
selection and diagnosis. They are a frozen regression and optimization target, not
an untouched holdout. The constants are global and query-independent and contain no
answer labels, but their observed performance remains subject to benchmark selection
bias.

Reports may call this the best observed balanced policy on the frozen contract after
real reproduction. They must not claim universal or out-of-domain superiority. Such
a claim requires a new versioned benchmark, an untouched question cohort, broader
source types and languages, and latency-aware validation. Corrections to frozen
questions or ground truth require a new benchmark ID and manifest rather than an
in-place edit.

## Consequences

Positive:

- direct-search breadth is structurally preserved while four-route consensus
  improves ordering;
- reviewed graph paths and binding-filtered semantic claim search recover bounded,
  complementary answer candidates without admitting co-mention edges or similarity
  scores as facts;
- exact sections and claim-to-section joins make evidence navigation auditable;
- deterministic finalization protects identifiers, paths, locators, pages, and
  citations from model reconstruction errors;
- explicit quality, fast, and robust policies expose cost and route behavior; and
- the new pair remains independently installable and leaves every prior alternative
  unchanged for comparison.

Negative:

- the ensemble is larger and slower than a classical-only projection;
- the quality policy fails closed without its exact pinned semantic runtime;
- a protected set cannot recover a direct-search paper absent from adaptive top-*k*;
- bounded coverage can still omit a required reviewed claim;
- structural finalization cannot prove that drafted prose is semantically entailed;
  and
- the selected constants remain optimized on a repeatedly used benchmark until a
  fresh cohort is evaluated.
