---
adr: "0007"
title: "ADR 0007: Benchmark Semantic OKF Consultation with Isolated PI Profiles"
summary: "Compare a closed-book PI profile with a profile that receives a pinned Semantic OKF snapshot and its reader skill across 300 grounded questions."
status: "Accepted"
date: "2026-07-11"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Evaluation"
tags:
  - knowledge
  - evaluation
  - semantic-okf
  - isolation
  - pi
---

# ADR 0007: Benchmark Semantic OKF Consultation with Isolated PI Profiles

## Status

Accepted

## Context

Semantic OKF bundles expose several consultation layers: a compact ledger, human-readable concepts, an accepted RDF data graph, provenance, ontology, SHACL shapes, and validation evidence. A reader must choose the cheapest authoritative layer, return grounded answers, preserve typed values, and avoid treating validation or shape graphs as domain facts.

Informal demonstrations cannot distinguish model recall from snapshot-grounded consultation. They also make it easy to leak the corpus, gold answers, or skill instructions into a control run. A useful benchmark therefore needs independent executions, identical model conditions, hidden deterministic oracles, broad semantic coverage, and a reproducible knowledge release.

## Decision

Maintain a generated Skill Arena comparison with exactly 300 semantically distinct questions and two isolated PI profiles:

1. `no-skill` receives an empty base workspace, no capability declaration, no knowledge snapshot, and no Semantic OKF reader skill.
2. `skill` receives one profile-only workspace overlay containing both the pinned Semantic OKF snapshot and an independently pinned `build-semantic-okf` snapshot. The benchmark records both tree hashes so production-skill improvements cannot rewrite a completed experiment.

Both profiles use the same PI adapter and model route, prompt, configured read-only sandbox, enabled model network, approval policy, output contract, and deterministic assertions. The runtime route calls `openai-codex/gpt-5.3-codex-spark` first. Because Skill Arena V1 accepts one model and has no native model-fallback field, a profile-visible command wrapper retries with `openai-codex/gpt-5.6-luna` only when the primary PI process exits unsuccessfully. It discards failed primary stdout, retains diagnostic stderr, and marks the model that returned the response. Each attempt has a 90-second hard timeout and kills its complete child process tree; a Spark timeout becomes exit 124 and activates Luna. Semantic assertion failure never triggers this runtime fallback. A Luna-only route does not retry Luna with the same model identifier. PI 0.80.6 or newer is required so both model identifiers are recognized. On Windows, the Skill Arena PowerShell command boundary reads prompt files explicitly as UTF-8 and emits UTF-8 stdout so multilingual titles and values remain byte-correct. Each prompt is a separate Skill Arena cell and model request. Skill Arena may reuse a profile-scoped workspace and home directory across cells, so fixtures remain read-only and questions cannot rely on mutations or session state from earlier cells. Gold answers, evidence locators, query descriptors, and semantic signatures remain outside both profile workspaces.

Technical completion and semantic correctness are recovered separately. A host-side technical builder classifies cells only from nonblank `response.output` and absent `response.error`; it never treats Promptfoo assertion state as a transport error. Technical resume manifests use `openrouter/openai/gpt-5.6-luna` and an explicit `$HOST_ENV:OPENROUTER_API_KEY` reference, so the credential is neither serialized nor inherited wholesale. The canonical merger validates each result against its own exact manifest, joins by `(promptId, profileId)` rather than run-local indices, restores primary identity, recomputes row and provider aggregates, records ordered attempt hashes, and refuses duplicates or an incomplete 600-cell matrix.

Semantic assertion failures use a separate, result-derived stage only after the technical matrix is complete. The host-side builder verifies benchmark ID, every treatment prompt ID and exact prompt text, rejects any incomplete treatment cell, and selects only unsuccessful `skill` cells. It emits a one-profile Luna manifest and a `.selection.json` record. It never retries `no-skill` cells, passing treatment cells, or an unverified results/config combination. The semantic merger replaces every selected row with its bound retry result, including a failed retry, so reporting cannot choose the better attempt after observing both. The control run remains canonical, and runtime fallback, technical recovery, and semantic retry are reported separately. Because result-derived subsets depend on one completed live run, their manifests remain outside deterministic generation and drift checks.

The question allocation spans typed facts, bidirectional relation traversal, multi-hop joins, typed filters, aggregation, cross-graph provenance, ontology and SHACL contracts, integrity and negative checks, and bundle inventory. Expected values are derived from the pinned release artifacts, normalized as JSON, hashed, and verified against existing evidence files. ISO date-time strings with offsets are canonicalized to UTC milliseconds before hashing, so equivalent forms such as `+00:00` and `.000Z` do not create lexical false negatives. Every non-null answer must contain one reviewed sufficient evidence subset. Alternative ledger, RDF, and sufficient Markdown-concept paths are accepted; additional evidence is allowed only when every cited path exists in the pinned snapshot. Prompts still prefer the smallest useful set. Semantic signatures hash only canonical query descriptors containing operations, entities, paths, projections, filters, aggregates, and graph scope. They exclude question text, category, difficulty, and query-layer coverage labels, so paraphrases or relabeling cannot inflate the nominal question count.

Scoring separates semantic accuracy, evidence grounding, evidence-path validity, response format, and response-contract compliance. Evidence normalization accepts paths relative to either the bundle root or the workspace `knowledge/` directory. A `no-skill` run is instructed to return `answer: null` with empty evidence because it lacks the snapshot. That abstention passes the response and evidence-discipline metrics but intentionally fails semantic accuracy against the shared gold answer. The control therefore measures the closed-book access baseline; it is not a separate accuracy target.

Generation and execution remain separate. The generator writes the full manifest, hidden question bank, coverage report, and a five-question smoke manifest. Check mode verifies byte-for-byte drift. Manifest validation and Skill Arena dry-runs are required before live execution. The initial full benchmark expands to 600 Skill Arena cells, while the initial smoke benchmark expands to 10; runtime fallback attempts and result-derived Luna retries add model calls. Neither benchmark runs live merely because fixtures were generated.

This two-arm comparison measures the complete augmented access path: reader procedure plus snapshot. It does not identify the reader skill's causal contribution independently of knowledge availability. A later study may add `knowledge-only` as a third profile while retaining the same snapshot and runtime settings.

PI isolation is an experimental workspace and home-directory boundary, not a hostile-code security sandbox. The fixtures contain trusted repository artifacts and execute with a configured read-only workspace while model network access remains enabled.

## Consequences

Positive:

- the control cannot answer from mounted benchmark knowledge or skill instructions;
- every treatment answer and its selected minimal evidence set can be checked against pinned local artifacts without an LLM judge;
- the benchmark covers several authoritative layers instead of only exact-record lookup;
- stable IDs, signatures, evidence hashes, and generated manifests make regressions reviewable;
- the smoke manifest permits inexpensive end-to-end verification before the 600-cell initial run.
- runtime model errors can recover through Luna without doubling every successful Spark request.
- failed treatment assertions can be retried selectively with an auditable, exact-manifest-bound Luna stage.

Negative:

- the full live comparison starts with 600 PI cells, may add fallback calls, and can take hours at conservative concurrency;
- deterministic exact assertions require normalized JSON answers and do not score stylistic explanation quality;
- the two-arm result conflates the benefit of the reader instructions with access to the snapshot;
- query-layer metadata does not measure runtime efficiency, latency, tokens, or tool calls;
- changing the pinned release intentionally invalidates derived answers, signatures, and snapshot checks until regeneration and review.
- the report's static variant label identifies the Spark-to-Luna route; per-cell execution stderr must be inspected to determine whether fallback occurred.
