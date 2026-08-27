# Isolated review methodology and result correction

The same frozen answer generations were measured in every row. Coverage changes below are evaluator corrections, not changes to the generated answers. All non-canonical semantic gates remain rejected.

| Version | Scope | Calibration | Disposition | Methodological finding |
| --- | --- | ---: | --- | --- |
| R1 | q047-q052 preflight | incomplete | abandoned | Two outputs were incomplete after a schema-validation failure; invalid attempts were not preserved. |
| R2 | q047-q052 | 9/12 | rejected | Positive controls covered summarized truth claims but not every rubric component. |
| R3 | q047-q052 and q019-q024 | 12/12 hard-truth controls | superseded | A model-authored packet digest typo exhausted the attempt cap, showing that digest transcription was not a semantic gate. |
| R4 | all cohorts | 24/24 | superseded | Runner binding became authoritative, but malformed diagnostic echoes could still trigger retries. |
| R5 | all cohorts | 24/24 | accepted retrospective audit | Runner-owned binding, diagnostic-only digest echo, complete arm validation, isolated three-pass majority, and component-wise comparison. |

| Cohort | Strategy | Old coverage | R5 coverage | Delta | Old paired result | R5 paired result |
| --- | --- | ---: | ---: | ---: | --- | --- |
| q019-q024 | canonical | 83.33% | 91.67% | +8.33 pp | baseline | baseline |
| q019-q024 | structural-envelope-v3 | 58.33% | 58.33% | 0.00 pp | regressed=2, tie=4 | regressed=3, tie=3 |
| q019-q024 | canonical-passage-envelope-v3 | 66.67% | 66.67% | 0.00 pp | regressed=1, tie=5 | regressed=3, tie=3 |
| q019-q024 | canonical-passage-composer-v4 | 75.00% | 75.00% | 0.00 pp | regressed=1, tie=5 | improved=1, regressed=2, tie=3 |
| q019-q024 | facet-expanded-passage-v5 | 75.00% | 75.00% | 0.00 pp | improved=1, regressed=1, tie=4 | improved=1, regressed=1, tie=4 |
| q019-q024 | dynamic-source-cards-v6 | 91.67% | 91.67% | 0.00 pp | improved=1, regressed=1, tie=4 | improved=1, regressed=1, tie=4 |
| q019-q024 | source-deduplicated-cards-v7 | 83.33% | 83.33% | 0.00 pp | improved=1, regressed=1, tie=4 | improved=1, regressed=1, tie=4 |
| q019-q024 | acronym-dehyphenated-focus-v8 | 91.67% | 91.67% | 0.00 pp | improved=1, regressed=1, tie=4 | improved=1, regressed=1, tie=4 |
| q019-q024 | terminal-passthrough-v9 | 83.33% | 83.33% | 0.00 pp | improved=1, regressed=1, tie=4 | regressed=1, tie=5 |
| q019-q024 | concept-path-first-v10 | 91.67% | 91.67% | 0.00 pp | improved=1, regressed=1, tie=4 | improved=1, regressed=1, tie=4 |
| q019-q024 | structured-multiline-v11 | 91.67% | 91.67% | 0.00 pp | improved=1, regressed=1, tie=4 | improved=1, regressed=1, tie=4 |
| q041-q046 | canonical | 87.50% | 87.50% | 0.00 pp | baseline | baseline |
| q041-q046 | structured-multiline-v11 | 56.25% | 60.42% | +4.17 pp | improved=1, regressed=5 | improved=1, mixed=1, regressed=4 |
| q041-q046 | facet-aware-multifocus-v12 | 45.83% | 41.67% | -4.17 pp | improved=1, regressed=3, tie=2 | improved=1, regressed=5 |
| q041-q046 | clause-reserved-v13 | 60.42% | 62.50% | +2.08 pp | improved=1, regressed=3, tie=2 | improved=1, regressed=4, tie=1 |
| q041-q046 | structural-head-backoff-v16 | 70.83% | 66.67% | -4.17 pp | regressed=4, tie=2 | improved=1, regressed=4, tie=1 |
| q041-q046 | reference-aware-v18 | 64.58% | 56.25% | -8.33 pp | regressed=4, tie=2 | regressed=6 |
| q041-q046 | prose-preferred-anchor-v21 | 70.83% | 68.75% | -2.08 pp | regressed=4, tie=2 | improved=1, regressed=5 |
| q041-q046 | overlap-robust-v24 | 79.17% | 81.25% | +2.08 pp | improved=1, regressed=3, tie=2 | improved=2, regressed=3, tie=1 |
| q041-q046 | compact-distinctive-v27 | 79.17% | 72.92% | -6.25 pp | improved=1, regressed=2, tie=3 | improved=2, regressed=3, tie=1 |
| q047-q052 | canonical | 77.08% | 83.33% | +6.25 pp | baseline | baseline |
| q047-q052 | chunked-v27 | 75.00% | 68.75% | -6.25 pp | improved=2, mixed=1, regressed=3 | mixed=2, regressed=3, tie=1 |

No cross-cohort ranking is valid. Q019-q024 and q041-q046 are qrel-grounded rubric audits; q047-q052 has hard ground truth but is consumed validation. No row is promotion eligible.
