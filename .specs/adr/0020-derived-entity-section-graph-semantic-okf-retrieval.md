---
adr: "0020"
title: "ADR 0020: Add a Derived Entity-to-Section Graph for Semantic OKF Retrieval"
summary: "Project reviewed Semantic OKF claims and deterministic entity mentions into a closed graph whose evidence edges terminate at exact source sections, without changing the authoritative core."
status: "Accepted"
date: "2026-07-14"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - entity-graph
  - provenance
  - retrieval
  - graph-traversal
---

# ADR 0020: Add a Derived Entity-to-Section Graph for Semantic OKF Retrieval

## Status

Accepted.

This decision extends ADR 0008, ADR 0010, ADR 0012, ADR 0014, ADR 0015, ADR 0017,
and ADR 0019. It adds a new standalone generation and does not modify the legacy,
embedding, or classical packages.

## Context

The existing Semantic OKF alternatives provide authoritative ledger and concept navigation,
embedding retrieval, and deterministic lexical/topic/association retrieval. None materializes a
single graph that begins with extracted entities, preserves reviewed claim relations, and terminates
at exact file sections suitable for evidence verification.

An entity graph introduces an authority risk. Automatic phrases, mentions, and co-occurrences can
be useful retrieval signals, but they are not reviewed facts. Treating a co-mention as a semantic
relation would silently weaken the Semantic OKF evidence contract. A graph also needs stable section
identities, exact locators, deterministic rebuilds, and a way to distinguish reviewed edges from
candidate edges during traversal.

## Decision

Ship two independently installable skills:

1. `build-semantic-okf-entity-graph` builds the unchanged authoritative Semantic OKF core and a
   derived `entity-graph/` projection.
2. `consult-semantic-okf-entity-graph` validates and queries a published projection read-only.

The packages duplicate their small shared deterministic graph model so neither imports a sibling
skill or repository helper. Package tests require those copies to remain byte-identical.

The builder selects the exact fifteen paper sources, fifteen reviewed-claim sources, and separately
declared analysis vocabulary through a closed plan. It creates:

- `sections.jsonl`, with one stable node per PDF-page section, an exact Unicode character range,
  source path, authoritative concept identity, text, and text hash;
- `entities.jsonl`, with reviewed paper, claim, method, and dimension identities plus separately
  labeled candidate phrases extracted by bounded salient n-grams;
- `mentions.jsonl`, with deterministic normalized phrase-to-section matches;
- `edges.jsonl`, with reviewed claim-to-paper, claim-to-dimension, and claim-to-evidence-section
  paths, reviewed paper-to-section paths, candidate mention paths, and candidate co-mention paths;
- `lexicon.json`, with the exact section Bag-of-Words statistics used by BM25; and
- closed `index.json` and `build-report.json` files binding the plan, algorithms, authoritative core,
  source inventory, artifact hashes, counts, and authority markers.

Every node and edge has an explicit `review_state`. A reviewed edge is a deterministic projection of
an already reviewed Semantic OKF identity or evidence locator. Automatically extracted phrases,
mentions, co-mentions, weights, graph paths, and rankings remain candidate or discovery-only. In
particular, `coMentionedWith` never establishes a factual domain relation, and absence of an edge is
not evidence of absence.

The accepted graph shape is:

```text
reviewed method/dimension -> reviewed claim -> exact evidence section -> reviewed paper
candidate phrase          -> exact mention section             -> reviewed paper
candidate phrase          -> candidate co-mention phrase
```

Consultation exposes four routes:

- `lexical`: section-level Okapi BM25;
- `entity`: exact and partial entity resolution followed by mention and reviewed-claim evidence
  scoring;
- `traversal`: bounded propagation across reviewed and candidate edges with separate pinned weights;
  and
- `fusion`: reciprocal-rank fusion of the other routes followed by a plan-pinned per-paper cap.

Query results expose exact sections, component scores, resolved entity state, graph edge identities,
and, for reviewed claims, the authoritative `record_id`, concept path, source-record path, and
claim-evidence page bindings. Graph paths explain discovery; answers must still open and cite the
reviewed claim and exact paper section.

The builder publishes from a private sibling only after core and graph validation. Independent
validation rederives the entire graph in memory and requires the closed file set, safe paths,
referential integrity, exact section ranges and hashes, reviewed record identities, lexical
statistics, core hash, plan hash, artifact hashes, and build report to match. Consultation performs
no cache or bundle writes and can request the same deep rederivation.

Evaluation retains the frozen forty-question benchmark and ten hidden evidence-first hard-question
ground truths. Retrieval compares twelve routes across legacy, embedding, classical, and entity-graph
packages under one evidence-valid schema and identical authoritative-core hash. Answer behavior uses
a paired Skill Arena comparison in which the same model, questions, and graph bundle are used for a
knowledge-only control and a single consult-skill treatment.

The accepted direct top-10 run found 91.7% hard-question paper recall for entity-graph fusion, versus
80.7% for legacy lexical and 95.5% for classical fusion, with 100% independently valid retrieval
evidence. The paired answer run did not show a treatment benefit: the entity-graph consult treatment
reduced grounding and semantic completeness relative to its same-bundle control. This negative result
is retained. It shows that better evidence retrieval does not guarantee reliable claim-ID, path, and
page serialization by an answer agent.

## Consequences

Positive:

- entities and reviewed relations now lead directly to exact file sections;
- graph-only entity and traversal routes materially participate in evidence selection;
- the deterministic offline baseline is independently rebuildable and inspectable;
- reviewed and candidate semantics cannot be confused without violating a closed schema; and
- the new package can complement lexical, topic, association, and embedding routes without changing
  their frozen baselines.

Negative:

- the projection is larger than a pure lexical index and duplicates section text for read-only
  retrieval;
- candidate phrase extraction includes some generic terms, so candidate weights must remain bounded
  and visible;
- graph traversal can amplify noisy co-mentions if treated as evidence rather than discovery; and
- answer agents can still corrupt otherwise valid evidence by reconstructing claim IDs, paths, or page
  locators instead of copying authoritative fields.

A future change may add a deterministic evidence-to-response adapter that emits contract-ready claim,
paper, path, and page rows. That adapter requires a separate decision and holdout evaluation; it is not
retroactively tuned into this frozen benchmark result.
