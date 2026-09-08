# Classical with Luna: internal full-corpus answer evaluation

**Complete: 500/500 answers and 500/500 first-evaluable judgments, with no unresolved execution or evaluator failures.** The internal Overall score is **48.33/100**. The GPT-5.4 arm remains incomplete after Copilot quota errors.

[Full-corpus report](README.md) · [CTA](cta.md) · [Execution guide](../../../docs/enterprise-classical-full-corpus.md)

The answer generator and judge both use `gpt-5.6-luna` at medium reasoning,
through the existing Codex connection. Retrieval is exactly the same immutable
Classical BM25 pass over 511,962 physical documents and all 500 public queries.
There is no new retrieval pass, skill mutation or reuse of GPT-5.4 answers.

The evaluation uses the pinned upstream answer prompt and source formatter,
then the upstream citation stripping, document correction, fact checks and
holistic correctness flow. Overall is the mean of each question's binary
correctness multiplied by its completeness percentage. A Luna judge makes this
an internal score; it is not eligible for a public-table rank or a controlled
comparison against GPT-5.4-judged submissions.

The Codex subscription protocol supplies its default system instruction,
`You are a helpful assistant.`, with low text verbosity. It does not support an
API output-token cap. The host accepts up to 8,192 output tokens and reserves
cost at the model's 128,000-token maximum. The execution ceiling is $75 in
frozen-runtime token-rate equivalents, separate from actual subscription billing.

The runtime, source manifest, question-only inputs and evaluator code are
digest-bound before inference. Every retained completion records the actual
provider model and usage; two historical attempts have unavailable usage, as
disclosed below. Completed SSE output items must match SDK-decoded text exactly. All
raw questions, source bodies, answers, judgments, request traces and credentials
remain local and ignored. The publication contains only reviewed aggregates.

## Internal answer quality

| Pos. | Pair / strategy | Overall | Correctness | Completeness | Corrected document recall | Invalid extra documents |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Classical / Luna / Luna judge | 48.33% | 70.20% | 52.75% | 68.11% | 8.89 |

Position 1 enumerates this single internal treatment; it is not a public rank.

The official correction flow updated 9 questions. Answer quality averages all 500 questions. Document recall and invalid-extra-document means exclude questions without expected documents after correction. Invalid extra documents is a mean count, not a percentage. This single treatment does not identify a best model or skill.

The [category breakdown](categories.md) shows the strongest answer scores on
information-not-found questions (100.00), constrained questions (79.73), and
intra-document reasoning (67.29). The weakest are completeness (20.13), semantic
questions (25.20), and project-related questions (32.96). Semantic retrieval
also has the lowest nDCG@10, at 22.38, with Recall@10 of 36.80. These descriptive
observations do not establish a causal diagnosis or an independent promotion.

[Aggregate evidence](luna.aggregate.json) · [Frozen binding](luna.binding.json) · [Numeric table contract](luna.comparison.json)

## Recovery lineage

A local process exited unsuccessfully after returning a complete verified model reply. The interrupted aggregate was rejected. Offline replay consumed all 1,449 original response occurrences, restored their document permutations, and recovered 233 complete evaluations without model calls. Of those, 232 exactly match the original question results and one incorporates the valid reply lost by the host. The first continuation added 206 complete questions before a second local failure. A third interruption exposed a host restriction that rejected completed empty citation-stripping text; the official helper already supports that outcome through its original-answer fallback. The final transport delivers completed empty judge replies to that unchanged helper. Its offline audit retained 439 exactly matching question results and all 3,637 available component replies before completing the remaining 61 questions. No available answer or judgment was resampled. All 500 generated answers remain unchanged. Two historical attempts lack retained responses and usage; they remain explicit unknowns, with a combined conservative cost ceiling of $0.4634448. The aggregate companion binds every interrupted history, replay and continuation.

Repository verification: **1,440 tests passed**, **90.7% application coverage** (80% minimum gate). The model workload is separate from these software tests.
