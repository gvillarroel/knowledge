# Grounded Answer Comparison on the Ten Hard Questions

All values are means across ten actual answers. Semantic correctness, completeness, and important-negative coverage come from a blinded fixed-rubric review; evidence validity and grounding are independently recomputed against the authoritative ledger and concept files. The strict Skill Arena full-pass rate is reported separately because one failed sub-contract fails a whole cell.

| Method / profile | Strict all-contract | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `legacy` / `knowledge-only-control` | 0.0% | 40.0% | 82.6% | 82.8% | 94.0% | 83.2% | 57.5% | 82.2% | 79.2% | 100.0% |
| `legacy` / `legacy-consult-treatment` | 0.0% | 10.0% | 84.3% | 83.5% | 88.8% | 75.0% | 50.5% | 75.0% | 74.0% | 90.0% |
| `embedding` / `knowledge-only-control` | 0.0% | 20.0% | 70.9% | 71.0% | 95.2% | 80.8% | 42.5% | 77.5% | 72.5% | 97.5% |
| `embedding` / `embedding-consult-treatment` | 0.0% | 40.0% | 83.6% | 83.4% | 96.2% | 82.8% | 48.5% | 89.2% | 85.4% | 100.0% |
| `classical` / `knowledge-only-control` | 0.0% | 20.0% | 83.9% | 83.4% | 95.5% | 82.2% | 49.5% | 79.7% | 74.7% | 100.0% |
| `classical` / `classical-consult-treatment` | 0.0% | 30.0% | 80.4% | 79.7% | 91.5% | 82.2% | 37.0% | 86.7% | 79.2% | 95.0% |
| `entity_graph` / `knowledge-only-control` | 0.0% | 30.0% | 75.6% | 76.0% | 100.0% | 82.0% | 50.0% | 84.2% | 75.8% | 100.0% |
| `entity_graph` / `entity-graph-consult-treatment` | 0.0% | 40.0% | 60.0% | 60.0% | 78.8% | 70.2% | 31.5% | 67.7% | 57.6% | 90.0% |

## Paired treatment deltas

Positive values favor the single-skill treatment over its same-bundle knowledge-only control.

| Method | Correctness | Completeness | Evidence validity | Grounding | Papers | Negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `legacy` | -5.2% | -8.2% | +1.7% | +0.6% | -7.2% | -10.0% |
| `embedding` | +1.0% | +2.0% | +12.7% | +12.4% | +11.7% | +2.5% |
| `classical` | -4.0% | +0.0% | -3.5% | -3.6% | +7.0% | -5.0% |
| `entity_graph` | -21.2% | -11.8% | -15.6% | -16.0% | -16.5% | -10.0% |

## Reading the metrics

- **Correctness** asks whether each stated candidate claim is faithful to its cited reviewed claim records.
- **Completeness** asks whether the answer conveys every atomic ground-truth claim, allowing reviewed paraphrases and equivalent supporting records.
- **Exact atomic IDs** is deliberately stricter: it requires the particular reviewed claim identities chosen during evidence-first question construction.
- **Grounding** requires every cited supporting claim ID to appear in the answer's evidence list.
- **Evidence validity** accepts normalized `knowledge/` prefixes and integer page locators, but still requires an exact ledger/concept/paper/page binding.
