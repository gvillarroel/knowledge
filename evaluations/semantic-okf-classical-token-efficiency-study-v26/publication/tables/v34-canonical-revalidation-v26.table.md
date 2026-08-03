# Exact V34 versus frozen canonical Classical

Native tokens are input plus output tokens; cache tokens are a subset of input tokens and are not added again. The development comparison used six paired, isolated QEC consultation tasks. Acceptance required a mean token ratio strictly below 0.70, median nonincrease, complete error-free zero-retry execution, no regression in any paired numeric verifier metric, and an independent semantic review with zero regressed cases.

| Treatment | Total tokens | Mean tokens | Median tokens | Primary passes | Numeric verifier regressions | Independent semantic regressions | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Frozen canonical Classical | 6,015,810 | 1,002,635.0 | 779,410.0 | 3/6 | Baseline | Baseline | Control |
| Exact frozen V34 | 79,744 | 13,290.7 | 12,782.0 | 6/6 | 0 | 4/6 | Reject |

V34 reduced mean native tokens by 98.6744% and was cheaper in all six cases. It nevertheless failed the non-compensating semantic gate: an independent no-context-fork reviewer found regressions in four of six paired answers after checking correctness, explicit coverage, relevance, source support, citation assignment, material omissions, and new critical defects. Automatic metrics therefore overstated answer preservation for this treatment.

Validation and holdout remained sealed and were not released. V34 was not promoted.
