# V36 Evaluation Response Audit

Date: 2026-07-24

## Scope

This audit reviews all 18 responses cited by the v36 trace-distillation and
promotion evidence:

- three v28 discovery-baseline responses (`q002`-`q004`);
- three v36 development-candidate responses (`q002`-`q004`);
- six v36 holdout-baseline responses;
- six v36 holdout-candidate responses.

Each response was checked separately against the four hidden semantic
`required_points` in its task, then against its response contract, evidence
validity, first-use ordering, qrel minimum, and recorded reward. `F/P/M` below
means fully addressed, partially addressed, or missing required points. This
is a manual semantic-coverage review, not a replacement reward.

## Overall finding

The final `keep-baseline` decision is correct, but the reported rewards are not
reliable semantic-quality measurements.

The holdout baseline is semantically better on `q005`, `q010`, `q020`, `q025`,
and `q029`; the two `q015` answers are roughly tied. The candidate nevertheless
has a slightly higher recorded mean reward (`0.133380` versus `0.130857`)
because strict mechanical gates collapse structurally invalid or
qrel-incomplete answers to zero. The candidate also emits `answer: null` for
`q020` and corrupts evidence identity fields in `q025` and `q029`, so it must
not be promoted.

The development result is more concerning: all three v36 responses pass the
mechanical gate, but none covers all four semantic required points. The
development gate is therefore a false positive relative to the documented
semantic rubric.

## Individual response reviews

### Discovery baseline v28

1. **q002 — reward `0.000000`; semantic coverage `1F/1P/2M`.**
   The answer gives a good end-to-end pipeline backbone and partially compares
   retrieval units, but it omits the required extraction-method contrast and
   the accuracy/cost/updateability/task-scope trade-off. The release failure is
   mechanically justified: evidence row 7 has the wrong `text_sha256`, and
   only 3 of the 6 required qrel documents are covered. The zero still hides
   useful partial semantic content.

2. **q003 — reward `0.861037`; semantic coverage `1F/2P/1M`.**
   It clearly separates document-derived from graph-native systems and gives a
   useful representation/task comparison. It only partially explains what
   different graph elements preserve and the overlap between task families,
   and it omits extraction errors/cost versus supplied-graph
   coverage/schema constraints. This is a semantic false-positive risk: the
   mechanical pass does not mean the expected answer is complete.

3. **q004 — reward `0.000000`; semantic coverage `3F/0P/1M`.**
   This is one of the strongest answers in the set. It explains the precision,
   fragmentation, multi-hop, pruning, redundancy, token, breadth, and
   detail-loss trade-offs. It only misses hybrid or multi-granular retrieval.
   The response fails because evidence is not in first-use order, even though
   every evidence row is valid and the qrel minimum is met. The release failure
   is structurally correct, but the zero is a severe semantic false negative.

### Development candidate v36

4. **q002 — reward `0.818615`; semantic coverage `0F/2P/2M`.**
   It covers query decomposition, structured retrieval, generation, and
   verification, but only partially covers the complete stage sequence and
   retrieval-unit spectrum. It omits the required extraction-method contrast
   and the cost/updateability/task-scope trade-off. The pass is a semantic false
   positive.

5. **q003 — reward `0.795629`; semantic coverage `1F/2P/1M`.**
   It correctly separates graph origins and partially covers representation
   and task differences. It does not discuss extraction cost/errors versus
   coverage/schema constraints and does not adequately cover fact
   verification or overlap between task families. The pass is a semantic false
   positive.

6. **q004 — reward `0.733706`; semantic coverage `0F/3P/1M`.**
   It enumerates all requested retrieval units, but mostly describes them
   rather than comparing their trade-offs. Search/pruning cost, detail loss,
   and hybrid multi-granular retrieval are absent or weak. It is materially
   less complete than the failed v28 `q004` answer, so this pass exposes a
   format-driven false preference.

### Holdout baseline

7. **q005 — reward `0.000000`; semantic coverage `3F/0P/1M`.**
   It clearly explains hierarchy/community summaries, top-down and bottom-up
   use, global sensemaking, and when communities beat local retrieval. It
   misses abstraction, redundancy, token-cost, and local-detail limitations.
   The response contract, evidence, and reference order all pass; it receives
   zero solely because 3 rather than 4 cited documents are in the hidden qrel
   set, despite citing 6 valid independent documents. This is a likely qrel-gate
   false negative.

8. **q010 — reward `0.785142`; semantic coverage `2F/2P/0M`.**
   It gives the best comparison of community summaries, paths, organized graph
   context, coherence, and coarse-to-fine selection. Source-excerpt fidelity,
   abstraction loss, and token-budget constraints are only partial. The pass
   is directionally reasonable, but it should be labeled semantically partial,
   not complete.

9. **q015 — reward `0.000000`; semantic coverage `2F/2P/0M`.**
   It distinguishes static rebuilds, incremental updates, and query-time
   adaptation well. Deduplication/provenance/community maintenance and the
   full cost/error-accumulation trade-off are partial. The failure is
   mechanically justified by first-use-order invalidity and a 3-of-5 qrel
   shortfall, but the semantic content is roughly as good as the passing
   candidate response.

10. **q020 — reward `0.000000`; semantic coverage `1F/3P/0M`.**
    It directly covers authoritative medical sources, professional
    schemas/rules, enterprise extraction cost, hybrid retrieval, and reusable
    graph patterns. Evaluation/risk controls and transfer mismatch are less
    complete. All structural and evidence checks pass; it receives zero only
    because 3 rather than 5 of its 7 cited documents are qrels. This is the
    clearest holdout qrel-gate false negative.

11. **q025 — reward `0.000000`; semantic coverage `3F/1P/0M`.**
    Semantically, this is the best answer in the holdout: it covers task
    structure, weak baselines, leakage, LLM judging, pipeline failures, and the
    danger of universalizing benchmark wins. It only partially states the need
    for both stage-wise and end-to-end evaluation. The output is nevertheless
    invalid because every `locator` is a string rather than the required
    object, making all ten evidence rows invalid. Zero is correct for the
    deliverable contract but deeply misleading as a semantic score.

12. **q029 — reward `0.000000`; semantic coverage `2F/2P/0M`.**
    It compares static and adaptive retrieval well and balances robustness
    against latency and token cost. Concrete static mechanisms,
    non-determinism, and error propagation are incomplete. It fails first-use
    ordering and covers 5 of the required 6 qrel documents. The structural
    failure is real; the semantic zero is not representative.

### Holdout candidate

13. **q005 — reward `0.000000`; semantic coverage `0F/2P/2M`.**
    It gives a generic graph-versus-local-retrieval comparison but does not
    explain community-summary construction, map-reduce/top-down/bottom-up
    synthesis, or community limitations. The zero is aligned with the expected
    answer.

14. **q010 — reward `0.000000`; semantic coverage `0F/3P/1M`.**
    It partially discusses graph structures, notebooks, coherence, and source
    anchoring, but misses the requested community-report comparison, explicit
    path ordering, and all major context-budget limitations. The zero is
    directionally correct, although the recorded failure comes from qrel
    coverage rather than semantic review.

15. **q015 — reward `0.800281`; semantic coverage `2F/2P/0M`.**
    It is a good partial answer and the only valid candidate holdout pass.
    Deduplication, mutual indexes, community maintenance, and error
    accumulation remain incomplete. Its semantic quality is comparable to the
    failed baseline `q015`, so the reward difference overstates candidate
    improvement.

16. **q020 — reward `0.000000`; semantic coverage `0F/0P/4M`.**
    It returns `answer: null` with no evidence even though the baseline
    demonstrates that the snapshot supports a substantive answer. This is a
    genuine candidate regression and the zero is correct.

17. **q025 — reward `0.000000`; semantic coverage `1F/3P/0M`.**
    The answer contains useful observations about task mix, generalization,
    baselines, human judgment, and pipeline stages, but it is shallow relative
    to the expected synthesis. Four of six evidence rows are invalid because
    `source_path` or `record_id` loses the slash after `tika/extracted`.
    The zero is correct.

18. **q029 — reward `0.000000`; semantic coverage `0F/3P/1M`.**
    It gives a partial static/adaptive comparison but omits most planning
    mechanisms and the latency/token/non-determinism/error-propagation balance.
    Evidence row 5 has a corrupted `concept_path`
    (`74c255b70` instead of `74c2556b70`). The zero is correct and confirms that
    the candidate's identity-preservation mutation is unsafe outside its
    development cases.

## Evaluation defects

1. **The semantic rubric is recorded but never scored.** The grader calculates
   retrieval metrics and then sets `semantic_correctness` to
   `manual-review-required`. The trace-distillation gate nevertheless treats
   `reward >= 0.7` as a pass. This creates the development false positives.

2. **The public document minimum and the implemented gate differ.** The prompt
   asks for a minimum number of independently relevant papers, but the grader
   counts only documents in the hidden qrel set. Valid off-qrel evidence cannot
   satisfy the gate. Baseline `q005` and `q020` are the clearest failures.

3. **A single binary multiplier conflates semantic quality with release
   validity.** Any evidence typo, locator shape error, or first-use-order error
   forces the whole reward to zero. Strict qualification should remain, but
   semantic/retrieval utility must be reported separately.

4. **Qrel overlap does not measure claim entailment or required-point
   coverage.** A response can cite the expected papers while omitting central
   comparisons and limitations, as the three v36 development responses do.

5. **The aggregate mean is unstable and misleading.** The candidate's
   `+0.002523` mean gain is an artifact of which answers survive binary gates,
   not evidence of better answers. Pairwise manual review favors the baseline
   on five holdout tasks and finds no clear candidate advantage on the sixth.

## Recommended improvements

1. Add an explicit semantic-review result for every required point, using
   blinded human review or a calibrated judge with citations and an abstention
   path. Do not promote on mechanical reward alone.
2. Emit at least three independent axes:
   `response_contract_qualified`, `evidence_qualified`, and
   `semantic_rubric_score`. Keep the strict release gate, but never replace the
   other scores with zero.
3. Split the current minimum into:
   `valid_independent_document_count` and `qrel_document_coverage`. Either make
   qrels explicitly exhaustive and re-audit them, or let valid off-qrel
   documents satisfy the public minimum while qrel recall remains a separate
   metric.
4. Treat first-use ordering as a deterministic canonicalization check with a
   precise failure class. The finalizer should reorder evidence and remap
   indices before emission.
5. Add claim-to-passage entailment checks and per-required-point diagnostics;
   document-level qrel membership is too coarse.
6. Base promotion on pairwise task outcomes with a no-regression rule across
   semantic, contract, and evidence axes. Do not use mean reward as the primary
   quality signal when binary gates create many zeros.
7. Add adversarial fixtures for immutable evidence identities, including slash
   preservation and repeated hexadecimal suffixes. Candidate `q025` and `q029`
   show that the current mutation is not safe.

## Decision

Retain the production baseline and keep ADR 0057's no-promotion decision.
Amend future evaluation reports to state that the existing v36 reward is a
mechanical retrieval/contract score, not a semantic correctness score.
