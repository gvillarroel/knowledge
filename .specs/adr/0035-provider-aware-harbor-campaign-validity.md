---
adr: "0035"
title: "ADR 0035: Require Provider-Aware Validity Before Harbor Strategy Ranking"
summary: "Separate structural completion from evaluable responses, preserve semantic rubrics, and interleave live strategy trials with quota aborts."
status: "Accepted"
date: "2026-07-17"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic OKF Evaluation"
tags:
  - semantic-okf
  - harbor
  - evaluation
  - provider-failure
  - semantic-review
  - reproducibility
---

# ADR 0035: Require Provider-Aware Validity Before Harbor Strategy Ranking

## Status

Accepted.

This decision qualifies ADR 0034 and follows ADR 0033's requirement to exclude quota- and infrastructure-dominated cells from semantic claims. It does not replace the dual-mode dataset or authority boundaries.

## Context

The first eight-family GraphRAG papers consultation campaign persisted all 320 expected Harbor result directories and 24 run receipts. The original summarizer therefore marked it complete and ordered families by mean reward.

A terminal-trace audit showed that artifact presence was not evaluation completion. Of 320 trials, 254 ended with provider `usage_limit_reached`, 14 with a context limit, 4 with an output limit, 16 while agent tool work was interrupted, and only 32 with a complete final response. All 80 hard trials ended at the quota boundary. Whole family/cohort jobs were launched in family blocks, so quota timing also determined which strategies received real model calls.

The audit found two independent grader-contract defects. Evidence objects were rejected when their exact declared members appeared in a different order even though neither the prompt nor JSON Schema imposed that order. The Harbor adapter also discarded the original q001–q030 `min_papers` thresholds and hidden `required_points`. Finally, hard metrics named claim or negative completeness measured only global exact evidence-anchor presence; they never tested candidate statement entailment.

Treating provider absence as zero semantic reward, calling it a verifier error, or publishing a winner from the surviving calls would confound strategy quality with execution order and external quota.

## Decision

Adopt provider-aware, layered campaign validity and explicit mechanical-versus-semantic scoring.

### Terminal outcome authority

- Classify the terminal Pi assistant event as a complete response, provider quota/rate/context failure, output limit, agent interruption, missing response, or other provider failure.
- A recovered retry is classified from its final successful event, not from an earlier transient error.
- Persist only stable outcome and error codes. A `usage_limit_reached` outcome may additionally retain an allowlisted `provider_reset` object containing only a canonical UTC `at` instant and non-negative `remaining_seconds`, when the provider error body supplies them. Do not derive reset metadata from headers or serialize raw provider messages, headers, credentials, answer text, or unrelated provider fields.
- A complete but contract-invalid final response is an evaluable strategy outcome. A provider or infrastructure failure is not a semantic zero and is not a verifier failure.
- Reserve `verifier-error` for corrupted hidden inputs or internal scoring faults after the verifier begins its own authoritative work.

### Campaign validity layers

- `structurally_complete` means the exact expected result/identity artifacts exist without duplicates or drift.
- `provider_clean` means no terminal provider failure occurred.
- `evaluator_clean` means no true internal evaluator failure occurred after a complete response.
- `cohort_observable` means every family/cohort has at least one complete scorer-observable response.
- `evaluation_complete` requires structural completion, provider cleanliness, evaluator cleanliness, and cohort observability.
- `ranking_eligible` additionally requires one evaluable final response for every declared family/question cell. The current forty-question, eight-family comparison therefore requires 40 evaluable responses per family.
- Strict aggregation rejects a non-rankable campaign. A separate forensic mode may emit a prominently invalid report but must suppress family ordering and winner fields.

### Mechanical and semantic evaluation

- Preserve the exact declared evidence member set but do not impose undeclared JSON object-member ordering.
- Pin the authored paper rubric separately from qrels. State `min_papers` publicly as a source-generic minimum relevant-document count; keep `required_points` verifier-only.
- Split the former quality gate into `evidence_contract_gate`, `minimum_document_gate`, and `mechanical_qualification_gate`.
- Rename hard deterministic metrics to `authoritative_evidence_anchor_coverage`, `answer_claim_anchor_coverage`, and `important_negative_anchor_coverage`.
- Do not use lexical keyword matching as a semantic substitute. Evaluate required points and hard claims, derivations, acceptable variants, and negatives through a blinded reviewer or a documented manual adjudication bound to the exact answers and rubric.

### Fair live execution

- Use a checked schedule containing every question/family pair exactly once.
- Before the first model call, persist an immutable campaign input-binding manifest that binds the schedule digest, corrected generated-task manifest and complete generated-task tree, family bundle and ledger, consultation skill tree, grader tree, family registry, model, Pi version, thinking level, runtime build receipt, and runtime image ID. Reverify the affected family bindings before each submitted wave, verify the live Docker tag against the recorded image ID, and abort before another model call on drift.
- Compute every evaluation tree digest by sorting normalized relative POSIX paths in case-sensitive UTF-8 byte order; never use platform-native `Path` ordering, whose case semantics differ between Windows and Linux.
- Process one question across all eight families before advancing, rotate family positions each question, and cap concurrent one-task shards at four.
- Count the first scheduled live cell as the synchronous quota preflight; never duplicate it as a later evaluation attempt.
- Stop submitting new shards after the first terminal quota, rate, or general provider failure. Allow only already in-flight shards to finish and persist an aborted checkpoint.
- Keep schedules, outcome summaries, and checkpoints append-only. A run receipt records timestamps, Harbor exit status, redacted terminal outcome counts, and provider-failure state; receipt existence alone is not success.
- A scheduled campaign auditor must verify its schedule, input binding, one-task shard paths, per-shard receipts, terminal outcome files, and completed checkpoint as one chain. A complete assistant trace is evaluable only when the current scorer emitted its complete finite metric vector and a recognized scored status.

### Historical corrections

- Preserve raw Harbor outputs and the original report hashes.
- Append a superseding audit checkpoint and publish corrected forensic and manual-review artifacts under new names.
- Current-facing documentation must link to the correction and must not present the invalidated historical ordering as a winner.

## Alternatives considered

- **Keep provider failures as zero reward.** Rejected because it measures quota timing and launch order instead of the strategy response.
- **Retry only failed cells in place.** Rejected because it changes attempt opportunity and can become best-of-attempt selection. A replacement campaign is append-only and prospectively scheduled.
- **Require only one observable response per cohort for ranking.** Rejected. Cohort observability is useful for diagnosing an incomplete run, but an answer-quality ranking needs the full fixed matrix.
- **Score semantic rubrics with keywords.** Rejected because wording-independent synthesis, negation, and trade-offs require entailment judgment rather than token presence.
- **Rewrite the historical final report.** Rejected because the original flawed artifact and its hashes are part of the audit trail. A new report supersedes its interpretation.

## Consequences

Positive:

- quota, context, timeout, contract, retrieval, and semantic failures remain distinguishable;
- rankings cannot be published from unequal or provider-biased response samples;
- the original paper breadth requirement and semantic rubric remain reproducibly bound to Harbor tasks;
- exact evidence checks retain deterministic authority without overclaiming semantic entailment;
- balanced one-task scheduling limits wasted quota and makes aborted campaigns diagnosable; and
- evaluator corrections remain append-only and auditable.

Negative:

- a campaign with 319 valid answers and one provider failure cannot produce the intended full-matrix ranking;
- one-task shards and continuous outcome inspection create more result directories and orchestration overhead;
- semantic review remains a separate cost after mechanical scoring; and
- historical summaries require explicit compatibility mapping when metric names change.
