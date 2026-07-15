---
adr: "0021"
title: "ADR 0021: Add Adaptive Evidence Fusion to Semantic OKF"
summary: "Add a standalone, source-generic Semantic OKF builder and read-only consultant that preserve the authoritative core while combining deterministic full-query, aspect, lexical, topic, and association evidence selection."
status: "Accepted"
date: "2026-07-14"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - adaptive-retrieval
  - bm25
  - topic-modeling
  - query-decomposition
  - evidence-contract
---

# ADR 0021: Add Adaptive Evidence Fusion to Semantic OKF

## Status

Accepted.

This decision extends ADR 0008, ADR 0010, ADR 0012, ADR 0014, ADR 0015, ADR 0017,
ADR 0019, and ADR 0020. It creates a new standalone generation and does not modify the legacy,
embedding, classical, or entity-graph packages.

## Context

The classical Semantic OKF alternative is the strongest broad retriever in the forty-question
benchmark. Its full-query fusion nevertheless treats a long, multi-part question as one lexical
request. A single ranking can underrepresent a contrast, exclusion, failure boundary, or secondary
mechanism even when the required evidence is present in the corpus.

A broadly reusable alternative must not depend on GraphRAG-specific filenames, arXiv identifiers,
PDF-page headings, or claim schemas. It must accept arbitrary declared Markdown, CSV, JSON, JSONL,
and RDF sources while still permitting an evaluation plan to opt known paper sources into exact page
passages and shared reviewed-paper identities. Automatically inferred topics, term associations,
query aspects, and rankings must remain non-authoritative discovery signals.

The answer-facing contract also needs stronger protection than a list of ranked passages. Previous
answer evaluations showed that a model can retrieve valid evidence and then corrupt a claim ID,
source path, paper identity, or page locator while serializing the response. The retriever should
therefore copy exact bound fields into deterministic evidence rows and require verification against
the authoritative ledger.

## Decision

Ship two independently installable skills:

1. `build-semantic-okf-adaptive` builds the unchanged authoritative Semantic OKF core and a derived
   adaptive retrieval projection.
2. `consult-semantic-okf-adaptive` validates and queries a published projection without writing it.

Each package contains its own runtime implementation and requirements. Neither imports a sibling
skill, repository evaluation helper, or repository document at runtime. The independently copied
builder and consultant plan validators are parity-tested across valid and invalid plans.

The builder publishes a closed `adaptive/` tree containing:

- `documents.jsonl`, with exact passages, source-scoped identities, authoritative bindings, lexical
  fields, topic weights, locators, and text hashes;
- `lexicon.json`, with persisted Bag-of-Words and Okapi BM25 statistics;
- `associations.jsonl`, with bounded two-step positive-PMI term neighbors;
- `topics.json`, with deterministic weighted term communities and document topic weights;
- `index.json`, which binds the closed plan, algorithms, authoritative core, inputs, counts, and
  artifact hashes; and
- `build-report.json`, which records validation and publication results but is not domain evidence.

The version 1.1 plan has closed schemas for source selection, passage construction, evidence identity,
tokenization, BM25, associations, topics, expansion, diversity reranking, and adaptive fusion. Its
generic defaults are intentionally conservative:

- one full-record passage per selected record;
- the collision-safe evidence identity `source-record / source_id / record_id`; and
- no guessed paper identity from a title, path, header, or identifier-like string.

A plan may explicitly opt declared Markdown sources into PDF-page heading segmentation and may map
multiple sources to one reviewed paper identity. Those options are configuration, not corpus-specific
runtime behavior. Page segmentation rejects non-Markdown sources.

Consultation exposes the classical component routes `bm25`, `topic`, `association`, and `fusion`, plus
`adaptive`. Adaptive mode:

1. runs the complete question through the full classical fusion route;
2. deterministically decomposes a long question into bounded, coverage-preserving aspects while
   retaining contrast markers and repeated clauses;
3. ranks each non-duplicate aspect independently;
4. combines the full and aspect rankings through pinned reciprocal-rank weights;
5. protects the first nine full-query results; and
6. admits a new evidence identity outside the full-query top ten only when it ranks first for an
   aspect.

The conservative admission gate prevents aspect expansion from displacing broad full-query evidence
with weak lexical fragments. The plan records all weights, caps, and algorithms, so the decision is
reproducible offline.

Every search route emits `evidence_rows` using the `exact-authoritative-fields-v2` adapter. The adapter
copies source ID, record ID, concept path, source path, locator, record hash, text hash, and evidence
text from validated projection bindings. It never reconstructs identities from filenames or prose.
Locators address `semantic/records.jsonl` `record.body`; concept Markdown is the readable mirror after
YAML frontmatter. Retrieval output remains discovery-only and requires authoritative verification.

The builder rejects symlinks and junctions throughout inputs and output paths, builds in a private
sibling payload, independently rederives the projection, and performs one atomic replacement only
after validation. Failure removes the private candidate and leaves no destination. The consultant
rejects an unclosed or stale bundle and performs no cache, repair, log, or query write.

## Evaluation decision

The retrieval comparison uses the same fifteen Markdown papers, fifteen reviewed-claim JSONL files,
separately declared analysis vocabulary, unchanged authoritative core, original thirty questions, and
ten evidence-first hard questions used by the prior alternatives. It evaluates thirteen direct
top-10 routes under the evidence-valid schema 1.2 contract.

Adaptive parameters were selected on the original thirty questions. The hard ten served as a frozen
no-regression cohort during selection, not as an untouched post-selection statistical holdout. The
same hard questions are also used in a paired Skill Arena knowledge-only control versus one-skill
treatment comparison. That paired structure can estimate the effect of adding the consult instructions
within this benchmark, but repeated use means the hard ten must not be presented as a fresh population
generalization test.

The accepted retrieval run reports:

- adaptive fusion: 83.8162% all-question recall@10, 95.8333% MRR@10, and 83.4272% nDCG@10;
- classical fusion: 83.4591% recall@10, 95.8333% MRR@10, and 83.2286% nDCG@10;
- an exact adaptive/classical tie on the hard ten: 95.5% recall@10, 95.0% MRR@10, and 84.9848%
  nDCG@10; and
- 100% independently valid evidence with zero query errors for every route.

Adaptive therefore has the highest observed overall recall and nDCG, by 0.3571 and 0.1986 percentage
points over classical fusion. The entire metric difference comes from `q011-vector-graph-hybrid`; the
other 39 questions tie on these paired metrics. A deterministic paired-question bootstrap gives a 95%
descriptive interval of 0 to 1.0714 points for recall and 0 to 0.5959 points for nDCG. Because both
intervals include zero and the hard cohort ties, the result does not establish a general superiority
claim. Adaptive mean query time is 296.45 ms versus 94.63 ms for classical fusion, approximately 3.13
times slower in the recorded in-process diagnostic.

The accepted isolated answer run contains twenty completed cells, ten knowledge-only controls and ten
single-skill treatments, with zero execution errors. The adaptive bundle's control is strong: 97.50%
claim correctness, 90.25% semantic completeness, 93.23% independently valid answer evidence, and
93.32% grounding. Adding `consult-semantic-okf-adaptive` reduced those metrics to 93.58%, 57.25%,
59.33%, and 60.00%. Exact curated evidence-identity coverage fell from 73.50% to 19.50%.

The treatment preserved high fidelity for the claims it did state, but it omitted required facets and
four of ten answers still serialized full source locator strings into integer page fields. An earlier
diagnostic exposed the same serialization family and led to stricter instructions; the accepted run
used those instructions but did not establish a reliable repair. Because the same ten questions were
used for diagnosis and rerun, differences between the two stochastic runs are not a causal estimate
of the instruction change. The architectural implication is that exact answer evidence must move to a
deterministic serializer outside the answer model. The current adaptive consult skill is retained as
an evaluated experimental package, not selected as the default answer-construction treatment.

Large bundles and raw runs remain append-only and ignored. Compact plans, questions, ground truth,
configuration manifests, environment bindings, determinism evidence, retrieval summaries, answer
summaries, and English evaluation documentation are checked in.

## Consequences

Positive:

- long questions can retrieve evidence for distinct mechanisms, exclusions, and failure conditions;
- exact evidence rows reduce answer-time identity reconstruction errors;
- arbitrary sources have safe generic passage and identity defaults;
- every derived signal is persisted or deterministically rederived and participates visibly in
  ranking;
- two clean 890-file builds are byte-identical, and all five routes are invariant across twenty Python
  hash seeds; and
- the new pair remains separately installable without changing any established baseline.

Negative:

- adaptive mode performs several full component rankings and is materially slower than classical
  fusion;
- the English ASCII-alphanumeric tokenizer and English stopword list are not language-neutral;
- aspect boundaries are deterministic lexical heuristics, not reviewed semantic decompositions;
- the current aggregate gain is concentrated in one question and should not justify replacing the
  classical default by itself;
- the current consult treatment reduces completeness, exact evidence coverage, and grounding relative
  to its same-bundle knowledge-only control; and
- direct top-10 paper recall does not measure the larger candidate-pool sensitivity previously found
  for chunk-based embedding routes.

A future selection decision requires a new untouched question set, broader source domains, and a
latency-aware utility target. It also requires a deterministic evidence-to-response adapter that
enforces exact claim IDs, paths, paper identities, integer pages, and citation agreement without model
reconstruction. Until then, adaptive fusion is an evidence-backed retrieval option for complex
multi-aspect queries, classical fusion remains the simpler broad default, and embedding consultation
has the strongest observed isolated answer-treatment effect.
