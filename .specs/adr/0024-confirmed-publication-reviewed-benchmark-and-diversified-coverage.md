---
adr: "0024"
title: "ADR 0024: Bind Definitive Answers to Confirmed Publication and Reviewed Evidence Coverage"
summary: "Publish the exact confirmed answer-candidate bytes at the host boundary, evaluate answer evidence against an append-only reviewed benchmark, and diversify semantic claims by independently retrieved papers."
status: "Accepted"
date: "2026-07-15"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - answer-publication
  - frozen-benchmark
  - evidence-coverage
  - diversified-retrieval
  - quality-gates
  - skill-arena
---

# ADR 0024: Bind Definitive Answers to Confirmed Publication and Reviewed Evidence Coverage

## Status

Accepted.

ADR 0025 supersedes only this record's v1.3.1 long-candidate confirmation handshake.
The reviewed-benchmark, paper-diversification, host-publication, and non-compensating
quality-gate decisions remain accepted.

This decision extends ADR 0015, ADR 0022, and ADR 0023. It preserves the
definitive ensemble's direct paper-ranking policy and accepted final-03 bundle.
It supersedes ADR 0023 only where that record describes answer-output publication,
the hard-question expected-ID set, and the pre-diversification coverage result.

## Context

The definitive ensemble passed deterministic build, direct retrieval, evidence
identity, and MCP answer-construction checks, but interrupted live comparisons
exposed publication boundaries that server-side construction alone did not close.

In the first diagnostic, all 15 treatment rows called the then-current single-tool
finalizer prototype, but only 5 visible answers were byte-identical to its output.
Ten answers changed at least one character, including an authoritative source path.
In a later three-row q031 diagnostic, a superseded two-mode prototype produced valid
prepared candidates and confirmation receipts, but the ordinary host command still
published a free-form agent message. None of the three host outputs matched the
already confirmed bytes, and six contract-sensitive evidence fields changed. These
were transport and publication failures, not answer-quality measurements. Neither
prototype is the accepted split-tool interface.

A later frozen full-run attempt, `2026-07-15T13-50-35-550Z-compare`
(`eval-d9Z-2026-07-15T13:50:43`), exercised MCP v1.3.1 after the host wrapper existed.
The first treatment prepared successfully but failed to copy the complete candidate
into confirmation and did not recover. The runner stopped at that first treatment
protocol failure. This rejected attempt showed that the v1.3.1 long-copy handshake
remained an unreliable model-mediated transport step and contributes no benchmark row
or answer-quality metric.

The expected-ID audit also established a subtler evaluation issue. Every parent
expected ID was real, correctly bound, and semantically sensible, but an exact-ID
metric can under-credit an answer when another reviewed record independently
supports the same complete atomic claim or important negative. Correcting that
measurement issue must not rewrite the frozen parent benchmark, weaken an atomic
claim into partial fragments, or leak answers into questions.

Finally, the first evaluation against the reviewed alternatives covered 43 of 44
atomic answer groups. The missing q033 group had a reviewed claim in a paper already
selected by the independent adaptive route, but a global semantic ranking spent its
bounded per-facet positions on more similar claims. Increasing the global budget
would weaken the cost contract. A query-derived diversity rule can reserve evidence
depth inside independently relevant papers without using question IDs or expected
answers.

## Decision

### Historical v1.3.1 publication handshake, superseded by ADR 0025

The intermediate decision used MCP runtime version 1.3.1 and three distinct
enforcement layers for the definitive treatment:

1. `semantic_okf_prepare_answer` validates the draft, recomputes the current unpaged
   coverage pack, constructs the canonical contracted JSON, and stores its exact
   UTF-8 bytes and SHA-256 for the active session. Its closed schema has no `mode`.
   It may run again only before confirmation when the candidate itself needs repair.
2. `semantic_okf_confirm_answer` accepts only the exact prepared text in its required
   `candidate_json` field, compares bytes, rejects duplicate JSON members and
   non-standard numbers, consumes the candidate, and returns a closed receipt
   containing the confirmed hash and byte count. Confirmation is non-idempotent,
   must succeed exactly once, and must be the terminal tool call. A failed prepare or
   failed confirm publishes nothing and abandons the active transaction; another
   confirm is eligible only after a fresh successful prepare, and no candidate from
   the abandoned transaction remains eligible.
3. The host publication wrapper validates a final clean transaction suffix of one or
   more successful prepares followed by exactly one successful terminal confirm,
   plus the receipt, candidate hash, and byte count. It then atomically replaces the
   single absolute output-last-message file with the confirmed candidate bytes. An
   earlier successful confirm, confirm without a fresh prepare after any failed
   protocol call, `candidate_json` changed from the last prepare, repeated confirm,
   trailing tool call, or other treatment protocol failure exits nonzero instead of
   publishing the agent's free-form final message. Control profiles continue to
   publish their ordinary raw messages.

Server confirmation is therefore necessary but not sufficient. The treatment output
remains the host-published byte sequence, and an independent runtime attestation must
bind it to the final confirmed candidate. ADR 0025 retains those boundaries while
replacing the model's long-candidate copy with a prepared envelope and short digest.
A new answer comparison may be accepted only when every treatment trace passes the
active ADR 0025 publication contract.

### Version reviewed expected-ID alternatives as a benchmark superset

Keep `semantic-okf-adaptive-frozen-40-plus-hard10-v1` unchanged and create the
standalone answer benchmark
`semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1`.

The reviewed benchmark preserves, byte for byte, all 40 retrieval questions and all
10 hard questions. It also preserves every parent statement, required paper and
source identity, derivation, acceptable textual variant, important negative, qrel,
and authoritative evidence object. A closed amendments file may append a reviewed
claim ID to an existing OR option only when that one claim independently supports
the complete atomic group. Partial conjuncts cannot be combined as though they were
independent OR alternatives.

The review retained the parent's 72 expected-ID links and added 22 atomic and 19
important-negative links. The resulting benchmark has 113 links, 68 unique reviewed
claim IDs, and 71 authoritative evidence objects across the unchanged 44 atomic
groups and 13 important-negative groups. Thirty-eight close but partial or otherwise
insufficient alternatives were explicitly rejected. Every new evidence object is
rederived from the pinned reviewed-claim JSONL line and exact Markdown PDF-page
segment, including Unicode offsets, locators, and SHA-256 values.

This is an append-only measurement correction, not a change to the questions or
their semantic answers. The parent remains a historical regression target. Future
corrections require another benchmark ID, another closed amendments document, and a
new frozen manifest rather than an in-place edit.

### Diversify semantic claims inside independently selected papers

Retain `bounded-reviewed-claim-multisignal-expansion-v2` and all existing per-facet
and total caps, but apply
`adaptive-paper-conditioned-claim-diversification-v1` inside each semantic-claim
candidate list:

1. retrieve a pool up to ten times the bounded per-facet maximum through the exact
   pinned hybrid embedding route, filtered to reviewed claim sources;
2. retain the first six claims in global semantic order;
3. identify the first three distinct paper IDs from the adaptive primary ranking;
4. retain up to six semantically ranked claims from each of those papers; and
5. fill any remaining positions from the original global semantic order.

Deduplication and the existing maximum of 20 semantic claims per facet and 240
semantic claims overall still apply. The preferred papers come only from the query's
adaptive result. The reranker receives no question ID, qrel, expected claim, or
ground-truth label. It cannot introduce a paper, change direct paper ranking, grant
similarity factual authority, or bypass an exact reviewed answer binding.

On the reviewed hard ten, the pre-diversification candidate covered 43/44 atomic
groups, 13/13 important-negative groups, all required papers, and 713/713 validated
bindings. The diversified candidate covered 44/44 atomic groups, 13/13 negatives,
all required papers, and the same 713/713 validated bindings. Mean semantic
candidates fell from 126.1 to 104.4 and mean union candidates from 166.4 to 162.4.
The semantic route alone covered fewer atomic groups, 39 instead of 42, but its new
composition was more complementary to adaptive and graph candidates, raising union
coverage from 97.5% to 100.0%. This illustrates why ensemble marginal coverage,
not one component's standalone count, is the selection criterion for answer
preparation.

### Apply non-compensating acceptance gates

A definitive answer evaluation must pass all of these gates independently:

- exact bundle, authoritative-core, plan, provider, model revision, and component
  index bindings;
- reviewed-benchmark schema, hash, locator, evidence-text, and append-only invariants;
- no benchmark identifiers, expected claims, or qrels in the skill, runtime plan,
  published bundle, or query request;
- deterministic candidate sets over three repetitions, closed caps, reviewed claims
  only, zero candidate-edge authority, and byte-identical bundle state before and
  after consultation;
- deep inspection, every bounded coverage page with identical parameters, and a
  final clean suffix of one or more no-mode successful prepares returning strict
  `semantic-okf-prepared-answer/1.0` envelopes followed by exactly one
  non-idempotent terminal confirm containing only the final envelope's unchanged
  `response_sha256`;
- zero publication from a failed prepare or failed confirm, recovery only through a
  fresh successful prepare and digest, no earlier successful confirm, no stale or
  mismatched digest, and no tool call after successful confirm;
- exact envelope keys, canonical `candidate_json`, SHA-256, UTF-8 byte count, receipt
  binding, and host-published candidate bytes;
- exact host publication for every treatment row;
- a fresh and complete 90-answer Cartesian product from the isolated three-profile
  Skill Arena configuration, with no mixed, resumed-from-diagnostic, or filled rows;
- independent mechanical evidence validation and profile-blinded semantic review;
  and
- separate reporting of retrieval, candidate coverage, correctness, completeness,
  grounding, response-contract compliance, latency, determinism, and causal
  contrasts.

No ranking, coverage, or semantic score can compensate for invalid evidence,
publication drift, benchmark leakage, an incomplete run, or authoritative-core
mutation.

### Keep experiments append-only and distinguish diagnostics from evidence

Large bundles, raw model runs, traces, review batches, and intermediate preparations
remain ignored and append-only. Compact closed reports, benchmark manifests,
amendments, configuration manifests, hashes, and English explanations are checked
in.

Interrupted copy-integrity and host-publication runs remain rejected diagnostics.
They explain the adopted gates but contribute no row to an accepted answer metric.
Every material runtime or publication change requires a fresh run; results are never
spliced across configurations. An all-skills portfolio remains a routing smoke, not
causal evidence. The accepted three-arm comparison estimates the full treatment
capability—consult skill plus gated MCP workflow and host publication wrapper—not
the isolated effect of skill prose.

## Evidence boundary

The accepted direct retrieval result remains 83.8162% Recall@10, 100.0% MRR@10,
85.2001% nDCG@10, and 100.0% evidence validity over all 40 questions. The accepted
diversified coverage result establishes candidate availability and exact evidence
identity only. Neither result establishes generated-answer correctness,
completeness, grounding, or response-contract compliance.

The compact evidence bindings are:

- reviewed benchmark manifest
  `evaluations/semantic-okf-ensemble/reviewed-benchmark/frozen-answer-benchmark.json`,
  SHA-256 `257997cc2da3d9afae596ac8b46551a1b1fa73480f15861a25f262bb85a91f62`;
- reviewed hard ground truth, SHA-256
  `c656fc575b0c7e06cd386093d975cd74ef9c9aead743312e3aadec1cbdc08451`;
- accepted diversified coverage JSON and Markdown, SHA-256
  `f96ab9356a99ca5b3798e4de6912e0a6b5fc010c3abb5711360b85257374deec`
  and `25720899f87efedf4f9c901d91df19dbe97d2ffba53fec7c61e8dff0576ad0a1`;
- retained pre-diversification coverage JSON and Markdown, SHA-256
  `b477a5a51f7ccaef9695d496c57f79ae8c515b365745f26ded987c12b2637c60`
  and `fdf3f6a96b242dec2b1534746648589597871de65afcadd736628e44352b1e96`;
- rejected finalizer-copy diagnostic JSON and Markdown, SHA-256
  `0ce8e9df47ed3f226acbaa254143f528473331cfc9ce78222a96d4c0f41026f3`
  and `748ad1131265c642b7e35803d5ec53ac6ffec869e25daaef33b63cff9f3e555d`;
  and
- rejected host-publication diagnostic JSON and Markdown, SHA-256
  `950d295ff35a7b132fd94a970ae2c8977e274a9da1004b8f329a3bdde4feb21c`
  and `b2a780f94b557249b28a27de7a0768769188d5de8b90ce79a272149bc85f6dca`.

The rejected v1.3.1 `eval-d9Z` attempt contributes no row or metric. Final
answer-output metrics remain pending until a fresh v1.4.0 90-answer run, publication
attestation, independent preparation, blinded review, aggregation, and repository
validation all pass. This ADR intentionally records no metric from a partial or
diagnostic run.

## Consequences

Positive:

- a valid prepared-and-confirmed candidate can no longer be corrupted by an agent's
  later reserialization at the host output boundary;
- exact-ID scoring recognizes independently sufficient reviewed alternatives while
  preserving every parent question, semantic requirement, qrel, and evidence option;
- paper-conditioned diversity recovers the last reviewed hard-question answer group
  without increasing published caps or using evaluator labels;
- all evidence remains reviewed, exact-bound, derived, read-only, deterministic, and
  independently validated; and
- rejected experiments remain useful architectural evidence without contaminating
  the accepted comparison.

Negative:

- treatment publication requires a stateful MCP session, a host wrapper, and trace
  attestation in addition to ordinary Skill Arena execution;
- the reviewed benchmark is a second frozen identity that must be bound explicitly
  in answer reports;
- candidate coverage now reflects a larger variable union and must never be labeled
  Recall@30 or confused with direct retrieval;
- the hard ten have been repeatedly inspected and remain an optimization/regression
  target rather than an untouched holdout; and
- 100% candidate-group coverage still does not guarantee that a model will select,
  interpret, or state every required claim correctly.
