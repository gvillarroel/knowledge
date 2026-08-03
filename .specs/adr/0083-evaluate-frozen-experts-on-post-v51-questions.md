# ADR 0083: Evaluate frozen GraphRAG experts on post-v51 questions

## Status

Accepted on 2026-07-30.

## Context

ADR 0077 packaged v51 from all forty exposed GraphRAG questions and qrels. Its
perfect MRR and nDCG therefore measure fixed-workload fit, not unseen-query
generalization. ADR 0078 transferred the same profiling technique to a new QEC
domain, but again exposed every evaluation question during profile
construction.

The repository needs a direct test in which questions are authored only after
the expert candidates are frozen. The test must preserve one corpus, paper
identity, candidate budget, and metric contract so differences are attributable
to retrieval behavior rather than dataset drift.

## Decision

Create an organizer-managed append-only study for twenty post-v51 GraphRAG
questions.

- Freeze seven existing expert packages before holdout release: v39, v43, v44,
  v45, v46, v48, and v51.
- Author questions from the same fifteen-paper corpus only after those
  candidates exist.
- Bind every expected answer to the repository's previously reviewed claim
  ledger and exact PDF pages.
- Keep questions, answers, tasks, raw rankings, and reports private under the
  study's deny-by-default allowlist.
- Evaluate every candidate at Top 10 using canonical versioned paper identity,
  Recall@10, MRR@10, nDCG@10, exact-evidence validation, and three independent
  process repetitions. Report ranking stability instead of assuming it.
- Publish only a reviewed aggregate metric table.

No candidate may be rebuilt, reprofiled, tuned, or selected using the new
questions. The study evaluates frozen artifacts only.

## Consequences

- The result estimates same-corpus unseen-query retrieval generalization.
- It does not estimate unseen-corpus transfer or generated-answer correctness.
- Expected answers have strong source provenance but no new independent human
  adjudication, so semantic claims must retain that limitation.
- Any later mutation based on these questions converts them permanently into
  development evidence; a further promotion attempt requires another untouched
  cohort.
