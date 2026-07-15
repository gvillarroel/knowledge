---
adr: "0022"
title: "ADR 0022: Freeze the Benchmark and Evolve Adaptive Semantic OKF Answer Evidence"
summary: "Freeze the forty-question Semantic OKF benchmark, add verified non-authoritative answer bindings and deterministic answer assembly, and retain complementary adaptive consult policies under isolated control/treatment evidence."
status: "Accepted"
date: "2026-07-15"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - frozen-benchmark
  - adaptive-retrieval
  - evidence-binding
  - deterministic-finalization
  - skill-arena
  - population-search
---

# ADR 0022: Freeze the Benchmark and Evolve Adaptive Semantic OKF Answer Evidence

## Status

Accepted.

This decision extends ADR 0015, ADR 0017, ADR 0019, ADR 0020, and ADR 0021. It supersedes ADR 0021's
answer-treatment conclusion while preserving its retrieval architecture and results. The legacy,
embedding, classical, and entity-graph packages remain unchanged comparison alternatives.

## Context

The first adaptive retrieval generation achieved the highest observed all-40 Recall@10 and nDCG@10,
but its isolated consult treatment lost answer facets and corrupted evidence fields during model-side
serialization. Repeatedly editing both a skill and its questions would make improvement impossible to
distinguish from benchmark overfitting or test falsification.

The next generation therefore needed a hard boundary between mutable skill implementation and
immutable evaluation inputs. It also needed to distinguish three answer properties:

1. finding likely evidence;
2. choosing a minimal set that directly entails the answer; and
3. serializing exact authoritative identities and locators.

All new mechanisms must preserve the authoritative Semantic OKF core. Rankings, topics, term
associations, query facets, graph projections, answer bindings, and answer packs remain derived,
non-authoritative data.

## Decision

### Freeze the benchmark

Adopt `semantic-okf-adaptive-frozen-40-plus-hard10-v1` as an immutable fixed benchmark. Its manifest
binds seventeen files, including:

- the original thirty and expanded forty retrieval questions;
- ten evidence-first hard questions and their ground truth;
- the authoritative corpus inventory and build manifest;
- answer assertions and evaluator implementations; and
- incumbent retrieval and grounded-answer reports.

The validator enforces exact hashes, order, 30+10 composition, qrel alignment, and prompt isolation.
Skill candidates may change only their standalone build or consult packages. A genuine benchmark
correction requires a new benchmark ID and manifest; it must never be made silently in place.

### Add verified answer bindings

Advance the adaptive derived projection to schema 1.2 and publish
`adaptive/answer-bindings.jsonl`. It contains one closed binding for each of 831 reviewed claim
records. Every row copies or deterministically derives:

- the exact claim record ID and reviewed interpretation;
- authoritative-text and Semantic OKF record hashes;
- paper and source identities;
- concept and source paths;
- declared paper evidence paths and `PDF-page-N` locator tokens; and
- sorted integer citation pages.

The builder independently rederives and validates the complete binding artifact before atomic
publication. Consultation loads it read-only and rejects missing, duplicate, stale, malformed, or
unclosed rows. The binding artifact is an evidence adapter, not a new source of domain truth.

### Separate candidate discovery from final evidence selection

Retain the ordinary adaptive search route unchanged for the all-40 retrieval comparison. For hard
answer construction, rank reviewed claims using a 2:1 fusion of full-record and reviewed-interpretation
views, initially cap contribution at three claims per paper, and backfill only after paper diversity.

Expose two additional read-only operations:

- `coverage-pack` deterministically decomposes a question into bounded lexical facets and retains a
  separate paper-diverse candidate list for each facet; and
- `finalize-answer` accepts only a compact external or stdin draft, rejects unknown claim IDs and
  in-bundle drafts, and reconstructs all paper IDs, citations, evidence rows, paths, and locators from
  verified bindings.

Facet expansion is discovery only. The final consult policy must minimize support to directly
entailing records, remove unused and merely topical evidence, split broad claims, and qualify an
unresolved facet instead of returning a null answer when a substantive partial answer is supported.

### Use fixed-contract population search and isolated causal comparisons

Score candidates under the predeclared fitness contract with hard gates for the frozen benchmark,
package validation, deterministic rebuild, authoritative-core parity, evidence validity, ordinary
retrieval no-regression, question-ID isolation, and read-only consultation. Use three sequential
executions per hard question. Retain complementary Pareto survivors rather than collapsing every
property into one scalar winner.

Use Skill Arena only as a two-profile control/treatment comparison: the same pinned bundle with no
consult skill versus the same bundle with exactly one adaptive consult skill. Do not treat an
all-skills portfolio as causal evidence. Keep model, prompts, workspace, restrictions, and task object
identical across profiles and generations.

## Evidence and selection

Generation 0 evaluated ten explicit answer-ranking hypotheses:

- candidate 02 is the efficiency/paper-coverage survivor, with 100% required-paper Recall@30; and
- candidate 07 is the evidence-coverage survivor, with 60% exact answer-claim Recall@30 and 75%
  important-negative recall.

Candidate 07 became the canonical code base because evidence coverage is the binding constraint for
multi-paper synthesis.

Generation 1 added facet candidate generation and deterministic finalization. It improved formal
response conformance but its unrestricted evidence-selection policy reduced correctness, validity,
grounding, and negative coverage. Discard that policy while retaining both mechanisms.

Generation 2 added minimal direct support. In its isolated paired run, the treatment achieved:

- 100% response-contract compliance;
- 98.0% correctness and 84.75% completeness;
- 94.40% evidence validity and 93.68% grounding;
- 53.5% exact atomic-ID coverage;
- 93.0% required-paper and 91.33% required-source coverage; and
- 100% important-negative coverage.

Relative to its same-run control, it improved response contract by 90.0 points, evidence validity by
20.86, grounding by 21.11, exact-ID coverage by 4.0, paper coverage by 3.83, and source coverage by
12.17. It reduced correctness by 0.75 points and completeness by 4.25 points. Keep generation 2 as the
default adaptive policy and generation 0 as the complementary high-grounding/exact-ID survivor.

The facet union raises exact answer-claim candidate coverage from 60.0% in the primary top 30 to
76.5%, negative coverage from 75.0% to 88.33%, and required-paper coverage from 98.0% to 100%. It
averages 81 unique candidates, so it must not be reported as Recall@30.

## Expected-ID interpretation

The independent audit found all 44 atomic expected-ID mappings sensible and reproduced 42 unique
reviewed claim records, their source lines, locator pages, hashes, answer bindings, and four configs
without mismatch. Forty mappings are direct record paraphrases, three are bounded derivations, and one
adds a detail supported by the exact paper page.

Exact atomic-ID coverage is deliberately stricter than semantic correctness. It may under-credit an
otherwise correct answer that uses another valid record. Important-negative ID assertions only test
the presence of at least one declared evidence anchor; blinded semantic review remains necessary to
verify that the answer actually states the exclusion, contrast, or failure boundary.

## Consequences

Positive:

- evaluation questions and ground truth cannot drift with the candidate skill;
- exact evidence serialization no longer depends on model reconstruction;
- facet discovery exposes missing mechanisms without weakening the fixed-budget retrieval table;
- minimal direct support materially improves evidence validity, grounding, and response conformance;
- ordinary all-40 retrieval remains unchanged at 83.82% Recall@10 and 83.43% nDCG@10 with 100%
  evidence validity; and
- every new artifact remains closed, hash-bound, deterministic, offline-capable, independently
  validated, atomically published, and read-only during consultation.

Negative:

- the ten hard questions are now a fixed optimization target, not an untouched holdout;
- exact-ID metrics can penalize semantically equivalent evidence;
- candidate facet unions use a larger and variable budget;
- control answer quality varies across stochastic runs, so only within-run deltas are causal;
- no generation yet passes every strict conjunctive assertion; and
- the generation-2 evidence-minimization policy trades a small amount of completeness for much stronger
  evidence mechanics.

A new untouched question cohort and broader domains are required before claiming general superiority.
Until then, classical fusion remains the simpler broad retrieval default, entity graph remains the
auditable navigation alternative, generation 2 is the default adaptive answer policy, and generation
0 remains its complementary evidence-coverage survivor.
