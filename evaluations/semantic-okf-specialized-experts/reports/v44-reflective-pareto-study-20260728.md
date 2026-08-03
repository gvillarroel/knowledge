# V44 Reflective Pareto Specialized Expert Study

Date: 2026-07-28

## Evaluation boundary

This study evolves `graphrag-trace-expert-v43` with native Harbor 0.18.0 jobs
and reflective Pareto search. The search cohort is q031-q040 from
`graphrag-papers-40`. V43 had already been confirmed on those questions, and
the six registered Harbor holdout questions had also been exposed in preceding
studies. The complete study is therefore retrospective. Its result can compare
retrieval variants and justify a new candidate, but it cannot establish formal
holdout promotion.

Every Harbor job installs exactly one complete expert bundle. Pi 0.73.1 with
`openrouter/openai/gpt-5.4-mini` reads the installed skill and executes one
fixed query-helper command. The verifier scores the raw
`/logs/agent/retrieval.json` artifact against immutable qrels and requires:

- an exact manifest and knowledge binding;
- an exact concept-path and ledger-record binding for every retained hit;
- one authoritative paper identity per returned result;
- zero query or verifier errors; and
- finite Recall@10, MRR@10, and nDCG@10 values.

The Harbor development job signature is
`sha256:600e27bebd591396dbd16dff8a2effa568b699d70179ebd13b3edfa1eeb396a2`.
The development profile digest is
`sha256:dddf81e430ed7c1801e1eeced7d6ae6daa9d731ec3f26ba8fed839446a4decf5`.
The schema-1.1 task payload inventory is
`b1570e4f350e4799e09ceccdfdc1e720169356404f548c1188292de4a82cdef1`.

## Diagnostic protocol corrections

Two append-only attempts are preserved but excluded from selection.
`ep-v43-g0-01` used a verifier that confused hyphenated and dotted arXiv
identities and emitted false zero rewards. `ep-v43-g0-02` corrected identity
handling, but the task still asked the model to reproduce the query result; one
retyped concept path caused a false evidence failure even though the retrieval
metrics were valid.

Schema 1.1 removes that transcription boundary. The fixed command writes the
helper's output directly to the agent log, and the grader reads that immutable
artifact. The accepted append-only run is `ep-v43-g0-03`. These are evaluation
protocol corrections, not candidate retries, and no diagnostic result
contributes to the Pareto archive.

## Pareto generations

Generation zero establishes the frozen v43 baseline. Generation one evaluates
a facet-balanced mutation and a hybrid that joins v43's trace-derived
paper/claims BM25 rank with the snapshot's passage-BM25, PPMI-association, and
MALLET-topic rank. Generation two tests a conservative agreement gate against
the generation-one winner.

| Generation | Candidate | q031-q040 nDCG@10 | Qualified | Archive outcome |
|---:|---|---:|---|---|
| 0 | Frozen v43 baseline | 70.40% | Yes | Baseline |
| 1 | Facet-balanced | 69.06% | Yes | Complementary, lower aggregate |
| 1 | Classical hybrid | 80.79% | Yes | Best aggregate |
| 2 | Incumbent classical hybrid | 80.79% | Yes | Best aggregate |
| 2 | Agreement-gated hybrid | 80.68% | Yes | No-regression alternative |

The generation seals form one continuous chain:

1. `sha256:ddcb30bdf909e767b83fc1c016343b4491262c9f5999450d5de5609fe01607bf`
2. `sha256:ad29e70c871499c37ba33dd3f6633bcceabaebba2ad80f9e4c198818c2a64197`
3. `sha256:c9fd58880710ce29b2fdfa81375084252be793228b21558b6d9830fa4101d7d6`

Every accepted candidate completed all ten trials, passed every required
reward gate, and had zero errors. No generation opened Harbor holdout. The
agreement-gated branch ties v43 on five cases and improves five, while the
selected hybrid has the highest aggregate and two small case-level decreases.
Keeping both in the final archive preserves that trade-off instead of hiding it
behind one mean.

## Selected v44 candidate

The selected helper uses RRF constant 60, trace weight 1.0, and classical weight
2.0. The complete question and exact hyphen expansion remain the trace anchor.
Classical artifacts affect rank only; the authoritative evidence continues to
come exclusively from the immutable semantic ledger and concept files.

| Version | Recall@10 | MRR@10 | nDCG@10 |
|---|---:|---:|---:|
| V43, q031-q040 | 85.50% | 67.26% | 70.40% |
| V44, q031-q040 | 95.50% | 83.33% | 80.79% |
| Change | +10.00 pp | +16.07 pp | +10.39 pp |

The winning Harbor bundle digest is
`sha256:0190b3e4f81cd1efe4847624b1bc4c32342d4ff357c5dcdd209bd67b65479dd9`.
V44 copies its query helper byte-for-byte while changing the package name and
guidance:

- retrieval contract: `trace-classical-hybrid-rrf-v3`;
- query helper:
  `25adc3196b0bc21769f3115a4c5889a5369f5ae211418ddbfdece5e447e44ead`;
- expert tree:
  `72c65803130629dd81bfbccf3a423c419975454f3b0b0ecfdb6624fffb494e74`;
- expert manifest:
  `b3a4e3f25c64c5da05de48ef54d1baaf793a4cdee58e327903dc0804a6c42ad9`;
- guidance:
  `c41e168c2f600e791b5bcdb34f71a73dfca932b487ed04caa1df85647bdf8315`;
  and
- 108-file knowledge tree:
  `e787e3ef4a2c2a3a624be0803a3536ab24c2dcdd66e4b894c2d0ec10634f1d9e`.

The package validator, skill validator, manifest verification, representative
query, and byte-identical packaging check all pass.

## All-40 evaluation and rank

The frozen v44 package was evaluated independently at Top 10 and pool 100. The
Top-10 ranking is an exact prefix of the larger run for every question; all 400
Top-10 evidence rows validate, the query error count is zero, and both runs
have identical expert, knowledge, builder, packager, question, and Pareto-archive
bindings.

| Version | Recall@10 | MRR@10 | nDCG@10 | P95 | Position |
|---|---:|---:|---:|---:|---:|
| V43 trace BM25 | 82.88% | 87.65% | 81.76% | 229.86 ms | 10 of 24 |
| V44 trace/classical hybrid | 84.97% | 92.08% | 83.47% | 568.22 ms | 3 of 24 |
| Change | +2.09 pp | +4.43 pp | +1.70 pp | +338.36 ms | +7 places |

The checked
[retrieval audit](pareto-improved-retrieval-20260728.md) replaces v43 rather
than counting two versions of the same expert. V44 ranks below the `quality`
and `fast` ensembles and above adaptive fusion. This is a deterministic
retrieval rank, not a grounded answer-quality rank.

## Repository verification

- The canonical dataset registry and all eight build/consult strategy pairs
  pass validation.
- The packager, expert retrieval, Harbor task generator, and grader suite passes
  12 focused tests.
- The schema-1.1 Harbor task tree passes deterministic regeneration.
- The metric-only report validator accepts all 24 rows and three metrics.
- The comparison-contract validator accepts all 24 alternatives and three
  aggregate dataset metrics.
- The complete repository suite has 2,107 passing and 16 skipped tests. Its only
  three failures are pre-existing standalone-boundary checks in three untouched
  skills.
- The required application coverage gate passes 758 tests with 90.9% total
  coverage against the 80.0% threshold.
