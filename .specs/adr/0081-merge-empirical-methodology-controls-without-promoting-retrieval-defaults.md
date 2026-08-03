---
adr: "0081"
title: "ADR 0081: Merge Empirical Methodology Controls Without Promoting Retrieval Defaults"
summary: "Adopt reproducible cross-domain ablations, input binding, uncertainty reporting, and configurable chunking while explicitly rejecting unsupported repository-wide retrieval defaults."
status: "Accepted"
date: "2026-07-29"
product: "knowledge"
owner: "Platform Architecture"
area: "Knowledge Methodology"
tags: [knowledge, evaluation, retrieval, chunking, uncertainty, reproducibility]
---

# ADR 0081: Merge Empirical Methodology Controls Without Promoting Retrieval Defaults

## Status

Accepted.

## Context

ADR 0080 introduced a paper-grounded methodology corpus, standalone review
skill, and read-only reviewer agent. Its audit proposed eleven improvements,
but paper support alone does not establish that a repository-specific treatment
works.

Offline ablation 01 tested three proposals over the existing GraphRAG and
quantum-error-correction paper workloads. It evaluated 21 chunker-retriever
treatments in each domain, covering 80 exposed questions and 1,680 query
results. The study is retrospective: every qrel was visible before execution,
so its results can guide development but cannot qualify a production default.
Each workload has only 15 papers, and Recall@10 searches two thirds of that
collection. The qrels are document-level, non-exhaustive focus sets.

The first runtime-bearing attempt omitted retrieval time from hybrid latency.
That attempt is invalid and preserved as a superseded receipt. The accepted
report includes BM25, character-TF-IDF, and fusion time for hybrid treatments.

## Decision

Merge the reproducible experiment harness, its frozen evidence, and the
following methodology controls:

- keep fixed chunk size configurable and measure retrieval quality together
  with latency;
- retain fixed-512 BM25 as a simple chunked control without claiming a Recall
  improvement;
- retain fixed-128 character-trigram TF-IDF as a high-quality diagnostic
  candidate;
- retain fixed-512 reciprocal-rank fusion as a cross-domain candidate with an
  explicit Recall caveat;
- select candidates by domain and objective instead of naming one global
  winner;
- require confidence intervals and practical-effect thresholds beside point
  estimates; and
- bind accepted reports to the exact question bytes and complete Markdown
  paper trees used to produce them.

These controls are accepted for evaluation and subsequent qualification, not
as production retrieval defaults.

## Rejected and Inconclusive Treatments

Do not adopt:

- fixed-128 BM25 as a repository-wide default, because it reduced GraphRAG
  Recall@10 by 0.0273 while increasing median latency by 20.7 times;
- whole-document character-TF-IDF as the default, because fixed-128 chunking
  improved Recall@10 by 0.1363 on GraphRAG and 0.1375 on QEC;
- a single global treatment, because the domain point winners differed and 14
  of 21 treatments remained on the measured cross-domain Pareto frontier; or
- uncertainty-free point ranking, because the widest Recall@10 confidence
  interval was 0.1625 while several observed treatment deltas were below 0.04.

Keep hierarchical page scoring and 256-token overlap experimental. Their
effects were mixed, inconclusive, or insufficient to repay their measured
costs consistently across domains and retrievers.

Do not use the invalid attempt's latency or Pareto conclusions.

On QEC, three treatments tie at Recall@10 of 1.0. Fixed-128
character-trigram TF-IDF is only the secondary-metric tie-break winner, not a
unique primary-metric winner.

## Deferred Proposals

The experiment provides no evidence for:

- neural semantic retrieval or late and learned chunking;
- claim-level grounded answer quality;
- automated-judge calibration against blinded human review;
- transfer to genuinely new source bytes and independently authored questions;
- reviewed evidence cards or a future systematic-search delta;
- SHACL mutation detection;
- component-level skill evolution; or
- visually grounded PDF extraction fidelity.

Each item remains open until the staged evidence contract in
`evaluations/knowledge-methodology-proposal-experiments/NEXT-STAGES.md` is
completed. No later stage may reuse opened evidence as a holdout.

## Consequences

Positive:

- working review artifacts and empirical controls become reproducible from
  `main`;
- accepted, rejected, inconclusive, and deferred outcomes have separate
  machine-readable and human-readable records;
- input drift and partial hybrid timing cannot silently preserve an accepted
  result; and
- future retrieval changes have explicit baselines, uncertainty requirements,
  and promotion boundaries.

Negative:

- the accepted candidates add substantial query latency;
- document-level non-exhaustive qrels do not measure claim-bearing chunk
  quality or grounded answer quality;
- the best-treatment comparisons are exploratory and have no multiplicity
  correction;
- the bootstrap intervals represent variation over the exposed questions, not
  repeated stochastic executions, providers, generators, or judges;
- latency is a single-run, machine-specific diagnostic rather than portable
  qualification evidence;
- the QEC input snapshot must remain available to reproduce the second domain;
  and
- no production retrieval default changes as a consequence of this decision.

## Evidence

The durable evidence is:

- `evaluations/knowledge-methodology-proposal-experiments/PREREGISTRATION.md`;
- `evaluations/knowledge-methodology-proposal-experiments/reports/offline-ablation-01.json`;
- `evaluations/knowledge-methodology-proposal-experiments/reports/offline-ablation-01-decision-table.md`;
- `evaluations/knowledge-methodology-proposal-experiments/reports/offline-ablation-01-decisions.json`; and
- `evaluations/knowledge-methodology-proposal-experiments/reports/attempt-00-invalid.md`.

Promotion requires a genuinely untouched qualification cohort plus the
claim-quality and judge-calibration evidence described in the next-stage
record.
