# q032 independent semantic answer review

This report independently reviews the definitive Pi + GPT-5.3 Spark `*-q032-grader-r1` observations for the six baseline/evolved consultation pairs. Eleven trials produced final answers; the ensemble baseline reached the 600-second agent timeout and is retained as an execution failure. Earlier pre-fix, empty, and infrastructure-only runs are excluded.

The review uses the checked evidence-first `q032` ground truth in `evaluations/semantic-okf-astro/benchmark/hard-ground-truth.jsonl`. The machine-readable review is [`q032-semantic-review.json`](q032-semantic-review.json), governed by the closed [`q032-semantic-review.schema.json`](q032-semantic-review.schema.json). Every observation binds the exact Harbor trial `result.json` SHA-256 and final-assistant-text SHA-256. The validator also recomputes pair coverage and completeness arithmetic, checks the ground-truth IDs, compares the recorded Harbor metrics, and extracts the final answer from each locally retained Pi trace:

```text
python evaluations/semantic-okf-harbor/validate_q032_semantic_review.py --verify-artifacts
```

## Rubric

The five atomic answer claims (`a1`-`a5`), two important negatives (`n1`-`n2`), cacheable-design derivation, and deployment-correctness derivation are each scored `0`, `0.5`, or `1`. Completeness is their unweighted nine-item mean. Semantic correctness and grounding are separate conservative manual judgments on a 0-1 scale. Grounding requires that cited evidence actually support the prose; document retrieval, a valid hash, or evidence sufficiency alone does not establish entailment. Response contract is Harbor's exact binary result.

## Summary comparison

| Family | Variant | Output status | Harbor reward | Semantic correctness | Completeness | Grounding | Contract |
|---|---|---:|---:|---:|---:|---:|---:|
| Legacy | Baseline | Contract invalid | 0.000 | 0.95 | 0.778 | 0.00 | 0 |
| Legacy | Evolved | Valid | 1.000 | 0.95 | 0.722 | 0.95 | 1 |
| Embeddings | Baseline | Valid | 0.485 | 0.95 | 0.722 | 1.00 | 1 |
| Embeddings | Evolved | Valid | 0.704 | 0.95 | 0.833 | 0.95 | 1 |
| Classical | Baseline | Valid | 0.726 | 0.95 | 0.722 | 1.00 | 1 |
| Classical | Evolved | Valid | 1.000 | 0.95 | 0.722 | 1.00 | 1 |
| Adaptive | Baseline | Valid | 1.000 | 0.90 | 0.667 | 1.00 | 1 |
| Adaptive | Evolved | Valid; quality gate failed | 0.000 | 0.80 | 0.611 | 0.75 | 1 |
| Entity graph | Baseline | Valid | 0.548 | 0.90 | 0.667 | 0.95 | 1 |
| Entity graph | Evolved | Valid | 0.726 | 0.95 | 0.889 | 1.00 | 1 |
| Ensemble | Baseline | Timeout | 0.000 | 0.00 | 0.000 | 0.00 | 0 |
| Ensemble | Evolved | Valid | 0.992 | 0.90 | 0.722 | 0.95 | 1 |

## Ground-truth element coverage

| Family | Variant | a1 | a2 | a3 | a4 | a5 | n1 | n2 | Cacheable design | Deployment correctness |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Legacy | Baseline | 1 | 1 | 1 | 0.5 | 1 | 0.5 | 0.5 | 1 | 0.5 |
| Legacy | Evolved | 0.5 | 1 | 1 | 0 | 1 | 1 | 0.5 | 1 | 0.5 |
| Embeddings | Baseline | 1 | 1 | 1 | 0 | 1 | 0.5 | 0.5 | 1 | 0.5 |
| Embeddings | Evolved | 0.5 | 1 | 1 | 1 | 1 | 0.5 | 0.5 | 1 | 1 |
| Classical | Baseline | 0.5 | 1 | 1 | 0 | 1 | 0.5 | 1 | 1 | 0.5 |
| Classical | Evolved | 1 | 0.5 | 1 | 0 | 1 | 1 | 0.5 | 1 | 0.5 |
| Adaptive | Baseline | 0.5 | 1 | 1 | 0 | 1 | 0.5 | 0.5 | 1 | 0.5 |
| Adaptive | Evolved | 0.5 | 0.5 | 1 | 0 | 1 | 1 | 0.5 | 0.5 | 0.5 |
| Entity graph | Baseline | 1 | 0.5 | 1 | 0 | 1 | 1 | 0.5 | 0.5 | 0.5 |
| Entity graph | Evolved | 1 | 1 | 1 | 1 | 1 | 0.5 | 0.5 | 1 | 1 |
| Ensemble | Baseline | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ensemble | Evolved | 0.5 | 1 | 1 | 0.5 | 1 | 0.5 | 0.5 | 1 | 0.5 |

The strict omissions matter. Most answers do not fully state `a4`: inside a server island, `Astro.url` identifies the special island endpoint, so page identity must be passed explicitly or recovered from `Referer`. Most also only imply `n2`; they prescribe a stable key during overlap without saying why the default new random key per build is unsafe. `n1` is often weakened from “do not pass an entire object when an identifier suffices” to a generic instruction to keep props small.

## Evolution deltas

| Family | Reward delta | Semantic delta | Completeness delta | Grounding delta | Contract delta | q032 disposition |
|---|---:|---:|---:|---:|---:|---|
| Legacy | +1.000 | +0.00 | -0.056 | +0.95 | +1 | Operational gain; evidence/contract fixed, but page-URL coverage falls |
| Embeddings | +0.219 | +0.00 | +0.111 | -0.05 | +0 | Clear semantic gain from adding page identity |
| Classical | +0.274 | +0.00 | +0.000 | +0.00 | +0 | Harbor evidence gain; manual completeness is unchanged |
| Adaptive | -1.000 | -0.10 | -0.056 | -0.25 | +0 | Reject: invalid evidence row and an over-prescribed server-default design |
| Entity graph | +0.179 | +0.05 | +0.222 | +0.05 | +0 | Strongest manual answer; all five atoms are explicit |
| Ensemble | +0.992 | +0.90 | +0.722 | +0.95 | +1 | Clear execution gain: timeout converted to a valid grounded answer |

## Interpretation

The entity-graph evolution is the strongest answer under the manual rubric. It is the only output to state all five atomic claims, including the isolated `Astro.url`/`Referer` rule, and reaches `0.889` completeness. Its Harbor reward is only `0.726` because the response cites one full authoritative server-islands record rather than both required document identities. That difference is expected: required-document retrieval and semantic answer completeness measure different things.

Legacy, classical, and adaptive baseline each reach Harbor `1.000`, but that does not make their prose equally complete. Legacy evolved and classical evolved score `0.722` manual completeness; adaptive baseline scores `0.667`; all omit the page-URL rule. Conversely, embeddings evolved has lower Harbor reward (`0.704`) but higher manual completeness (`0.833`) because its prose supplies page identity even though its evidence set covers only one required document identity.

Adaptive is a genuine regression. Its evolved response remains valid JSON, but one evidence row is invalid, causing the non-compensating quality gate to reduce reward from `1.000` to zero. It also suggests `output: 'server'` where the minimum mostly static design only requires an adapter plus `server:defer`. Ensemble shows the opposite outcome: the evolution converts a 600-second timeout into a valid, grounded answer with reward `0.992`.

This is one frozen development question, so it is diagnostic rather than a population estimate. It must not be used alone to promote a candidate or to tune after holdout. Harbor retrieval/evidence metrics, manual semantic correctness, completeness, grounding, and contract compliance remain separate axes; averaging them into one number would obscure the failures this review is designed to expose.
