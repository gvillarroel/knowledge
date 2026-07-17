# q031 independent semantic answer review

This report independently reviews the actual Pi + GPT-5.3 Spark final answers for the six baseline/evolved consultation pairs on `q031`. It uses the checked evidence-first ground truth in `evaluations/semantic-okf-astro/benchmark/hard-ground-truth.jsonl`. The earlier entity-graph and ensemble authentication failures are excluded; the completed `*-auth-r1` results are the evolved observations.

The machine-readable review is [`q031-semantic-review.json`](q031-semantic-review.json), governed by the closed [`q031-semantic-review.schema.json`](q031-semantic-review.schema.json). Every observation binds the exact Harbor trial `result.json` SHA-256 and final-answer SHA-256. The validator recomputes pair coverage and completeness arithmetic and can verify locally retained raw artifacts:

```text
python evaluations/semantic-okf-harbor/validate_semantic_review.py --verify-artifacts
```

## Rubric

Each of the five atomic answer claims (`a1`-`a5`), two important negatives (`n1`-`n2`), join derivation, and conditional derivation is scored `0`, `0.5`, or `1`. Completeness is their unweighted nine-item mean. Semantic correctness and grounding are separate conservative manual judgments on a 0-1 scale. Grounding asks whether the answer's cited evidence actually supports its prose; a relevant retrieved document or a passing hash check is not by itself proof of entailment. Response contract is the exact Harbor binary result.

## Summary comparison

| Family | Variant | Output status | Harbor reward | Semantic correctness | Completeness | Grounding | Contract |
|---|---|---:|---:|---:|---:|---:|---:|
| Legacy | Baseline | Contract invalid | 0.000 | 0.90 | 0.722 | 0.00 | 0 |
| Legacy | Evolved | Invalid JSON | 0.000 | 0.80 | 0.667 | 0.00 | 0 |
| Embeddings | Baseline | Valid | 0.270 | 0.90 | 0.722 | 0.90 | 1 |
| Embeddings | Evolved | Valid | 0.991 | 0.85 | 0.667 | 1.00 | 1 |
| Classical | Baseline | Valid | 0.960 | 0.90 | 0.722 | 1.00 | 1 |
| Classical | Evolved | Valid | 0.995 | 0.95 | 0.611 | 1.00 | 1 |
| Adaptive | Baseline | Valid; quality gate failed | 0.000 | 0.85 | 0.611 | 0.90 | 1 |
| Adaptive | Evolved | Valid | 0.995 | 0.75 | 0.500 | 0.90 | 1 |
| Entity graph | Baseline | Timeout | 0.000 | 0.00 | 0.000 | 0.00 | 0 |
| Entity graph | Evolved | Valid | 0.622 | 0.90 | 0.611 | 0.75 | 1 |
| Ensemble | Baseline | Valid | 0.767 | 0.90 | 0.722 | 0.90 | 1 |
| Ensemble | Evolved | Valid | 0.603 | 0.85 | 0.556 | 0.95 | 1 |

## Ground-truth element coverage

| Family | Variant | a1 | a2 | a3 | a4 | a5 | n1 | n2 | Join | Conditional |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Legacy | Baseline | 0.5 | 1 | 0.5 | 0 | 1 | 1 | 1 | 1 | 0.5 |
| Legacy | Evolved | 0.5 | 1 | 0.5 | 0.5 | 0.5 | 1 | 0.5 | 1 | 0.5 |
| Embeddings | Baseline | 0.5 | 1 | 0.5 | 0 | 1 | 1 | 1 | 1 | 0.5 |
| Embeddings | Evolved | 0.5 | 1 | 0.5 | 0.5 | 0.5 | 1 | 0.5 | 1 | 0.5 |
| Classical | Baseline | 0.5 | 1 | 0.5 | 0 | 1 | 1 | 1 | 1 | 0.5 |
| Classical | Evolved | 0.5 | 0.5 | 0.5 | 0 | 1 | 1 | 1 | 0.5 | 0.5 |
| Adaptive | Baseline | 0.5 | 1 | 0.5 | 0 | 0.5 | 1 | 0.5 | 1 | 0.5 |
| Adaptive | Evolved | 0.5 | 0.5 | 0.5 | 0 | 0.5 | 1 | 0.5 | 0.5 | 0.5 |
| Entity graph | Baseline | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Entity graph | Evolved | 0.5 | 0.5 | 0.5 | 0 | 1 | 1 | 1 | 0.5 | 0.5 |
| Ensemble | Baseline | 0.5 | 1 | 0.5 | 0 | 1 | 1 | 1 | 1 | 0.5 |
| Ensemble | Evolved | 0.5 | 0.5 | 0.5 | 0 | 1 | 0.5 | 1 | 0.5 | 0.5 |

The strict recurring omissions are meaningful. No answer fully states `a1` because all omit rate limiting. No answer fully states `a3` because none captures both configured session drivers and adapter-specific defaults. No answer fully states `a4`: the outputs do not explicitly contrast `context.rewrite` starting a new rendering phase and rerunning middleware with `next(Request-or-path)` rewriting in place without rerunning the chain.

## Evolution deltas

| Family | Reward delta | Semantic delta | Completeness delta | Grounding delta | Contract delta | q031 disposition |
|---|---:|---:|---:|---:|---:|---|
| Legacy | +0.000 | -0.10 | -0.056 | +0.00 | +0 | Reject: evolved output is invalid JSON |
| Embeddings | +0.720 | -0.05 | -0.056 | +0.10 | +0 | Mixed: major evidence gain, slightly less explicit semantics |
| Classical | +0.034 | +0.05 | -0.111 | +0.00 | +0 | Mixed: most correct evolved prose, less complete against all required atoms |
| Adaptive | +0.995 | -0.10 | -0.111 | +0.00 | +0 | Mixed: quality-gate repair, material semantic specificity loss |
| Entity graph | +0.622 | +0.90 | +0.611 | +0.75 | +1 | Clear gain: timeout converted to a valid answer |
| Ensemble | -0.164 | -0.05 | -0.167 | +0.05 | +0 | Reject on q031: lower reward, focus, and completeness |

## Interpretation

The Harbor evolution most clearly succeeds for entity graph: it changes a 600-second timeout into a valid, mostly correct response. Embeddings also makes a large operational improvement by restoring full required-document/evidence coverage and a valid grounded answer. Classical remains the strongest overall answer candidate on this case: its evolved answer has the highest manual semantic-correctness score and ties the top Harbor reward, though its concise prose omits more required ground-truth nuances than its baseline.

Adaptive demonstrates why the semantic review must remain separate from verifier reward. Its evolution fixes evidence first-use ordering and moves reward from zero to `0.995`, but the prose omits the middleware coarse-gate role and introduces a questionable categorical pipeline-order explanation; its manual completeness falls from `0.611` to `0.500`. Ensemble regresses even under the Harbor score and adds irrelevant claims. Legacy cannot be promoted because neither answer is contract-usable.

This is one frozen training question and therefore diagnostic, not a population estimate. Promotion decisions still require the frozen development and untouched holdout cases. The manual scores must not be averaged into the Harbor retrieval score as if they measured the same construct.
