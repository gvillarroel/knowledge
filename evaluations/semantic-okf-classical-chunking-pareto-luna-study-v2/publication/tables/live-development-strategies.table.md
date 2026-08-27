# Live development strategy results

These are complete six-case Harbor jobs. Results are grouped by cohort and
must be compared only within the same cohort. This table preserves the original
mechanical results and the limited semantic reviews available at the time. Its
`Blind regressions` column is historical and is superseded by
`complete-solution-agnostic-all-strategies-r1.table.md`, which reviews every
completed strategy with one counterbalanced, solution-agnostic protocol.

## q019-q024, Pi 0.84.2, GPT-5.6 Luna

| Strategy | Mean reward | Mean tokens | Exact passes | Evidence-valid cases | Blind regressions | Observed failure or outcome |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Canonical classical baseline | 0.796817 | 632,748.8 | 2/6 | 5/6 | baseline | Unbounded source consultation remained expensive |
| Structural envelope v3 | 0.773143 | 23,760.3 | 2/6 | 5/6 | - | Very small payload, but omitted required material in one comparison |
| Canonical-passage envelope v3 | 0.645986 | 24,022.8 | 2/6 | 5/6 | - | Passage copying did not preserve the full evidence contract |
| Canonical-passage composer v4 | 0.969319 | 51,273.3 | 3/6 | 6/6 | 4/6 | Mechanically strong but semantically regressive |
| Facet-expanded passage composer v5 | 0.316819 | 201,913.5 | 1/6 | 2/6 | - | Expansion increased cost and damaged qualification |
| Dynamic source cards v6 | 0.333333 | 56,604.0 | 2/6 | 2/6 | - | Only two answers retained valid evidence |
| Source-deduplicated cards v7 | 0.969167 | 50,788.8 | 3/6 | 6/6 | 2/6 | Best early semantic trade-off, but still regressive |
| Acronym and dehyphenation focus v8 | 0.647917 | 51,524.7 | 2/6 | 4/6 | - | Normalization introduced evidence failures |
| Terminal pass-through v9 | 0.804583 | 51,889.8 | 2/6 | 5/6 | - | Reduced transcription risk but did not restore full validity |
| Concept-path-first v10 | 0.798333 | 52,203.0 | 2/6 | 5/6 | - | Path preference did not improve the mechanical frontier |
| Structured multiline terminal v11 | 0.958750 | 52,121.3 | 2/6 | 6/6 | 0/6 development | Passed this cohort, then failed fresh validation with 4/6 regressions |

## q041-q046 repair development, Pi 0.84.2, GPT-5.6 Luna

| Strategy | Mean reward | Mean tokens | Exact passes | Evidence-valid cases | Blind regressions | Observed failure or outcome |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Canonical classical baseline | 0.293824 | 705,460.8 | 1/6 | 2/6 | baseline | High cost and poor mechanical completion on this cohort |
| v11 frozen predecessor | 0.677068 | 63,660.2 | 1/6 | 5/6 | 4/6 | Fresh-cohort semantic rejection |
| Facet-aware multifocus v12 | 0.448143 | 60,903.7 | 1/6 | 3/6 | - | Facet diversity alone damaged evidence qualification |
| Clause-reserved five-source v13 | 0.820986 | 61,761.5 | 4/6 | 5/6 | - | Broader source reservation helped but remained incomplete |
| Structural head backoff v16 | 0.959671 | 83,565.2 | 5/6 | 6/6 | 4/6 | Mechanical repair did not prevent semantic defects |
| Reference-aware five-focus v18 | 0.959671 | 82,489.8 | 5/6 | 6/6 | 3/6 | Removed reference noise; metric and limitation defects remained |
| Prose-preferred anchor v21 | 0.955505 | 78,684.0 | 5/6 | 6/6 | 2/6 | Better prose selection; two source-local omissions remained |
| Overlap-robust role reservation v24 | 0.833333 | 78,900.5 | 5/6 | 5/6 | 1/6 | One manual digest-transcription defect invalidated a case |
| Compact terminal plus distinctive-facet v27 | 0.959671 | 80,168.2 | 5/6 | 6/6 | 0/6 development | Selected for the one-way independent validation gate |
