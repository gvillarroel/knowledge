# Generation 1: Facet Coverage and Response Finalization

Generation 1 kept the frozen forty retrieval questions, ten hard answer prompts, assertions, ground truth, bundle, model, and control profile unchanged. Candidate 10 added a query-derived `coverage-pack` and an authoritative `finalize-answer` path. The Skill Arena task object has the same canonical SHA-256 as generations 0 and 2: `da2fffaf3ea60976802ed6782633e9b2f079a6ddf65510d98a8c426c854d4a4b`.

## Result

The deterministic offline gates passed. Ordinary retrieval remained unchanged at 83.82% Recall@10 and 83.43% nDCG@10; the primary hard-question evidence pack retained 60.0% exact answer-claim Recall@30, 75.0% important-negative recall, 98.0% required-paper recall, and 100% binding validity.

The live treatment achieved 100% response-contract compliance in Promptfoo, up from 40% in generation 0. The blinded answer review nevertheless rejected the full policy:

| Metric | Control | Treatment | Delta |
| --- | ---: | ---: | ---: |
| Correctness | 97.1% | 87.1% | -10.0 points |
| Completeness | 83.5% | 80.8% | -2.8 |
| Evidence validity | 91.9% | 85.8% | -6.1 |
| Grounding | 92.6% | 86.7% | -5.8 |
| Required papers | 83.2% | 87.5% | +4.3 |
| Important negatives | 100.0% | 90.0% | -10.0 |

One treatment answer abstained even though the corpus supported a substantive comparison. The other nine treatment answers averaged 96.8% correctness and 89.7% completeness, showing that the aggregate regression was concentrated but still real. Several outputs also manually mistyped otherwise authoritative claim-source paths, demonstrating that instructions alone did not guarantee use of the finalizer.

## Decision

Discard the unrestricted facet-selection policy. Retain the deterministic finalizer and query-derived facet candidate generator as components. Generation 2 must minimize the final evidence set, require direct entailment, remove merely topical records, and qualify unresolved facets instead of turning a partially supported question into a null answer.
