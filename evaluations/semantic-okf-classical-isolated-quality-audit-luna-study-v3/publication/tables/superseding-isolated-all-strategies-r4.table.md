# Superseding isolated Classical answer-quality audit

This append-only retrospective correction supersedes population-review semantic counts. Frozen answer generations were not rerun. Luna judged one answer per call in three criterion orders; majority consensus, calibration controls, complete arm bindings, native Harbor validation, and component-wise comparison were applied.

| Cohort | Contract | Strategy | Native reward | Mean tokens | Token delta | Evidence valid | Full quality | Required coverage | Unanimous cells | Paired vs canonical | Semantic gate | Native fairness |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| q019-q024 | qrel-grounded-rubric | canonical | 0.797 | 632,748.8 | +0.00% | 5/6 | 5/6 | 91.7% | 66.7% | baseline | baseline | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | structural-envelope-v3 | 0.773 | 23,760.3 | -96.24% | 5/6 | 3/6 | 58.3% | 100.0% | regressed=3, tie=3 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | canonical-passage-envelope-v3 | 0.646 | 24,022.8 | -96.20% | 5/6 | 3/6 | 66.7% | 75.0% | regressed=3, tie=3 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | canonical-passage-composer-v4 | 0.969 | 51,273.3 | -91.90% | 6/6 | 3/6 | 75.0% | 83.3% | improved=1, regressed=2, tie=3 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | facet-expanded-passage-v5 | 0.317 | 201,913.5 | -68.09% | 2/6 | 4/6 | 75.0% | 58.3% | improved=1, regressed=1, tie=4 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | dynamic-source-cards-v6 | 0.333 | 56,604.0 | -91.05% | 2/6 | 5/6 | 91.7% | 100.0% | improved=1, regressed=1, tie=4 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | source-deduplicated-cards-v7 | 0.969 | 50,788.8 | -91.97% | 6/6 | 4/6 | 83.3% | 83.3% | improved=1, regressed=1, tie=4 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | acronym-dehyphenated-focus-v8 | 0.648 | 51,524.7 | -91.86% | 4/6 | 5/6 | 91.7% | 100.0% | improved=1, regressed=1, tie=4 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | terminal-passthrough-v9 | 0.805 | 51,889.8 | -91.80% | 5/6 | 4/6 | 83.3% | 100.0% | regressed=1, tie=5 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | concept-path-first-v10 | 0.798 | 52,203.0 | -91.75% | 5/6 | 5/6 | 91.7% | 91.7% | improved=1, regressed=1, tie=4 | reject | lock-and-trial-results |
| q019-q024 | qrel-grounded-rubric | structured-multiline-v11 | 0.959 | 52,121.3 | -91.76% | 6/6 | 5/6 | 91.7% | 83.3% | improved=1, regressed=1, tie=4 | reject | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | canonical | 0.294 | 705,460.8 | +0.00% | 2/6 | 2/6 | 87.5% | 73.3% | baseline | baseline | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | structured-multiline-v11 | 0.677 | 63,660.2 | -90.98% | 5/6 | 1/6 | 60.4% | 76.7% | improved=1, mixed=1, regressed=4 | reject | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | facet-aware-multifocus-v12 | 0.448 | 60,903.7 | -91.37% | 3/6 | 1/6 | 41.7% | 86.7% | improved=1, regressed=5 | reject | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | clause-reserved-v13 | 0.821 | 61,761.5 | -91.25% | 5/6 | 1/6 | 62.5% | 86.7% | improved=1, regressed=4, tie=1 | reject | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | structural-head-backoff-v16 | 0.960 | 83,565.2 | -88.15% | 6/6 | 0/6 | 66.7% | 83.3% | improved=1, regressed=4, tie=1 | reject | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | reference-aware-v18 | 0.960 | 82,489.8 | -88.31% | 6/6 | 0/6 | 56.2% | 76.7% | regressed=6 | reject | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | prose-preferred-anchor-v21 | 0.956 | 78,684.0 | -88.85% | 6/6 | 0/6 | 68.8% | 83.3% | improved=1, regressed=5 | reject | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | overlap-robust-v24 | 0.833 | 78,900.5 | -88.82% | 5/6 | 1/6 | 81.2% | 80.0% | improved=2, regressed=3, tie=1 | reject | lock-and-trial-results |
| q041-q046 | qrel-grounded-rubric | compact-distinctive-v27 | 0.960 | 80,168.2 | -88.64% | 6/6 | 1/6 | 72.9% | 83.3% | improved=2, regressed=3, tie=1 | reject | trial-results-with-documented-environment-wrapper-drift |
| q047-q052 | hard-ground-truth | canonical | 0.163 | 447,704.0 | +0.00% | 4/6 | 0/6 | 83.3% | 94.4% | baseline | baseline | lock-and-trial-results |
| q047-q052 | hard-ground-truth | chunked-v27 | 0.926 | 79,224.7 | -82.30% | 6/6 | 0/6 | 68.8% | 88.9% | mixed=2, regressed=3, tie=1 | reject | lock-and-trial-results |

All cohorts are exposed retrospective evidence. The q047-q052 contract retains hard ground truth but is consumed validation, not a fresh gate. No row is promotion eligible and no cross-cohort winner is declared.
