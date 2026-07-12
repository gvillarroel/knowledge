# Evolved Consult Skill: Luna-Only Retest

## Outcome

The evolved `consult-semantic-okf` skill passed 23 of 30 GraphRAG cross-paper questions (76.7%) in the primary skill-only run. The frozen prior skill passed 10 of 30 (33.3%). This is a gain of 13 fully valid answers, +43.4 percentage points, and 2.3 times as many strict passes.

- Model: `openai-codex/gpt-5.6-luna`
- Profiles executed: `consult-skill` only
- Control rerun: no
- Cross-model fallback: none
- Primary evaluation ID: `eval-eah-2026-07-12T20:53:32`
- Primary result: `results/graphrag-cross-paper-30-consult-skill-retest/2026-07-12T20-53-27-743Z-compare/`
- Primary wall-clock evaluation duration: 1,144,208 ms
- Primary status: 23 passed, 5 assertion failures, and 2 technical timeouts

Among the 28 cells that returned a model answer, 23 passed all six assertions (82.1%). The two timed-out cells were rerun separately with a 360-second wrapper limit and both passed, but those supplemental results are not merged into the primary 23/30 score.

## Why the prior skill failed

The discovery split contained two independent failure families:

1. Relevance-qualified breadth: ten responses either directly or latently counted topic-adjacent papers toward a relevance-backed source minimum. This caused semantic structure, page citation, and cross-paper evidence to fail together.
2. Mechanical assembly: responses emitted trailing JSON, unsorted evidence, reconstructed hashes, or source paths in place of published ledger `concept_path` values.

The prose workflow already warned about both problems, but the model had to assemble paper IDs, citations, pages, controlled dimensions, and exact paths manually. The improvement therefore moved those operations into executable read-only gates.

## Skill changes

- `prepare_cross_source_evidence.py` validates the snapshot, ranks reviewed claims locally, keeps five question-matched reserve sources, selects a compact page-grounded evidence set, and emits a canonical response seed.
- `validate_cross_source_answer.py` rejects duplicate or trailing JSON, wrong keys and ordering, word-bound violations, insufficient paper/citation/evidence counts, uncontrolled dimensions, unbacked pages, ownership mismatches, and unknown paths. It emits a safely normalized repair candidate without inventing semantic evidence.
- `_cross_source.py` provides the shared immutable paper/claim catalog, deterministic tokenization and ranking, exact paper ownership, and response-seed construction.
- `SKILL.md` now requires preparation, semantic review, preflight, repair, and a final passing preflight before answering.
- The skill-only benchmark contains one Luna variant and one consultation profile. The no-skill control was not rerun.

The q029 full-run answer used exactly the planner's paper IDs, citation objects, and evidence paths, confirming that the executable seed was used rather than merely described.

## Metric comparison

| Metric | Prior skill | Evolved skill | Delta |
| --- | ---: | ---: | ---: |
| Strict all-six pass | 10/30 (33.3%) | 23/30 (76.7%) | +43.4 pp |
| Response format | 29/30 (96.7%) | 28/30 (93.3%) | -3.4 pp |
| Response contract | 28/30 (93.3%) | 27/30 (90.0%) | -3.3 pp |
| Evidence-path validity | 24/30 (80.0%) | 27/30 (90.0%) | +10.0 pp |
| Semantic structure | 15/30 (50.0%) | 25/30 (83.3%) | +33.3 pp |
| Page-citation grounding | 15/30 (50.0%) | 24/30 (80.0%) | +30.0 pp |
| Cross-paper evidence | 14/30 (46.7%) | 25/30 (83.3%) | +36.6 pp |

The lower raw format and contract rates are entirely affected by the two technical timeouts. Conditional on receiving an answer, response format was 28/28, response contract 27/28, evidence-path validity 27/28, semantic structure 25/28, page grounding 24/28, and cross-paper evidence 25/28.

The paired question transition was 14 gains, one loss, nine passes in both runs, and six failures in both runs. An exact two-sided McNemar test on the 15 discordant pairs gives `p = 0.0009765625`. This supports a real paired-run improvement, while still leaving ordinary model-run variance as a limitation.

## Holdout gate

The fixed six-question holdout improved from 1/6 under the prior skill to 2/6 under the evolved skill, with zero technical errors. That met the predeclared non-regression gate and promoted the skill to the 30-question run.

- Holdout evaluation ID: `eval-5G7-2026-07-12T20:45:15`
- Holdout result: `results/graphrag-cross-paper-holdout-6-validation/2026-07-12T20-45-09-733Z-compare/`

## Primary failure audit

| Question | Failure | Verified cause |
| --- | --- | --- |
| q002 | Evidence path | One copied claim path inserted extra hash characters; every other metric passed. |
| q005 | Contract and relevance breadth | The summary had 177 words and selected 3 of 4 required relevance-focus papers. |
| q009 | Technical | The strict Luna wrapper reached 240 seconds and exited 124. |
| q010 | Relevance breadth | Selected 5 of 6 required relevance-focus papers; structure, pages, and evidence failed together. |
| q017 | Technical | The strict Luna wrapper reached 240 seconds and exited 124. |
| q019 | Relevance breadth | Selected 4 of 5 required relevance-focus papers; structure, pages, and evidence failed together. |
| q020 | Citation contract | The answer duplicated one citation object; the other five metrics passed. |

The residual nontechnical failures show that the planner substantially reduced, but did not eliminate, topic-adjacent selection. They also show that a model can still alter a valid seed or fail to rerun the preflight after its final edit.

## Supplemental technical recovery

The two timeout cells were rerun in a separate, explicitly non-mergeable evaluation with `PI_MODEL_TIMEOUT_SECONDS=360`. Both passed all six assertions.

- Recovery evaluation ID: `eval-JIj-2026-07-12T21:20:22`
- Recovery result: `results/graphrag-cross-paper-technical-recovery-2/2026-07-12T21-20-18-430Z-compare/`
- Result: 2/2, zero failures, zero errors

This establishes that the two primary errors were timing failures, not demonstrated knowledge or skill failures. It does not change the declared primary score.

## Validation

- Skill quick validation: pass
- Focused consultation and benchmark tests: 19 passed before the live run
- Full repository suite: 746 passed
- Coverage gate: 90.9%, above the required 80%
- Holdout, skill-only, and recovery configs: valid
- Dry runs: no unsupported cells
- Active routes: GPT-5.6 Luna only, no 5.3 model, no fallback

## Next improvement target

The next iteration should make final emission atomic: a successful preflight should offer an answer-only `--emit` mode, and the skill should require returning those exact bytes without manual post-validation edits. The planner should also expose clause-level coverage, not only question-token and controlled-dimension relevance, to distinguish the remaining topic-adjacent papers. That iteration requires a new unseen holdout before another promotion claim.
