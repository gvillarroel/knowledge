# ADR 0072: Use trace-derived fielded BM25 for the specialized expert

## Status

Accepted on 2026-07-28 for deterministic direct retrieval. Grounded answer
quality remains experimental.

## Context

ADR 0071 packaged two trace-derived GraphRAG experts over the qualified v46
Tika/MALLET knowledge snapshot. Their stable raw-occurrence helper reached
72.20% Recall@10 and 66.57% nDCG@10, placing the shared row 19 of 24. The v39
and v42 guidance did not participate in that deterministic score.

Harbor 0.18.0 trace analysis had independently diagnosed a retrieval failure:
generic facet paraphrases discarded distinctive terms from the full question.
The accepted v39 proposal prescribed a full-question anchor, a small number of
exact facets, and bounded fusion. The v42 proposal added evidence-union and
response-integrity constraints. Neither historical consultation candidate
passed its all-cases development gate, so those traces can motivate a new
retrieval candidate but cannot establish grounded-answer promotion.

The canonical six-question holdout had already been partially visible during
the preceding study. It therefore could not honestly serve as an untouched
promotion gate for this iteration.

## Decision

Revalidate the v39 and v42 trace studies with the trace-distillation skill's
`--dry-run`, `--doctor`, and `--analyze-only` modes. These operations use locked
discovery artifacts, execute no model, and do not open deferred Harbor holdout.

Select one deterministic retrieval mutation using only the 24-question
discovery cohort:

- preserve every full-question token as the anchor;
- retain each exact hyphenated token and add its component terms;
- score the research-paper and reviewed-claims channels independently with
  BM25, then fuse their scores;
- use `k1 = 5.0`, `b = 0.75`, paper weight `1.0`, and claims weight `0.5`; and
- return the highest-contribution exact record for each authoritative paper
  identity before applying the result budget.

Package the frozen adapter as `graphrag-trace-expert-v43`. Extend
`build-specialized-skill` with an optional `--query-template` input while
preserving its default helper. Bind the copied helper in the existing expert
manifest and require the same template for deterministic `--check`.

The frozen expert tree digest is
`2532924b2c254fc17d1c6f6049d227568887b05e7403db6d800837e39f2546df`.
Its embedded knowledge remains the 108-file v46 tree
`e787e3ef4a2c2a3a624be0803a3536ab24c2dcdd66e4b894c2d0ec10634f1d9e`.

After freezing, use q031-q040 as an independent confirmation cohort. Report the
six canonical holdout questions separately with an explicit prior-exposure
label, but do not use them to select or tune the candidate. Finally evaluate all
40 questions at Top 10 and pool 100, require an exact Top-10 prefix, zero query
errors, byte-identical artifacts, and 100% evidence validity.

Replace the predecessor row in the same 24-alternative comparison rather than
counting two versions of one expert. The v43 result is 82.88% Recall@10, 87.65%
MRR@10, 81.76% nDCG@10, and 229.86 ms selected P95. It is position 10 of 24.

## Consequences

- The specialized expert gains 10.68 percentage points of Recall@10 and 15.19
  points of nDCG@10, moving from position 19 to position 10.
- The untouched q031-q040 confirmation reaches 85.50% Recall@10 and 70.40%
  nDCG@10, supporting generalization beyond the development cohort.
- The custom helper remains local, read-only, standard-library-only, manifest
  bound, and reproducible; ordinary generated experts retain the prior default
  helper.
- The six-question canonical holdout result is useful descriptive evidence but
  not an untouched promotion claim.
- This decision promotes only deterministic direct retrieval. A balanced,
  leakage-controlled Harbor campaign is still required before assigning a
  grounded answer-quality rank.
