# Consult-Skill Luna Evaluation Status

## Evolved skill-only retest

- Date: 2026-07-12
- Configuration: `skill-only-evaluation.yaml`
- Model route: `openai-codex/gpt-5.6-luna`
- Profiles: `consult-skill` only
- Promptfoo evaluation ID: `eval-eah-2026-07-12T20:53:32`
- Completed cells: 30 of 30
- Passed: 23
- Assertion failures: 5
- Technical timeouts: 2
- Cross-model fallbacks: 0
- Duration: 1,144,208 ms
- Result directory: `results/graphrag-cross-paper-30-consult-skill-retest/2026-07-12T20-53-27-743Z-compare/`
- Detailed report: `consult-luna-skill-only-retest-report.md`

The evolved skill improved the strict score from 10/30 to 23/30. A fixed holdout improved from 1/6 to 2/6 before promotion. The two timed-out primary cells passed in a separately labeled 2/2 technical recovery run and are not merged into the primary score.

## Valid full run

- Date: 2026-07-12
- Configuration: `evaluation.yaml`
- Model route: `openai-codex/gpt-5.6-luna`
- Profiles: `no-skill`, `consult-skill`
- Promptfoo evaluation ID: `eval-ebe-2026-07-12T19:20:40`
- Completed cells: 60 of 60
- Infrastructure errors: 0
- Cross-model fallbacks: 0
- Duration: 1,147,969 ms
- Result directory: `results/graphrag-cross-paper-30-compare/2026-07-12T19-20-32-563Z-compare/`

| Profile | Passed | Failed | Rate |
| --- | ---: | ---: | ---: |
| `no-skill` | 0 | 30 | 0.0% |
| `consult-skill` | 10 | 20 | 33.3% |

The treatment passed methodology taxonomy, graph-origin comparison, retrieval units, query routing, hybrid retrieval, offline construction cost, evaluation practices, benchmark bias, explainability, and optimization-operator questions.

### Treatment assertion coverage

| Metric | Passed | Rate |
| --- | ---: | ---: |
| Response format | 29/30 | 96.7% |
| Response contract | 28/30 | 93.3% |
| Evidence-path validity | 24/30 | 80.0% |
| Semantic structure | 15/30 | 50.0% |
| Page-citation grounding | 15/30 | 50.0% |
| Cross-paper evidence breadth | 14/30 | 46.7% |

The dominant failure is breadth control. Most failed syntheses selected one or more relevant papers, but missed the benchmark's relevance-backed minimum from its focus set; page citations and evidence breadth then failed together. Three answers cited papers but supplied only generic semantic artifacts instead of paper-specific concept paths. Six answers used at least one nonexistent or reconstructed evidence path. One answer was not valid JSON, and one otherwise parsed answer violated the exact response contract.

The next skill revision should require a mechanical pre-output gate that counts distinct eligible papers independently in `paper_ids`, `citations`, and exact evidence paths, and should over-select one verified source beyond the minimum before drafting. It should forbid emitting generic graph paths as the only evidence for any cited paper and require copying every paper or claim path directly from the ledger.

## Earlier quota-blocked attempt

An earlier run, `eval-Gvm-2026-07-12T16:56:16`, reached the same Luna-only wrapper but produced zero model responses because the usage allowance was exhausted. Its 60 infrastructure errors are retained under `results/graphrag-cross-paper-30-compare/2026-07-12T16-56-08-201Z-compare/` and are not included in the valid score above.
