# Tantivy Consultation and Builder Evolution

This evaluation first improves `consult-semantic-okf-tantivy`, freezes the
promoted consumer, and then evolves the dedicated
`build-semantic-okf-tantivy` against that exact consumer. Tantivy remains
outside the canonical eight-family Semantic OKF registry.

## Final stopping round

The third prospective round used the previously unused endocrine-hygiene
benchmark. Its concept-type query candidate improved both development and
holdout means, but one holdout cell regressed, so the strict gate retained
consultant digest
`sha256:896d038b16dd974411ef50bf91e5efead5e2589262058114b4bed4d8993f0c84`.

With that consultant frozen, an exact structured-interpretation passage
builder improved both endocrine development and hard holdout. The complete
GraphRAG gate nevertheless rejected it: hard-10 Recall@10 fell from 92.17% to
83.17%, MRR from 90.00% to 88.33%, and nDCG from 80.54% to 77.43%. Builder
digest
`sha256:8a5024734f62d4b53fe55b6b6f569d831513429460c0de8783ae1b47584de40a`
is retained.

This complete query-then-builder round promoted neither skill, satisfying the
declared stopping criterion. The live skills and canonical table remain
unchanged. See
`reports/trace-distillation-round3-endocrine-20260723.{md,json}`.

## Earlier staged decisions

The `identity-natural` consultant won the 24-question development cohort and
the untouched 16-question holdout. Mean native Harbor reward rose from
0.548310 to 0.851161 on development and from 0.558400 to 0.852793 on holdout,
with zero regressed holdout tasks. The checked consultant is therefore
promoted and frozen at realizer tree digest
`sha256:8c3666ede3281b96a8630321d9c2fb91d015da96469003ecf22643e041b6f7e7`.
The complete freeze receipt is `consult-freeze-20260723.json`.

Builder evolution then kept that consultation tree byte-for-byte frozen. Four
sealed builder candidates and the stable dedicated baseline were evaluated
through native Harbor jobs. The best development mutation, `papers-forward-3`,
raised mean reward from 0.851161 to 0.868570. On the disjoint holdout it fell
from 0.852793 to 0.812123 and regressed the single aggregate holdout task. The
promotion gate therefore rejected the mutation. The checked dedicated builder
retains stable Classical-compatible construction semantics plus deterministic
UTF-8 LF serialization. Its frozen corpus output preserves all 884
authoritative core files byte for byte. It regenerates the six `classical/`
projection files: the four data artifacts equal the local Classical campaign
artifacts after newline normalization, while the index and build report bind
the resulting LF hashes. See `builder-freeze-20260723.json`.

The later trace-distillation round used six independent builder-development
tasks and four disjoint holdout tasks. Its `forward-four` candidate retained
all paper and semantic-claim records while replacing single-page paper
passages with exact forward windows of up to four pages. It improved every
development task and raised mean reward from 0.851161 to 0.866492. The sealed
holdout then fell from 0.852793 to 0.831703, with regressions on parts 03 and
04, so the strict gate again retained the stable builder. The paired
IDF-weighted query candidate was also rejected despite a positive holdout mean
gain because part 04 regressed by 0.001614. See the two 2026-07-23 compact
reports under `reports/`.

Population search and reflective Pareto search independently selected the same
earlier development winner. Trace distillation later materialized the
evidence-supported `forward-four` candidate and rejected it on untouched
holdout evidence.
Candidate realization sealed every compared bundle. Operator coevolution and
external-failure resume failed closed at their declared contracts, while GEPA
and metaskill evolution had no causal mutation or producer-ledger surface for
this staged runtime evaluation. No failed, neutral, or holdout-regressive
candidate was promoted.

## Historical trace-distillation experiment

The earlier E-through-S trace-distillation experiment used the validated
GraphRAG papers Classical snapshot. Four development questions (`q001`,
`q013`, `q031`, and `q039`) provided discovery evidence. Two disjoint questions
(`q010` and `q029`) remained hidden for its promotion holdout.

## Prepare

First validate and materialize the canonical classical input, snapshot, and
consult-only tasks as documented in
`evaluations/semantic-okf-datasets/README.md`. Then generate this isolated
experiment:

```bash
python evaluations/semantic-okf-tantivy/scripts/prepare_trace_distillation.py \
  --run-id 20260722-e \
  --auth-directory /tmp/semantic-okf-rust-mallet-auth-20260722
```

The preparer copies only the selected canonical tasks, rewrites the public
consultant identity to Tantivy, removes transient bytecode, pins Pi 0.81.1 and
the model, and emits complete zero-retry Harbor configurations. The small
`pi_luna_agent.py` Harbor adapter installs the Luna-capable
`@earendil-works/pi-coding-agent` distribution because the upstream
`@mariozechner` registry currently stops at 0.73.1. It refuses to replace an
existing output directory. Add the scripts directory to `PYTHONPATH` when
running Harbor or the distillation driver.

## Evaluation contract

- Discovery and candidate development use the same four task checksums and
  one independent attempt per task.
- Proposals require support from at least two unique discovery trials and two
  unique task checksums.
- Candidate development must be fully evaluable, satisfy both required
  mechanical gates, and achieve a 100% pass rate before holdout is opened.
- Baseline and candidate use the same two-task holdout profile with no retries.
- Promotion requires no errors, no task regression, and non-negative mean
  reward gain.
- Raw Harbor jobs and distillation outputs are append-only and remain outside
  the tracked source tree. Compact redacted results belong in `reports/`.

## Historical recorded result

The completed E-through-S evolution is summarized in
`reports/trace-distillation-20260722.md` with exact machine-readable gate
evidence in `reports/trace-distillation-20260722.json`. Final candidate S
passed 4/4 development trials, but neither experimental baseline R nor S
qualified on the disjoint q010/q029 holdout. The gate returned
`keep-baseline` with `promoted: false`; no evolved candidate was copied into
the checked-in skill or canonical family registry.

## Canonical direct-retrieval comparison

The promoted Tantivy consultant and dedicated builder were evaluated
on the same frozen 40-question direct Top-10 paper-identity contract used by
the general retrieval table. The dedicated build preserved the complete
authoritative core and deterministically regenerated its bound projection.
The consultant normalized
syntax-free natural questions against the frozen unigram lexicon without
qrel-aware expansion and used the independent schema 1.2 evidence validator.

The complete Top-10 run, exact replay, and pool-100 sensitivity run covered 120
queries with zero errors and 100% exact evidence validity. Top-10 Tantivy BM25
reached 80.74% all-40 Recall@10, 93.75% MRR@10, and 81.05% nDCG@10. On the
hard-10 cohort it reached 92.17% Recall@10, 90.00% MRR@10, and 80.54% nDCG@10.
All 40 ranked Top-10 results reproduced exactly; 400/400 Top-10 and 527/527
pool-100 evidence rows were valid. The latest P95 query time was 90.92 ms after
a separately measured 1,079.04 ms validation setup. The pair is therefore
reported in the general table as an experimental comparator but is not added
to the canonical Harbor registry.

A second prospective Astro distillation round rejected a query mutation after
its GraphRAG hard-10 regression, then froze the retained query while promoting
a builder that adds one exact pre-heading overview to long non-paper records.
The promoted builder passed 6/6 candidate-development trials and improved the
separate two-task holdout without a regressed cell. Two new canonical 890-file
builds were byte-identical. Their complete Top-10, replay, and pool-100 run
reproduced the same quality metrics, evidence counts, ranked Top-10, and
pool-100 prefix, so the quality columns in the canonical table are unchanged.

See `canonical-retrieval-summary.json` and
`canonical-retrieval-summary.md` for the digest-bound measurements. Use
`scripts/evaluate_canonical_retrieval.py` for append-only raw runs and
`scripts/summarize_canonical_retrieval.py` to gate their deterministic summary.
