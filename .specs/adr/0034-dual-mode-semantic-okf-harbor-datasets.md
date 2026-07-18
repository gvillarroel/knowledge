---
adr: "0034"
title: "ADR 0034: Register Dual-Mode Semantic OKF Harbor Datasets"
summary: "Evaluate matched build and consultation strategies either end to end from raw inputs or against an exact prebuilt Semantic OKF snapshot."
status: "Accepted"
date: "2026-07-17"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic OKF Evaluation"
tags:
  - semantic-okf
  - harbor
  - datasets
  - evaluation
  - reproducibility
---

# ADR 0034: Register Dual-Mode Semantic OKF Harbor Datasets

## Status

Accepted.

## Context

The repository already contained two substantial Semantic OKF corpora: the forty-question Astro documentation benchmark and the forty-question GraphRAG cross-paper benchmark. The historical Harbor harness exposed a prebuilt Astro bundle to one consultation skill, while paper evaluations lived in separate experiment directories. There was no single checked inventory or reproducible way to distinguish consultation quality from the combined build-and-consult path across all paired strategy families.

Without an explicit mode boundary, a nominal end-to-end test could accidentally receive prebuilt knowledge, a consultation-only test could accidentally install a builder or see raw sources, and generated tasks could be scored against an unbound snapshot. The paper benchmark also needed normalization from reviewed paper identities and evidence spans into the source-generic Harbor grader without weakening its exact-evidence checks.

## Decision

Add `evaluations/semantic-okf-datasets/` as the canonical registry and dual-mode Harbor scaffold while preserving the historical evaluation directories as immutable evidence.

- Register `astro-40` and `graphrag-papers-40` with hash-pinned descriptors and complete named cohorts.
- Register eight matched strategy families: legacy, embeddings, classical, adaptive, entity-graph, ensemble, graphify, and turso.
- Define `build-consult` as a trial with exactly the matched build and consult skills, evaluator-free raw input mounted read-only at `/dataset`, newly built knowledge at `/workspace/knowledge`, and no prebuilt knowledge mount.
- Define `consult-only` as a trial with exactly the matched consult skill, processed knowledge mounted read-only at `/knowledge`, no raw source mount, and no build skill.
- Keep questions, qrels, hard ground truth, authoritative source files, and the fixed scoring ledger inside the separate verifier environment in both modes.
- Require raw staged inputs and processed consultation snapshots to match generated task manifests by SHA-256. A consult-only agent bundle must be identical to the verifier reference.
- Normalize paper evidence to LF UTF-8 because its reviewed character offsets use normalized line endings. Split evidence around discarded C0 extraction controls so every derived span remains exact in both the authoritative paper and normalized record body.
- Validate deterministic task regeneration, prompt leakage, mode boundaries, hidden bindings, and a passing structural oracle for every question before a live job.
- Keep generated inputs, bundles, Harbor tasks, dry runs, credentials, and live results ignored. Record only redacted, append-only run receipts.
- Pin every Python package needed by the eight consultation strategies in the shared Harbor runtime, including `graphifyy==0.9.17`, `llama-index-core==0.14.23`, and `pyturso==0.6.1`; do not substitute a different graph or database engine during comparison.
- Validate completed multi-family reports against the exact eight-family, declared-cohort matrix and the pinned Pi/model identity before aggregating results. Preserve technical failures as zero-reward trials and expose observed denominators for metrics that a failed verifier could not emit.

## Consequences

Positive:

- the papers evaluation is now an explicit dataset rather than an implicit collection of experiment files;
- build-plus-consult and consult-only outcomes have enforceable, inspectable resource boundaries;
- every paired strategy can reuse the same dataset, cohorts, task generator, grader, and runner;
- host-side rebuilding and full oracle validation catch corpus, identity, and evidence drift before model quota is consumed;
- receipts bind comparisons to exact skill and data hashes without exposing credentials.
- campaign summaries reject missing, duplicate, or runtime-drifted trials instead of silently comparing unequal samples.

Negative:

- full validation executes eighty oracle scores when both modes are checked;
- Astro requires a locally generated validated reference bundle because no processed snapshot is checked into the new registry;
- embeddings and ensemble runs still require an externally prepared, verified Hugging Face cache;
- the hidden verifier uses a fixed reference ledger, so end-to-end builders must preserve authoritative core record identities and hashes to receive credit.
