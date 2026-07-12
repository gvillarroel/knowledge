# GraphRAG Cross-Paper Evaluation Status

Date: 2026-07-12

## Current experiment

- Corpus: 15 version-pinned GraphRAG papers, 304 PDF pages, and 65,237,570 source bytes.
- Knowledge snapshot: 31 sources, 874 normalized records, 831 reviewed paper claims, 28 analysis terms, and 15 paper concepts.
- Snapshot tree SHA-256: `331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`.
- Question battery: 30 semantically distinct cross-paper synthesis prompts.
- Full profiles: isolated `no-skill` and `skill`.
- Active PI model: `openai-codex/gpt-5.6-luna` for every request.
- Routing: one model, one attempt, no alternate route or retry.
- Scoring: six deterministic assertions per cell; no model-based judge.

The full, smoke, six-question holdout, and paired holdout manifests validate with zero unsupported cells. The active wrapper rejects any non-Luna model value and accepts exactly one `--model` argument.

## Full baseline

- Evaluation ID: `eval-88L-2026-07-12T14:57:27`.
- Run directory: `results/graphrag-cross-paper-30-compare/2026-07-12T14-57-22-738Z-compare`.
- Execution: 60 requested and 60 completed cells, with no reused scenarios.
- Treatment result: 14/30 cells passed all six assertions; 139/180 individual assertions passed.
- Control result: 0/30 cells passed all six assertions; 28 returned the required closed-book abstention and two timed out.
- Treatment technical errors: 0.
- Duration: 1,751,697 ms.

Treatment assertion totals:

| Assertion | Passed |
|---|---:|
| JSON response format | 30/30 |
| Response contract | 28/30 |
| Existing evidence paths | 24/30 |
| Semantic structure and relevant-source coverage | 19/30 |
| Page-citation grounding | 19/30 |
| Cross-paper evidence coverage | 19/30 |

The dominant failure was not missing prose or dimensions. Eleven answers selected enough papers in total but were exactly one directly relevant paper below the prompt's minimum. Six answers contained at least one invented, shortened, wildcard, or incorrectly hashed evidence path.

## Trace-guided skill evolution

The fixed holdout contains q005, q010, q015, q020, q025, and q029. The other 24 treatment cells produced 12 success and 12 failure traces. Holdout traces were excluded from patch discovery.

Consolidation required support from at least two independent traces. It promoted rules for:

- breadth-before-depth source selection using a source-by-clause coverage ledger;
- counting only directly relevant sources toward a requested minimum;
- aligning selected sources, citations, pages, and evidence paths;
- copying exact `concept_path` values from the ledger;
- rejecting abbreviated filenames, wildcards, placeholders, and reconstructed hashes;
- preserving the successful comparative synthesis and exact output-contract behavior.

Baseline skill SHA-256: `3319d50ebabbf8427c7fb8b667e9d596847138a4abf23c5bab8f97dee5f94641`.

Promoted skill SHA-256: `4b8dece35b21e79ba5f66984b8d1c656759abf0e37da1323f7b17e0af7c105f1`.

## Holdout validation

The initial unchanged-candidate holdout run completed six fresh Luna requests with no errors. It improved full-cell success from the previously recorded 2/6 baseline to 3/6, but its assertion total was mixed. A paired confirmation was therefore run without modifying the candidate.

Paired confirmation:

- Evaluation ID: `eval-eK9-2026-07-12T15:41:56`.
- Run directory: `results/graphrag-cross-paper-holdout-6-paired/2026-07-12T15-41-51-344Z-compare`.
- Execution: 12 requested and 12 completed cells, zero errors, and no reused scenarios.

| Profile | Cells passing 6/6 | Assertions passed | Valid paths | Semantic/citation/cross-paper groups |
|---|---:|---:|---:|---:|
| Frozen baseline | 2/6 | 22/36 | 4/6 | 2/6 each |
| Improved skill | 4/6 | 30/36 | 6/6 | 4/6 each |

The candidate doubled full-cell holdout success and improved every diagnostic group without a technical error. It is therefore promoted.

## Repository verification

- Full test suite: 728 passed.
- Application coverage: 90.9% against the required 80% threshold.
- Skill package validation: passed.
- Project OKF projection: current and conformant.
- Trace consolidation: 10 accepted patches, zero scope or conflict violations.
- Active GraphRAG route audit: only `openai-codex/gpt-5.6-luna`; the production skill contains no distributed data-processing dependency or terminology.

## Reproduction commands

```powershell
python evaluations\graphrag-cross-paper\scripts\generate_benchmark.py --check
skill-arena val-conf evaluations\graphrag-cross-paper\evaluation.yaml
skill-arena val-conf evaluations\graphrag-cross-paper\holdout-evaluation.yaml
skill-arena val-conf evaluations\graphrag-cross-paper\paired-holdout-evaluation.yaml
skill-arena evaluate evaluations\graphrag-cross-paper\paired-holdout-evaluation.yaml --dry-run
```
