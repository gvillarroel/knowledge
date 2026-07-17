# q034 independent semantic holdout review

This report independently reviews the definitive Pi + GPT-5.3 Spark `q034` holdout observations for the six baseline/evolved consultation pairs. All twelve trials completed and produced parseable final JSON. The legacy baseline is retained as a contract-invalid observation because its evidence rows fail the closed locator/hash contract; there were no timeouts or invalid-JSON outputs on this question.

The review uses the checked evidence-first `q034` ground truth in `evaluations/semantic-okf-astro/benchmark/hard-ground-truth.jsonl`. The machine-readable review is [`q034-semantic-review.json`](q034-semantic-review.json), governed by the closed [`q034-semantic-review.schema.json`](q034-semantic-review.schema.json). Every observation binds the exact Harbor trial `result.json` SHA-256 and final-assistant-text SHA-256. The validator recomputes pair coverage and completeness arithmetic, checks the ground-truth IDs, compares the recorded Harbor metrics, classifies the real output status, and extracts the final answer from each locally retained Pi trace:

```text
python evaluations/semantic-okf-harbor/validate_q034_semantic_review.py --verify-artifacts
```

The candidates were frozen before this holdout was opened. These judgments document the results; no skill, benchmark, grader, runner, or prior review was changed from holdout evidence.

## Rubric

The five atomic answer claims (`a1`-`a5`), two important negatives (`n1`-`n2`), processing-boundary derivation, and authorization-before-inference derivation are each scored `0`, `0.5`, or `1`. Completeness is their unweighted nine-item mean. Semantic correctness and grounding are separate conservative manual judgments on a 0-1 scale. Grounding requires that cited evidence actually support the statement; retrieval, a valid hash, or qrel coverage alone does not establish entailment. Response contract is Harbor's exact binary result.

## Summary comparison

| Family | Variant | Output status | Harbor reward | Semantic correctness | Completeness | Grounding | Contract |
|---|---|---:|---:|---:|---:|---:|---:|
| Legacy | Baseline | Contract invalid | 0.000 | 0.90 | 0.944 | 0.00 | 0 |
| Legacy | Evolved | Valid | 0.992 | 0.90 | 0.944 | 0.85 | 1 |
| Embeddings | Baseline | Valid | 0.658 | 0.85 | 0.889 | 1.00 | 1 |
| Embeddings | Evolved | Valid | 0.988 | 0.95 | 0.889 | 1.00 | 1 |
| Classical | Baseline | Valid | 1.000 | 0.90 | 0.944 | 1.00 | 1 |
| Classical | Evolved | Valid | 1.000 | 0.95 | 0.722 | 1.00 | 1 |
| Adaptive | Baseline | Valid | 1.000 | 0.90 | 0.944 | 1.00 | 1 |
| Adaptive | Evolved | Valid | 1.000 | 0.95 | 0.778 | 1.00 | 1 |
| Entity graph | Baseline | Valid | 0.400 | 0.90 | 0.944 | 1.00 | 1 |
| Entity graph | Evolved | Valid | 0.466 | 0.95 | 0.722 | 1.00 | 1 |
| Ensemble | Baseline | Valid | 0.992 | 0.85 | 0.889 | 0.90 | 1 |
| Ensemble | Evolved | Valid | 1.000 | 0.85 | 0.722 | 1.00 | 1 |

## Ground-truth element coverage

| Family | Variant | a1 | a2 | a3 | a4 | a5 | n1 | n2 | Processing boundary | Authorization before inference |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Legacy | Baseline | 1 | 1 | 1 | 1 | 0.5 | 1 | 1 | 1 | 1 |
| Legacy | Evolved | 1 | 1 | 1 | 1 | 0.5 | 1 | 1 | 1 | 1 |
| Embeddings | Baseline | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 |
| Embeddings | Evolved | 1 | 0.5 | 1 | 1 | 0.5 | 1 | 1 | 1 | 1 |
| Classical | Baseline | 1 | 1 | 1 | 1 | 0.5 | 1 | 1 | 1 | 1 |
| Classical | Evolved | 1 | 1 | 1 | 0.5 | 0 | 1 | 0.5 | 1 | 0.5 |
| Adaptive | Baseline | 1 | 1 | 1 | 1 | 0.5 | 1 | 1 | 1 | 1 |
| Adaptive | Evolved | 1 | 1 | 1 | 0.5 | 0.5 | 1 | 0.5 | 1 | 0.5 |
| Entity graph | Baseline | 1 | 1 | 1 | 1 | 0.5 | 1 | 1 | 1 | 1 |
| Entity graph | Evolved | 1 | 0.5 | 1 | 0.5 | 0.5 | 1 | 0.5 | 1 | 0.5 |
| Ensemble | Baseline | 1 | 1 | 0.5 | 1 | 0.5 | 1 | 1 | 1 | 1 |
| Ensemble | Evolved | 1 | 1 | 1 | 0.5 | 0 | 1 | 0.5 | 1 | 0.5 |

The persistent hard case is `a5`: an unauthorized remote image is displayed without optimization, while `<Image />` can still reserve layout space to reduce cumulative layout shift. No answer states that complete behavior without ambiguity. Several answers instead claim a not-allowed error; others correctly say “not optimized” but omit display and CLS behavior.

The other recurring gap is the `a4`/`n2` condition. Naming `inferSize` and separately naming an allowlist is weaker than stating that remote dimension inference itself is allowed only after the source passes the authorization boundary.

## Evolution deltas

| Family | Reward delta | Semantic delta | Completeness delta | Grounding delta | Contract delta | q034 holdout observation |
|---|---:|---:|---:|---:|---:|---|
| Legacy | +0.992 | +0.00 | +0.000 | +0.85 | +1 | Strong operational repair; semantics are retained, but one claim-to-evidence mapping is weak |
| Embeddings | +0.330 | +0.10 | +0.000 | +0.00 | +0 | Clear Harbor and correctness gain; public-dimension coverage replaces part of the baseline's remote-outcome gap |
| Classical | +0.000 | +0.05 | -0.222 | +0.00 | +0 | Harbor tie, but the shorter answer loses the unauthorized branch and explicit authorization-before-inference condition |
| Adaptive | +0.000 | +0.05 | -0.167 | +0.00 | +0 | Harbor tie with a manual completeness regression |
| Entity graph | +0.066 | +0.05 | -0.222 | +0.00 | +0 | Small Harbor gain does not compensate for lost policy detail |
| Ensemble | +0.008 | +0.00 | -0.167 | +0.10 | +0 | Fixes the wrong config identifier and reaches Harbor 1.0, but drops the unauthorized-image behavior |

## Interpretation

The most important result is metric separation. Entity-graph baseline receives Harbor `0.400` because its evidence-to-hard-claim proxy is weak, yet manual review finds `0.944` completeness with fully usable grounding. Classical evolved receives Harbor `1.000`, yet manual completeness is only `0.722`. Neither metric is wrong: Harbor scores the declared retrieval/evidence contract, while this review scores the semantics of the answer text against all nine ground-truth elements.

Among valid, fully grounded outputs, classical baseline, adaptive baseline, and entity-graph baseline have the highest manual completeness (`0.944`). Each still has an ambiguity in the unauthorized-remote branch, so none is a perfect answer. Legacy baseline matches that completeness but is unusable because every evidence locator/hash fails; the legacy evolution is a real operational improvement, although a mismatched citation keeps grounding at `0.85`.

Embeddings has the clearest all-around evolution on this case: reward rises from `0.658` to `0.988`, semantic correctness from `0.85` to `0.95`, and the contract remains valid. Its overall completeness is unchanged because adding the correct untrusted-inference condition is offset by omitting mandatory dimensions for public images.

The ensemble baseline exposes a separate response-quality failure that Harbor does not detect: it repeatedly uses `imageDomains` instead of the deployable `image.domains` key. The ensemble evolution repairs that identifier and all its citations are usable, but it replaces the checked unauthorized-image fallback with a blocked/not-allowed outcome.

This is one frozen holdout question, not a population estimate. The result must not be used to tune the candidates after the fact, and it cannot by itself establish a universally best skill. It does show why promotion gates need separate retrieval, evidence-validity, semantic-completeness, grounding, and response-contract checks rather than a single compensating score.
