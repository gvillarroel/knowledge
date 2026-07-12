# Semantic OKF Reader Benchmark — Final Report

Date: 2026-07-12

## Outcome

The benchmark completed all 600 canonical comparison cells with no unresolved execution errors. The final treatment policy answered 296 of 300 questions correctly with valid evidence and response structure. The isolated control passed 1 of 300.

| Profile or route | Overall pass | Semantic accuracy | Evidence grounding | Technical errors |
|---|---:|---:|---:|---:|
| `no-skill` control | 1/300 (0.3%) | 2/300 (0.7%) | 299/300 (99.7%) | 0 |
| `skill`, before semantic retry | 279/300 (93.0%) | 285/300 (95.0%) | 294/300 (98.0%) | 0 |
| Luna semantic retry subset | 17/21 (81.0%) | 19/21 (90.5%) | 19/21 (90.5%) | 0 |
| Final treatment policy | 296/300 (98.7%) | 298/300 (99.3%) | 298/300 (99.3%) | 0 |

All 300 final treatment responses passed JSON format, exact response-contract, and evidence-path-validity checks. “Overall pass” requires every metric to pass.

The final treatment policy is not a symmetric single-pass comparison: it retains the technically recovered treatment result, then applies the declared result-derived Luna retry to its 21 failed cells. The control remains the canonical one-attempt access baseline. The pre-retry row is therefore the appropriate direct control comparison; the final row measures the complete treatment routing policy.

## Coverage

The fixed battery contains 300 semantically distinct questions and expands to 600 initial cells across two isolated profiles. The question bank contains stable semantic descriptors and signatures rather than counting paraphrases as new cases.

| Category | Questions | Final treatment pass | Semantic | Grounding |
|---|---:|---:|---:|---:|
| Typed fact | 40 | 40 | 40 | 40 |
| Relation traversal | 40 | 40 | 40 | 40 |
| Multi-hop join | 50 | 50 | 50 | 50 |
| Typed filter | 40 | 40 | 40 | 40 |
| Aggregation | 45 | 45 | 45 | 45 |
| Provenance and lineage | 40 | 40 | 40 | 40 |
| Ontology and SHACL | 20 | 16 | 18 | 18 |
| Integrity and negative checks | 15 | 15 | 15 | 15 |
| Bundle inventory | 10 | 10 | 10 | 10 |

All 80 easy and 120 medium questions passed. The four remaining failures are within the 100 hard questions, giving 96/100 hard overall passes.

The pinned knowledge snapshot contains 60 records from 40 sources. Its normalized tree SHA-256 is `d1071f6f53b8df9bef5e1ea37b69b9efdb3ed8d5fe5ec4d9496ad7e28259fe43`. The evaluated `build-semantic-okf` skill snapshot is independently pinned at `5ac02f9dfbd228ec960f7d4444c1ec88b69b40b416a30d5bec32588267a941dd` so later skill improvements do not rewrite the experiment.

## Model routing and recovery

The initial route used PI with `openai-codex/gpt-5.3-codex-spark` as primary and `openai-codex/gpt-5.6-luna` only after a non-zero exit or timeout.

| Stage | Cells | Complete | Execution errors | Selected into canonical matrix |
|---|---:|---:|---:|---:|
| Initial comparison | 600 | 128 | 472 | 128 |
| Luna technical resume | 472 | 467 | 5 | 467 |
| Luna technical retry | 5 | 5 | 0 | 5 |
| Luna semantic retry | 21 | 21 | 0 | 21 treatment replacements |

Within the initial comparison, Spark returned 62 cells directly. Its 538 process failures activated the runtime Luna route; Luna recovered 66 and the shared Codex usage limit left 472 incomplete. Technical recovery therefore used the explicit `openrouter/openai/gpt-5.6-luna` PI route with a host-environment key reference. The wrapper detects an identical primary/fallback model and performs one attempt, not a duplicate fallback.

The canonical technical matrix selects 128 initial rows, 467 full-resume rows, and 5 retry rows by `(promptId, profileId)`. It restores global prompt indices, validates every source result against its exact manifest and prompt text, rejects partial merges, and records input hashes and the complete attempt chain. Its result contains exactly 600 unique cells and zero technical errors.

The main pipeline processed 1,098 Skill Arena cells: 600 initial, 477 technical-repair, and 21 semantic-retry cells. Runtime fallback adds model processes inside initial cells and is reported separately. Smoke, authentication preflight, and an excluded unauthenticated diagnostic run are not included in the scores above.

## Semantic retry

The result-derived semantic retry selected only complete, unsuccessful `skill` cells. It did not retry control or passing treatment cells. Ten selected typed-fact rows were historical scorer false negatives: their answers used `+00:00`, while the earlier assertion expected `.000Z`; both denote the same instant. The current scorer canonicalizes ISO timestamps to UTC milliseconds, and all ten passed the retry.

Luna recovered 17 of 21 selected cells. Four ontology/SHACL questions remain:

| Prompt | Failed metric | Observed issue |
|---|---|---|
| `q270-ontology-shacl` | Semantic accuracy | Returned absolute ontology and XSD IRIs where the requested schema required compact names. |
| `q272-ontology-shacl` | Evidence grounding | Correct answer, but cited `semantic-plan.json` instead of authoritative `shapes.ttl`. |
| `q273-ontology-shacl` | Evidence grounding | Correct answer, but cited `semantic-plan.json` instead of authoritative `shapes.ttl`. |
| `q275-ontology-shacl` | Semantic accuracy | Returned a nested RDF-style target object instead of the requested scalar target summary. |

## Skill improvement after the fixed evaluation

The production `build-semantic-okf` skill was revised after preserving the evaluated snapshot:

- the query helper can select `shapes.ttl` and `validation-report.ttl` explicitly through `--graph shapes` and `--graph validation`;
- the query guide distinguishes discovery artifacts from authoritative evidence;
- structured answers must verify exact keys, scalar/array/object shape, typed values, and the requested full-IRI versus compact-name representation;
- generated SHACL constraints must be cited from `shapes.ttl`, even when `semantic-plan.json` helped discover the rule.

Three context-clean forward checks exercised a different SHACL rule, the validation report, and `SemanticMappingShape`. All three selected the authoritative artifact and returned the requested compact structure. These checks validate the general guidance but do not alter the fixed benchmark score.

## Interpretation

The experiment shows a large effect for the complete augmented access path: a reader skill plus a pinned knowledge snapshot, compared with neither. It does not isolate the causal contribution of the skill instructions from snapshot access. A future three-arm study should add `knowledge-only` while retaining the same model route, snapshot, and assertions.

The control’s high evidence-grounding score is expected: a compliant `null` answer with empty evidence satisfies abstention discipline while failing semantic accuracy. Semantic accuracy and overall pass are the meaningful access comparisons.

## Reproducibility artifacts

- `evaluation.yaml`: fixed 300-question, two-profile comparison.
- `questions.jsonl`: hidden answers, evidence sets, semantic descriptors, and signatures.
- `coverage.json`: category, difficulty, snapshot, and evaluated-skill hashes.
- `scripts/merge_technical_results.py`: exact-manifest-bound technical recovery merge.
- `scripts/build_luna_fallback.py`: complete-failure-only semantic retry selection.
- `scripts/merge_semantic_results.py`: exact fallback overlay and final audit.
- `luna_fallback_report.md`: live 21-cell semantic retry report.

The final composite contains 600 unique rows, 297 total overall passes, 303 assertion failures, and 0 execution errors. Its SHA-256 is `6d1118d862c9df8f6143ba08114c880f44e6e8e007ba2a83649e1482bdf46fa8`.

## Validation gates

- Repository suite: 714 passed, 6 skipped.
- Application coverage: 90.9% against the required 80% minimum.
- Skill Arena suite: 339 passed.
- Benchmark drift check: 300 questions current.
- Project OKF projection and validation: current and valid.
- `build-semantic-okf` skill validation: passed.
