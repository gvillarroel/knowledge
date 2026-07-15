# Semantic OKF Ensemble Answer-Output Evaluation

Status: **pass**. This report covers 90 live answers: three profiles, ten hard questions, and three repetitions per profile-question cell.

Correctness, semantic completeness, and important-negative coverage are model-judged under a blinded fixed rubric. Contract, evidence validity, grounding, exact claim identity, paper, and source metrics are recomputed mechanically against the exact final-03 bundle. Promptfoo's evidence named score is not reused.

| Profile | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `knowledge-only-control` | 0.0% | 13.3% | 5.6% | 5.4% | 90.6% | 75.1% | 3.7% | 75.3% | 39.8% | 94.2% | 5.0% |
| `adaptive-consult-control` | 3.3% | 23.3% | 82.6% | 82.5% | 83.0% | 72.7% | 55.3% | 76.0% | 74.8% | 86.7% | 78.3% |
| `ensemble-consult-treatment` | 53.3% | 100.0% | 100.0% | 100.0% | 96.7% | 91.1% | 86.0% | 98.5% | 98.5% | 99.2% | 100.0% |

## Stability diagnostics

Population standard deviation and worst-question means are shown as `σ / worst`. These diagnostics prevent a high average from hiding a brittle question family.

| Profile | Contract | Evidence validity | Grounding | Correctness | Completeness |
| --- | ---: | ---: | ---: | ---: | ---: |
| `knowledge-only-control` | 22.1% / 0.0% | 11.4% / 0.0% | 11.2% / 0.0% | 10.4% / 63.3% | 13.9% / 50.0% |
| `adaptive-consult-control` | 26.0% / 0.0% | 21.4% / 33.3% | 21.2% / 33.3% | 20.7% / 33.3% | 20.2% / 26.7% |
| `ensemble-consult-treatment` | 0.0% / 100.0% | 0.0% / 100.0% | 0.0% / 100.0% | 3.4% / 87.5% | 6.5% / 79.2% |

## Causal profile contrasts

Positive values favor the ensemble consultation treatment. Deltas are means of ten matched question-level differences, each question already averaged over its three repetitions.

| Contrast | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ensemble_vs_knowledge_only` | +53.3% | +86.7% | +94.4% | +94.6% | +6.2% | +16.0% | +82.3% | +23.2% | +58.8% | +5.0% | +95.0% |
| `ensemble_vs_adaptive` | +50.0% | +76.7% | +17.4% | +17.5% | +13.7% | +18.4% | +30.7% | +22.5% | +23.8% | +12.5% | +21.7% |

## Interpretation boundary

- Retrieval metrics and answer metrics are separate: finding a paper does not prove that the generated synthesis is correct, complete, or grounded.
- Semantic scores are model-judged evidence, not mechanical truth. The reviewer is blinded to profile and repetition, and the report preserves that qualification.
- A strict full-pass failure can coexist with useful partial scores because one failed assertion fails a complete Skill Arena cell.
- Raw answers, prompts, mappings, and reviewer transcripts remain append-only under the ignored results tree. This compact report retains only hashes, bindings, and aggregate scores.
- The report binds Skill Arena config `5042a9dae24bdac352ddf1c1f7482a5fe9cf76b0b771ae6d606a514eff5ad4ac`, config manifest `e9c5a337a28384bc9b59d6d583bb624077d76cf1362ffb506f21039385066bdf`, and every evaluator/reviewer implementation file by SHA-256.

## Metric contract

- **response_contract**: independent exact ordered JSON response schema and word-bound validation.
- **evidence_validity**: exact reviewed ledger, concept, source, paper, and cited-page binding per evidence item.
- **grounding**: supporting claim references represented by independently valid evidence items.
- **exact_atomic_evidence_coverage**: curated atomic claim identity represented in support and valid evidence.
- **required_paper_coverage**: required paper identity represented in paper_ids and citations.
- **required_source_coverage**: required reviewed-claim and paper source identities represented.
- **exact_negative_evidence_coverage**: curated important-negative identity represented in support and valid evidence.
- **claim_correctness**: blinded fixed-rubric fidelity of each candidate claim to supplied authoritative support records.
- **semantic_completeness**: blinded fixed-rubric coverage of every atomic ground-truth claim.
- **important_negative_coverage**: blinded fixed-rubric coverage of important exclusions and failure conditions.
