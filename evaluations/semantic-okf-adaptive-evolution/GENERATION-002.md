# Generation 2: Minimal Direct Support

Generation 2 keeps the benchmark frozen and retains the generation-1 facet candidate generator and response finalizer. It changes only the consult policy: use expansion for discovery, then minimize support to directly entailing reviewed records; remove unused or merely topical evidence; split over-broad claims; and qualify an unresolved facet instead of returning a null answer when the corpus supports a substantive partial response.

## Offline evidence discovery

The normal retrieval route is unchanged: 83.82% Recall@10 and 83.43% nDCG@10 across all forty questions, with 100% validated evidence. The primary hard-question pack retains 60.0% exact answer-claim Recall@30, 75.0% important-negative recall, and 98.0% required-paper recall.

The facet-separated union raises exact candidate coverage, but uses a larger variable budget:

| Candidate metric | Primary top-30 | Facet union |
| --- | ---: | ---: |
| Answer-claim coverage | 60.0% | 76.5% |
| Important-negative coverage | 75.0% | 88.3% |
| Required-paper coverage | 98.0% | 100.0% |
| Mean unique candidates | 30 | 81 |

The union is not Recall@30 and must not be placed in the direct top-10 or top-30 table as if the budgets matched.

## Isolated answer result

All twenty Skill Arena cells completed with zero execution errors and zero strict conjunctive passes. The treatment passed the response contract on all ten answers, covered nine of ten exact negative assertions, and did not return a null answer. The blinded and independently validated metrics were:

| Metric | Control | Treatment | Delta |
| --- | ---: | ---: | ---: |
| Response contract | 10.0% | 100.0% | +90.0 points |
| Correctness | 98.8% | 98.0% | -0.8 |
| Completeness | 89.0% | 84.8% | -4.2 |
| Evidence validity | 73.5% | 94.4% | +20.9 |
| Grounding | 72.6% | 93.7% | +21.1 |
| Exact atomic IDs | 49.5% | 53.5% | +4.0 |
| Required papers | 89.2% | 93.0% | +3.8 |
| Required sources | 79.2% | 91.3% | +12.2 |
| Important negatives | 100.0% | 100.0% | 0.0 |

The control varied substantially from earlier runs, so absolute cross-run values and within-run causal deltas are both reported. The treatment's 98.0% correctness, 84.8% completeness, 94.4% evidence validity, 93.7% grounding, 93.0% paper coverage, and 100% negative coverage make it a credible Pareto survivor. It is not a universal winner: generation 0 retains higher exact evidence validity, grounding, and exact-ID coverage, while generation 2 is much stronger on response contract and correctness.

## Decision

Keep generation 2 as the default consult policy and retain generation 0 as the high-grounding comparison survivor. Discard generation 1's unrestricted evidence-selection policy. A future untouched question set is required before claiming general superiority, because all three generations used the same frozen hard ten for diagnosis.
