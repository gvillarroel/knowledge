# Complete solution-agnostic Classical knowledge-generation strategy audit

The table covers every completed strategy job in the Classical chunking program. Semantic review used Pi with GPT-5.6 Luna at high thinking, two full-order-reversed judgments per case, and conservative consensus. Reviewer-visible inputs excluded answer-selected evidence, retrieval traces, strategy and job names, paths, hashes, locators, native rewards, and token usage.

Rows are comparable only within the same cohort. `rubric-only` means the historical task predates separate hard-ground-truth claims; `rubric+truth` uses both authored required points and hard-ground-truth claims. Native reward remains mechanical, not semantic quality.

| Cohort | Contract | Strategy | Native reward | Mean tokens | Token delta | Evidence valid | Full-quality | Required coverage | Coverage delta | Satisfied points | Major-error cases | Order agreement | Paired result vs canonical | Semantic gate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| q019-q024 | rubric-only | canonical | 0.797 | 632,748.8 | +0.00% | 5/6 | 5/6 | 83.33% | +0.00 pp | 5/6 | 1/6 | 100.00% | baseline | baseline |
| q019-q024 | rubric-only | structural-envelope-v3 | 0.773 | 23,760.3 | -96.24% | 5/6 | 3/6 | 58.33% | -25.00 pp | 3/6 | 3/6 | 100.00% | regressed=2, tie=4 | reject |
| q019-q024 | rubric-only | canonical-passage-envelope-v3 | 0.646 | 24,022.8 | -96.20% | 5/6 | 4/6 | 66.67% | -16.67 pp | 4/6 | 2/6 | 91.67% | regressed=1, tie=5 | reject |
| q019-q024 | rubric-only | canonical-passage-composer-v4 | 0.969 | 51,273.3 | -91.90% | 6/6 | 4/6 | 75.00% | -8.33 pp | 4/6 | 2/6 | 91.67% | regressed=1, tie=5 | reject |
| q019-q024 | rubric-only | facet-expanded-passage-v5 | 0.317 | 201,913.5 | -68.09% | 2/6 | 4/6 | 75.00% | -8.33 pp | 4/6 | 2/6 | 91.67% | improved=1, regressed=1, tie=4 | reject |
| q019-q024 | rubric-only | dynamic-source-cards-v6 | 0.333 | 56,604.0 | -91.05% | 2/6 | 5/6 | 91.67% | +8.33 pp | 5/6 | 1/6 | 91.67% | improved=1, regressed=1, tie=4 | reject |
| q019-q024 | rubric-only | source-deduplicated-cards-v7 | 0.969 | 50,788.8 | -91.97% | 6/6 | 4/6 | 83.33% | +0.00 pp | 4/6 | 2/6 | 91.67% | improved=1, regressed=1, tie=4 | reject |
| q019-q024 | rubric-only | acronym-dehyphenated-focus-v8 | 0.648 | 51,524.7 | -91.86% | 4/6 | 5/6 | 91.67% | +8.33 pp | 5/6 | 1/6 | 91.67% | improved=1, regressed=1, tie=4 | reject |
| q019-q024 | rubric-only | terminal-passthrough-v9 | 0.805 | 51,889.8 | -91.80% | 5/6 | 4/6 | 83.33% | +0.00 pp | 4/6 | 2/6 | 91.67% | improved=1, regressed=1, tie=4 | reject |
| q019-q024 | rubric-only | concept-path-first-v10 | 0.798 | 52,203.0 | -91.75% | 5/6 | 5/6 | 91.67% | +8.33 pp | 5/6 | 1/6 | 91.67% | improved=1, regressed=1, tie=4 | reject |
| q019-q024 | rubric-only | structured-multiline-v11 | 0.959 | 52,121.3 | -91.76% | 6/6 | 5/6 | 91.67% | +8.33 pp | 5/6 | 1/6 | 91.67% | improved=1, regressed=1, tie=4 | reject |
| q041-q046 | rubric-only | canonical | 0.294 | 705,460.8 | +0.00% | 2/6 | 1/6 | 87.50% | +0.00 pp | 19/24 | 0/6 | 96.67% | baseline | baseline |
| q041-q046 | rubric-only | structured-multiline-v11 | 0.677 | 63,660.2 | -90.98% | 5/6 | 1/6 | 56.25% | -31.25 pp | 10/24 | 5/6 | 93.33% | improved=1, regressed=5 | reject |
| q041-q046 | rubric-only | facet-aware-multifocus-v12 | 0.448 | 60,903.7 | -91.37% | 3/6 | 1/6 | 45.83% | -41.67 pp | 10/24 | 3/6 | 100.00% | improved=1, regressed=3, tie=2 | reject |
| q041-q046 | rubric-only | clause-reserved-v13 | 0.821 | 61,761.5 | -91.25% | 5/6 | 1/6 | 60.42% | -27.08 pp | 11/24 | 2/6 | 93.33% | improved=1, regressed=3, tie=2 | reject |
| q041-q046 | rubric-only | structural-head-backoff-v16 | 0.960 | 83,565.2 | -88.15% | 6/6 | 0/6 | 70.83% | -16.67 pp | 12/24 | 2/6 | 93.33% | regressed=4, tie=2 | reject |
| q041-q046 | rubric-only | reference-aware-v18 | 0.960 | 82,489.8 | -88.31% | 6/6 | 0/6 | 64.58% | -22.92 pp | 9/24 | 3/6 | 90.00% | regressed=4, tie=2 | reject |
| q041-q046 | rubric-only | prose-preferred-anchor-v21 | 0.956 | 78,684.0 | -88.85% | 6/6 | 0/6 | 70.83% | -16.67 pp | 12/24 | 3/6 | 93.33% | regressed=4, tie=2 | reject |
| q041-q046 | rubric-only | overlap-robust-v24 | 0.833 | 78,900.5 | -88.82% | 5/6 | 1/6 | 79.17% | -8.33 pp | 15/24 | 0/6 | 90.00% | improved=1, regressed=3, tie=2 | reject |
| q041-q046 | rubric-only | compact-distinctive-v27 | 0.960 | 80,168.2 | -88.64% | 6/6 | 1/6 | 79.17% | -8.33 pp | 15/24 | 0/6 | 86.67% | improved=1, regressed=2, tie=3 | reject |
| q047-q052 | rubric+truth | canonical | 0.163 | 447,704.0 | +0.00% | 4/6 | 0/6 | 77.08% | +0.00 pp | 13/24 | 3/6 | 80.56% | baseline | baseline |
| q047-q052 | rubric+truth | chunked-v27 | 0.926 | 79,224.7 | -82.30% | 6/6 | 0/6 | 75.00% | -2.08 pp | 12/24 | 2/6 | 94.44% | improved=2, mixed=1, regressed=3 | reject |

The semantic gate is strict paired non-regression within a cohort. A mixed or regressed case rejects the treatment even when aggregate coverage or efficiency improves. No cross-cohort winner is declared.
