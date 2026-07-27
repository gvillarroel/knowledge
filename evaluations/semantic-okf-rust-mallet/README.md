# Semantic OKF RustMallet Evaluation

This evaluation compares an isolated RustMallet topic-model candidate with the frozen classical Semantic OKF retrieval baseline over the same 40-question GraphRAG corpus. It does not add a ninth family to the canonical dual-mode Harbor registry.

## Candidate

The standalone pair is:

- `skills/build-semantic-okf-rust-mallet`
- `skills/consult-semantic-okf-rust-mallet`

The pair preserves the classical projection's exact passages, BM25 statistics, PPMI associations, evidence locators, filters, fusion, and diversity reranking. It replaces deterministic weighted-label-propagation topic communities with fixed-seed sparse-Gibbs LDA from [`pyrmallet==0.1.1`](https://github.com/mimno/RustMallet).

The closed plan pins the topic count, iterations, burn-in, optimization interval, posterior sample schedule, alpha sum, beta, random seed, vocabulary thresholds, and top-term count. The builder invokes RustMallet's native Python extension with the explicit `[a-z0-9]+` token regex so the topic vocabulary remains a subset of the auditable Semantic OKF lexicon.

## Build and validate

Install the package-local requirements, then create two absent output paths:

```powershell
python skills/build-semantic-okf-rust-mallet/scripts/build_semantic_okf_rust_mallet.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-rust-mallet/rust-mallet-plan.json `
  tmp/rust-mallet-graphrag-a --output-format json

python skills/build-semantic-okf-rust-mallet/scripts/validate_semantic_okf_rust_mallet.py `
  tmp/rust-mallet-graphrag-a --output-format json

python skills/consult-semantic-okf-rust-mallet/scripts/query_semantic_okf_rust_mallet.py `
  tmp/rust-mallet-graphrag-a inspect --deep-validation
```

Repeat the build at a second absent path and require identical sorted path-and-byte inventories.

## Retrieval runs

`scripts/compare_retrieval.py` retains the evidence-valid classical evaluator contract and replaces only its four classical routes with `rust_mallet_bm25`, `rust_mallet_topic`, `rust_mallet_association`, and `rust_mallet_fusion`. Run it at both `--top-k 10` and `--top-k 100`. Store the full per-question JSON below an append-only ignored `results/runs/<run-id>/` directory.

Generate the checked compact report with:

```powershell
python evaluations/semantic-okf-rust-mallet/scripts/summarize_retrieval.py `
  --top10 evaluations/semantic-okf-rust-mallet/results/runs/<top10-run>/comparison.json `
  --pool100 evaluations/semantic-okf-rust-mallet/results/runs/<pool100-run>/comparison.json `
  --classical-summary evaluations/semantic-okf-classical/retrieval-summary.json `
  --build-a tmp/rust-mallet-graphrag-a `
  --build-b tmp/rust-mallet-graphrag-b `
  --output-json evaluations/semantic-okf-rust-mallet/retrieval-summary.json `
  --output-markdown evaluations/semantic-okf-rust-mallet/retrieval-summary.md
```

The summarizer rejects input drift, authoritative-core drift, route errors, invalid evidence, shared-baseline metric drift, missing cohorts, and non-identical builds.

## Result

The candidate passed two-build byte determinism across 890 files, authoritative-core parity, zero-error execution, and 100% exact evidence validity. It did not improve retrieval quality. At top 10, RustMallet fusion reduced all-40 paper recall by 3.18 percentage points and hard-10 recall by 9.50 points relative to classical fusion. Increasing the returned pool to 100 did not change those deltas.

Keep the RustMallet pair as an experimental alternative and retain deterministic classical topic communities as the default for this benchmark. See `retrieval-summary.json` and `retrieval-summary.md` for the compact evidence.

## Reference-dictionary evolution

The evolved consultation experiment adds `classical/references.json` to a
processed snapshot. Each compact `ref-` ID resolves to the exact seven-field
evidence identity already bound to one RustMallet document. The selected
consultant uses a bounded search/show/finalize protocol and returns IDs only;
deterministic verifier code resolves them before legacy evidence scoring.

Use `scripts/add_reference_dictionary.py` to atomically upgrade an existing
validated RustMallet snapshot. Use `scripts/compare_reference_retrieval.py` to
verify full retrieval parity between the original and upgraded snapshots.

Harbor retained the reference-aware consultant but rejected native integration
into the evolved builder after a small, error-free holdout regression. The
candidate remains under `evolution-assets/builder/` and is not promoted into the
live builder skill. See `reference-evolution-summary.json`,
`reference-evolution-summary.md`, and ADR 0045 for the exact gates and digests.

A later one-command builder candidate integrated the same dictionary natively
and reduced mean build-consult trial time from 262.25 to 244.97 seconds. Its
untouched q015/q025 holdout gained 0.04328 overall but regressed q015 by
0.00332. The frozen no-regressions rule therefore retained the live builder.
The exact per-cell rewards, timings, candidate digest, and deterministic build
digest are appended to the same reference-evolution summaries and recorded in
ADR 0056.

## Canonical direct-retrieval reporting

The reference-aware candidate was rerun over all 40 canonical questions at
Top 10 and pool 100 with independent deep validation and measured query
latency. Use `scripts/evaluate_canonical_retrieval.py` for an append-only
candidate run that reuses the canonical qrels, evidence validator, and timing
contract without loading unrelated frozen family runtimes.

The four candidate routes now appear as explicitly experimental rows in the
general direct-retrieval table. This reporting change does not register a ninth
Harbor family. See `canonical-retrieval-summary.json`,
`canonical-retrieval-summary.md`, and ADR 0047.

## Preserving-prepare trace distillation

A later schema-2 trace-distillation generation isolated a narrower consult
candidate that combines compact search guidance and selected authoritative text
without removing the successful breadth buffer or legacy commands. Local
qualification and a fresh two-task Harbor development gate passed. The
untouched q005/q020 holdout was then opened with two attempts per task, but it
was not evaluable for promotion: q005 failed the required mechanical gate on
both sides, and one candidate q020 trial exited 137. The live consultant remains
the reference-aware parent selected by the earlier complete campaign.

See `preserving-prepare-trace-distillation-summary.json`,
`preserving-prepare-trace-distillation-summary.md`, and ADR 0056 for the
candidate digest, per-trial timing, exact gates, and retained-baseline decision.
