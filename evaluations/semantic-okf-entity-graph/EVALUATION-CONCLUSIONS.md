# How to Read the Semantic OKF Evaluation Results

This document explains what the reported numbers mean, what the evaluation does and does not prove,
and which Semantic OKF alternative is the best current choice for each role.

## Executive conclusion

The evaluation produced two different findings that must not be collapsed into one score:

1. **Retrieval:** the new entity graph works. It finds substantially more of the required evidence for
   hard multi-paper questions than the legacy lexical route, and every returned section passed the
   independent evidence validator.
2. **Answer construction:** the current entity-graph consult instructions do not yet turn that better
   retrieval into better final answers. In the paired Skill Arena run, the treatment lost correctness,
   completeness, evidence validity, and grounding relative to the same graph bundle without the skill.

The later adaptive evaluation reinforces that separation. Its bundle produced the strongest
knowledge-only answer control, but its consult treatment also reduced completeness, evidence validity,
and grounding. A strong index is not sufficient when the answer model must reconstruct exact evidence
fields or fails to close every requested synthesis facet.

Adaptive fusion now has the highest observed overall recall and nDCG, but its entire lead over classical
fusion comes from one of forty questions; the hard ten tie exactly and adaptive is about three times
slower. Classical fusion therefore remains the simpler broad default, while adaptive is an option for
long multi-aspect questions. The entity graph remains a strong complementary retriever and audit index.
It should not yet be the sole answer-construction path until claim IDs, paths, paper IDs, and page
locators are emitted by a deterministic adapter instead of reconstructed by the answer model.

## The evaluation has four separate layers

| Layer | Question it answers | What was measured |
| --- | --- | --- |
| Retrieval | Did the route find the required papers? | Recall@10, MRR@10, nDCG@10 |
| Retrieval evidence | Are returned hits real and traceable? | Exact source, concept, locator, text-hash, and core-parity validation |
| Answer quality | Did the final response state the right and complete conclusions? | Blinded correctness, semantic completeness, and important-negative coverage |
| Answer grounding and contract | Did the response cite authoritative evidence in the required form? | Evidence validity, grounding, required papers/sources, and response-contract compliance |

Retrieval metrics must not be interpreted as answer correctness. A route can retrieve the right paper
and an answer agent can still copy the wrong claim ID or format a page locator incorrectly.

## Retrieval metric definitions

### Recall@10

Recall@10 measures the fraction of required paper identities present in the first ten paper-level
results, averaged across questions.

For example, entity-graph fusion has **91.67% hard recall@10**. This means that its top ten results
contained, on average, 91.67% of the papers required by the ten hard ground truths. It does not mean
that 91.67% of generated answers were correct.

Recall is the most important retrieval metric for these synthesis questions because missing one of the
required papers can remove an entire side of a comparison or an important failure condition.

### MRR@10

Mean Reciprocal Rank rewards putting the first relevant paper near the top. A first relevant hit at rank
1 contributes 1.0, rank 2 contributes 0.5, rank 3 contributes about 0.333, and no relevant hit in the
first ten contributes zero.

Entity-graph lexical retrieval has **96.67% overall MRR@10**, the highest first-hit score in the table.
This indicates excellent early precision, but it does not establish broad multi-paper coverage.

### nDCG@10

Normalized Discounted Cumulative Gain evaluates the ordering of all relevant papers in the first ten.
It rewards placing several required papers near the top and discounts relevant papers that appear late.

Classical fusion has **84.98% hard nDCG@10**, compared with **76.32%** for entity-graph fusion. The
classical route therefore orders the complete hard-question evidence set more effectively.

### Evidence validity

Evidence validity is not an information-retrieval relevance score. It independently verifies that each
returned hit has a valid authoritative identity, safe path, exact locator, matching text hash, and the
same Semantic OKF core hash as every other alternative.

All thirteen routes achieved **100% retrieval evidence validity with zero query errors**. This means the
retrieval comparison is not being inflated by nonexistent paths or stale bundle contents.

## Direct top-10 retrieval results

| Builder / consultant | Route | All recall@10 | All MRR@10 | All nDCG@10 | Hard recall@10 | Hard MRR@10 | Hard nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | lexical | 79.31% | 78.96% | 74.22% | 80.67% | 57.50% | 56.81% |
| Embedding | lexical | 54.75% | 88.83% | 60.92% | 73.50% | 80.33% | 65.78% |
| Embedding | vector | 50.40% | 78.75% | 54.77% | 61.00% | 66.67% | 53.05% |
| Embedding | hybrid | 48.34% | 88.54% | 56.51% | 65.17% | 87.50% | 64.60% |
| Classical | BM25 | 49.72% | 95.83% | 60.94% | 63.17% | 95.00% | 69.31% |
| Classical | topic | 82.42% | 93.33% | 82.25% | 93.00% | 95.00% | 83.75% |
| Classical | association | 82.56% | 94.58% | 82.58% | 93.00% | 95.00% | 84.76% |
| Classical | fusion | 83.46% | 95.83% | 83.23% | **95.50%** | **95.00%** | **84.98%** |
| Entity graph | lexical | 79.76% | **96.67%** | 81.14% | 84.67% | 86.67% | 74.47% |
| Entity graph | entity | 79.58% | 86.04% | 76.72% | 85.00% | 71.67% | 66.08% |
| Entity graph | traversal | 78.49% | 80.21% | 74.03% | 86.67% | 75.00% | 69.65% |
| Entity graph | fusion | 80.84% | 93.12% | 79.86% | 91.67% | 90.00% | 76.32% |
| Adaptive | fusion | **83.82%** | 95.83% | **83.43%** | **95.50%** | **95.00%** | **84.98%** |

### Important comparisons

- Entity-graph fusion improves hard recall over legacy lexical by **11.00 percentage points**:
  91.67% versus 80.67%.
- Classical fusion remains **3.83 points ahead** of entity-graph fusion on hard recall:
  95.50% versus 91.67%.
- Entity-only and traversal-only hard recall, 85.00% and 86.67%, both exceed legacy lexical. This is
  direct evidence that graph signals materially participate in evidence selection.
- Entity-graph lexical has the best overall MRR, while graph fusion has better coverage. The lexical
  route is strongest when the first precise section matters; fusion is preferable for multi-paper
  synthesis.
- Adaptive fusion improves overall recall over classical fusion by **0.36 percentage points** and
  nDCG by **0.20 points**, but all of that difference comes from `q011-vector-graph-hybrid`. The other
  39 questions tie on recall, MRR, and nDCG, and the hard ten tie exactly.
- Adaptive mean query time is approximately **3.13x** classical fusion in this diagnostic. This makes
  classical fusion the simpler default until a new untouched benchmark shows a distributed adaptive
  gain.

## Why the embedding numbers change with candidate-pool size

The direct table asks each route for ten raw results and then deduplicates them to papers. Chunk-based
embedding routes can return several chunks from one paper, leaving fewer than ten distinct papers.

The pool-100 comparison asks for 100 candidates before paper deduplication and scores the first ten
distinct papers. Under that protocol:

| Embedding route | Direct hard recall@10 | Pool-100 hard recall@10 | Change |
| --- | ---: | ---: | ---: |
| Lexical | 73.50% | 93.00% | +19.50 points |
| Vector | 61.00% | 78.00% | +17.00 points |
| Hybrid | 65.17% | 90.50% | +25.33 points |

This is not a contradiction. It shows that the embedding package is sensitive to the raw chunk budget
and needs a larger candidate pool or earlier paper-aware diversification. Classical and entity-graph
routes already apply paper-aware diversification, so their scores do not change between these runs.

## Grounded-answer results

The ten hard questions were also answered by actual agents. Each package used a paired design:

- the control received the pinned knowledge bundle but no declared consult skill;
- the treatment received the same bundle, model, question, sandbox, and timeout plus exactly one
  consult skill.

The absolute treatment scores were:

| Consult treatment | Contract | Evidence validity | Grounding | Correctness | Completeness | Required papers | Negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | 10.0% | 84.3% | 83.5% | 88.8% | 75.0% | 75.0% | 90.0% |
| Embedding | 40.0% | **83.6%** | **83.4%** | **96.2%** | **82.8%** | **89.2%** | **100.0%** |
| Classical | 30.0% | 80.4% | 79.7% | 91.5% | 82.2% | 86.7% | 95.0% |
| Entity graph | 40.0% | 60.0% | 60.0% | 78.8% | 70.2% | 67.7% | 90.0% |
| Adaptive | 20.0% | 59.3% | 60.0% | 93.6% | 57.2% | 69.7% | 100.0% |

Correctness and completeness were scored by a blinded fixed-rubric reviewer that did not receive the
method or treatment labels. Evidence validity and grounding were recomputed deterministically against
the authoritative ledger and concepts.

## How to read the causal deltas

The following values are treatment minus same-bundle control. A positive value favors adding the
consult skill; a negative value favors the knowledge-only control in this run.

| Method | Correctness | Completeness | Evidence validity | Grounding | Required papers | Negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | -5.2 points | -8.2 | +1.7 | +0.6 | -7.2 | -10.0 |
| Embedding | +1.0 | +2.0 | +12.7 | +12.4 | +11.7 | +2.5 |
| Classical | -4.0 | 0.0 | -3.5 | -3.6 | +7.0 | -5.0 |
| Entity graph | -21.2 | -11.8 | -15.6 | -16.0 | -16.5 | -10.0 |
| Adaptive | -3.9 | -33.0 | -33.9 | -33.3 | -18.7 | 0.0 |

Only the embedding treatment showed a consistent positive answer-level effect across correctness,
completeness, evidence validity, grounding, required papers, and important negatives.

The adaptive treatment kept stated-claim correctness high but omitted many required facets and
returned source locator strings where four answers required integer PDF pages. Its same-bundle control
scored 97.5% correctness, 90.2% completeness, 93.2% evidence validity, and 93.3% grounding, so the
negative treatment result is not evidence that the adaptive bundle lacks useful knowledge.

The entity-graph treatment result is a real negative finding, not a retrieval failure. Inspection of
the outputs found answer-assembly errors such as reconstructing a claim ID from a concept filename,
changing punctuation in a paper or claim identity, returning full source fragments where integer page
locators were required, and abstaining on one answerable question. The underlying graph retrieval hits
still passed the independent evidence validator.

## Why strict all-contract pass is zero

The strict Skill Arena cell passes only when every sub-contract succeeds simultaneously: JSON key
order, word limits, exact claim identities, path spelling, page types, citation agreement, atomic
answer coverage, and important negatives. One failed condition fails the complete cell.

Every method had a 0% strict full-pass rate, even when its semantic correctness was above 90%. The
strict result is therefore retained as a conformance stress test, while the component metrics are used
to diagnose answer quality. It should not be reported as “all answers were wrong.”

## Recommended use of each alternative

| Need | Recommended route | Reason |
| --- | --- | --- |
| Broad multi-paper synthesis | Classical fusion | Best hard recall and nDCG; deterministic and offline |
| Long question with several aspects or exclusions | Adaptive fusion | Preserves full-query evidence and can add one top-ranked aspect result |
| Auditable entity-to-claim-to-section navigation | Entity-graph fusion or traversal | Explicit graph path to exact hashed sections |
| Fast first precise hit | Entity-graph lexical | Highest overall MRR in this benchmark |
| Semantic paraphrase retrieval | Embedding hybrid with a large candidate pool | Captures semantic similarity, but needs paper-aware deduplication |
| Stable regression baseline | Legacy lexical | Simple frozen comparison point |
| Current end-to-end answer treatment | Embedding consult | Only treatment with consistently positive paired answer deltas |

The recommended production architecture is classical fusion as the primary broad retriever plus the
entity graph as a complementary audit and relation-traversal index. Candidate sets can be combined,
but factual support must continue to come from reviewed claims and exact authoritative sections.

## Next experiment

The next graph evaluation should freeze the current retriever and add a deterministic evidence adapter
that copies, without model reconstruction:

- authoritative claim record IDs;
- concept and claim-source paths;
- versioned paper IDs;
- integer PDF pages; and
- mutually consistent citations and evidence rows.

It should be evaluated on a new holdout against at least classical fusion alone, entity-graph fusion
alone, and a diversified union of both. Reusing the current ten hard questions for tuning would weaken
the causal evidence.

## Limitations

- The hard-answer causal estimate contains ten questions and one model route.
- The answer intervals are not confidence-bounded population estimates.
- The same model family generated and reviewed answers, although the reviewer was blinded and had no
  tools, skill, method label, or previous answer context.
- Candidate entities and co-mentions are corpus-derived discovery signals, not reviewed semantic facts.
- Retrieval quality is measured at paper level; it does not independently prove that every selected
  passage is sufficient for generation.

## Source reports

- [Full retrieval tables](retrieval-summary.md)
- [Grounded-answer component and causal tables](grounded-answer-summary.md)
- [Evaluation architecture and reproduction commands](README.md)
- [Machine-readable retrieval summary](retrieval-summary.json)
- [Machine-readable grounded-answer summary](grounded-answer-summary.json)
- [Manual read-only query verification](manual-query-verification.json)
- [Entity-graph architecture decision](../../.specs/adr/0020-derived-entity-section-graph-semantic-okf-retrieval.md)
- [Adaptive evaluation with the full thirteen-route and five-method answer tables](../semantic-okf-adaptive/EVALUATION-CONCLUSIONS.md)
