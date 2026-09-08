# ADR 0128: Run full Enterprise retrieval and preserve the public answer contract

## Status

Accepted for one fixed full-corpus measurement on 2026-09-08.

## Context

ADR 0127 measured the incoming and G2 generators on 40 exposed EnterpriseRAG
questions and a reference-enriched 985-document corpus. Exact retrieval parity
does not establish a position in the public answer-quality leaderboard. The
user subsequently authorized an unconditional push to main and requested
Classical over the entire dataset for a public-table comparison.

The public contract uses 500 questions and 511,962 physical source documents.
Its primary Overall metric averages per-question correctness multiplied by
completeness. The official evaluator also performs document-set correction,
gold-answer/fact updates when required, citation stripping, individual fact
checks, and a holistic correctness check. nDCG is a separate retrieval metric.

## Decision

Freeze Classical's BM25 route with the same tokenizer, unigram/bigram settings,
field weights, k1 and b used by the preceding comparison. Preserve all physical
documents and the complete body selected through an explicit native field map.
Do not train, tune, select, or mutate a skill from the full public workload.

Use a bounded-memory execution adapter for this BM25 measurement. The adapter
calls the unchanged Classical source normalizer and passage tokenizer, persists
all document postings independently of questions, and computes document
frequency and field-length averages over the entire corpus. It uses vectorized
arithmetic only to find a conservative candidate set, then calls the unchanged
native scalar BM25 scorer and native tie ordering. Require exact score/ranking
parity against the validated reduced snapshot and independent synthetic edge
cases before any full-corpus query is evaluated.

This adapter does not construct or certify a complete Semantic OKF/RDF bundle.
It is an execution path for the shipped Classical BM25 algorithm. Both canonical
Classical packages are byte-identical to the G2 generator's embedded packages.
Do not describe this experiment as an autonomous agent choosing among skills,
a full G2 package build, an evolution stage, or a new independent promotion gate.

Keep all four upstream ID collisions. Give colliding physical records internal
path-bound suffixes while retaining their original public IDs. Fail public
answer-stage preparation if a needed citation has an ambiguous original ID;
never silently discard a source or choose an answer-favorable collision policy.

Execute all 500 retrieval queries once against the frozen complete index. Report
retrieval means on the 470 questions that declare reference documents. Retain
the 30 high-level or information-not-found questions in the 500-answer workload;
their lack of qrels is not a retrieval failure or a reason to omit them from
answer scoring.

Use the pinned upstream BM25 baseline answer prompt with ten retrieved documents
and GPT-5.4 at medium reasoning. Fetch original source JSON by the upstream UUID
index for exact upstream context formatting and document review. Generate
answers without gold-answer access, freeze the complete submission, and only
then invoke the unchanged official evaluator with its correction flow enabled.
This direct upstream invocation owns the public metric; do not relabel it as a
native Harbor job. Preserve the general execution/error/provenance boundaries
from the Harbor reporting skills.

Select one available provider explicitly before sealing the answer phase.
Support the official OpenAI Responses route and an explicitly disclosed
OpenRouter route pinned to OpenAI's GPT-5.4 with provider fallback disabled.
The existing GitHub Copilot account also passed an explicit GPT-5.4 medium
availability check and was selected before answer-stage sealing. Use a copied,
digest-locked Pi/Node runtime, capture the actual provider response model and
usage, and disclose token-rate cost estimates separately from Copilot billing.
Never substitute a different model to obtain a leaderboard-looking score.
Preserve the upstream's bounded parser retries, use zero HTTP retries, halt
new calls on unavailable or truncated model output, and suppress answer-quality
ranking if the complete workload is not evaluable. Model credentials and raw
results remain local and ignored.

## Publication boundary

The previous work was pushed to main as `d52f3c8` after the coverage and data
hygiene gates passed. The full-corpus measurement receives separate reviewed
aggregate reports. A local public-table comparison is not a submitted or
maintainer-verified leaderboard entry. Publish a relative position only after
all 500 answers and official judgments are complete with no hidden model errors.
Preserve unavailable answer metrics as unavailable, never as zero or a rank
derived from retrieval metrics.

See the [full-corpus execution guide](../../docs/enterprise-classical-full-corpus.md).

## Citation-binding amendment before any answer

The completed retrieval pass found one public-ID collision among the returned
documents. Both physical versions occurred in one question's Top-10, and the
first version is the one selected by the pinned upstream UUID index. No answer
or judgment had been generated when this data-binding issue was diagnosed.

Use the official UUID namespace as an explicit answer-submission projection:
for every first-occurrence retrieved ID across all 500 questions, require its
physical path and complete body to match the pinned original JSON through the
unchanged upstream export functions. Deduplicate later occurrences of the same
public ID without refilling or reordering. Fail if the first occurrence is not
the official source; do not substitute a different body. This verifies 4,999
unique citations and removes one later physical alias from the answer context.

Keep the original index, physical rankings, retrieval metrics and question-only
input immutable. Bind the new public-citation input and the complete verification
receipt separately before sealing inference. This is an identity-serialization
amendment, not a skill mutation, retrieval rerun or answer-quality selection.
The public report must disclose the one affected question and nine unique
documents in its answer context. The initial collision guard remains visible
in the preserved retrieval summary.

## Explicit internal Luna treatment

The user subsequently requested Luna to obtain internal numbers. Preserve the
GPT-5.4 run and its frozen files. Copilot stopped that run with HTTP 429 quota
errors before all answers completed; do not score the partial workload or
convert infrastructure failures to incorrect answers. A neutral Luna probe
also encountered the Copilot quota. Luna then passed a neutral probe through
the existing Codex connection.

Create a separate, predeclared internal arm using `gpt-5.6-luna` for both answer
generation and judging, at medium reasoning, over the same 500 question-only
inputs and exact source documents. Reuse the immutable retrieval artifacts by
digest; never rerun retrieval or reuse GPT-5.4 answers. Keep separate auth
refresh files, call receipts, answer submissions, judgments and a $75 token-rate
equivalent execution ceiling. This is an internal model treatment, not skill
evolution or a public leaderboard submission.

The copied Codex runtime uses its subscription Responses protocol. Disclose its
default system instruction (`You are a helpful assistant.`), low text verbosity,
and lack of an API output-token cap. The host accepts at most 8,192 output
tokens and conservatively reserves the model's 128,000-token maximum for cost
accounting. Preserve all upstream user prompts, citation and correction rules.
Require exact agreement between completed SSE output items and SDK-decoded text;
bind the actual provider model and usage from the final event. Some Codex final
events have an empty output array despite complete output-item events.

Report Luna scores separately with both answer-model and judge-model identities.
A Luna judge prevents a direct public-table rank or a like-for-like comparison
against GPT-5.4-judged results. The shared retrieval metrics remain identical.
Model availability probes contain no benchmark questions or evaluator data.

## First-evaluable judge recovery

The Luna answer phase completed all 500 questions. During judging, one bridge
process exited unsuccessfully after emitting a complete provider response. Its
preserved receipt proves HTTP 200, one request, the exact model and medium
reasoning, literal input identity, completed output, and the bridge's prior
agreement check between SSE messages and SDK text. The host incorrectly treated
the later process exit as a missing model response and halted subsequent calls.
The upstream scorer then filled unavailable cases with fallback values. That
interrupted aggregate is invalid and must never be published as an answer score.

Preserve the original run unchanged. Repair only the interpretation of the
already completed response, with no new request for it. Require an offline
replay of all original response occurrences against literal prompt hashes,
restoring the recorded candidate-document permutations before prompt formatting.
Keep repeated identical requests as separate ordered occurrences. Reject
ambiguous cross-question ownership when recorded replies differ.

The offline replay consumed all 1,449 recorded responses without network calls
and recovered 233 complete question evaluations: 232 match the original records
exactly; one now includes the valid reply lost by the exit-status bug. Retain
these results. Complete the remaining 267 questions using their already recorded
component replies first and issue only missing requests. Restore old document
orders; use the bound 20260908 seed for unissued orders. Record question scope
through nested fact workers and suppress any unresolved helper or transport
failure. The continuation keeps the original model, prompts, sources, answers,
reasoning, concurrency and total token-rate-equivalent budget.

The recovery runner delegates citation stripping, document correction and answer
scoring in the exact order of upstream `evaluate_single_question`. It combines
the first evaluable question records with the unchanged upstream aggregation
functions. Freeze its code, parent binding, original call receipts and offline
audit before new requests. Publish the recovery lineage and the one recovered
process failure alongside the final internal score; do not describe this as an
uninterrupted run or overwrite its original artifacts.

## Durable reply capture and second continuation

The first continuation completed 206 additional question records before a
second local bridge failure. The failed attempt has no decodable provider
response or usage receipt; its outer JSON decoder failed, rather than an
upstream semantic parser rejecting a model answer. Preserve it as an
unevaluable local attempt with unknown usage. It is eligible for one new
first-evaluable request because there is no available reply to resample.

Combine the original 1,449 replies and 2,185 completed continuation replies in
an isolated occurrence cache. Bind each normalized record to its original
path, receipt digest and content. Keep the one missing attempt separately. A
second offline replay consumed all 3,634 available replies and exactly matched
all 439 retained question results. Freeze this audit and the new runner before
completing the remaining 61 questions.

Persist each completed, stream-verified provider response atomically before
stdout delivery or process shutdown. Preserve raw stdout, stderr and exit code
inside the ignored call directory; validate a durable reply against the exact
request before consuming it. No model, answer, prompt, retrieval, semantic
parser or scoring change is part of this transport repair.

Reserve $0.2317224 from the existing $75 budget for the historical attempt with
unknown usage, using the bound UTF-8 input ceiling, full output maximum and
long-context token rates. Publish known usage separately from this uncertainty
interval. Sum all executed original, offline replay and continuation phases
for time accounting, disclose both local interruptions, and retain every
original artifact unchanged.

## Preserve the upstream completed-empty judge response contract

The second continuation retained three additional component replies and failed
on the same literal citation-stripping request. Its captured process error
identified the bridge's nonempty-text check. The upstream citation-stripping
helper accepts an empty completed response and falls back to the unchanged
original answer; imposing the answer generator's nonempty rule in the judge
transport is an incompatible host restriction.

Save completed responses, including empty text, after exact SDK/stream
agreement. Let only judge transports deliver completed empty text to the
unchanged upstream helper or parser. Generated answers still require nonempty
output. Keep truncated output, model mismatch and inconsistent stream content
unavailable. Preserve diagnostic provider data before rejecting a stream
mismatch so a future audit does not lose it.

The third offline audit preserved all 3,637 available replies and exactly
matched the same 439 complete question results. Freeze that evidence and the
completed-empty handling amendment before the final continuation. Its first
captured response for the missing request confirms completed empty text with
exact SDK/stream agreement. The two earlier attempts lack retained replies
and usage; do not infer their content or count their cost as zero. Keep their
combined $0.4634448 conservative reserve within the original $75 budget.

This restores an existing upstream fallback and changes no benchmark answer,
prompt, semantic scoring rule or available model verdict. Disclose all three
local interruptions, all offline replays and the final first-evaluable chain.
