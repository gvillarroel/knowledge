# Classical consultation token-efficiency study v4

Native tokens are input plus output tokens; reported cache tokens are already a subset of input tokens. Development contains six isolated tasks (q019-q024), and holdout contains six disjoint isolated tasks (q025-q030). The frozen automatic gate required zero quality regressions, a lower median, an acceptable mean, and strict token reduction in at least five of six cases. Manual review compared every answer with its paired baseline answer.

## Development search

| Treatment | Mean tokens | Change vs. v28 | Median tokens | Cases reduced | Automatic result | Manual finding | Decision |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| v28 baseline | 16,670.5 | — | 14,763.5 | — | 6/6 mechanically valid | 3/6 complete under the strict semantic rubric | Baseline |
| v31 query-focused dual evidence | 17,641.0 | +5.82% | 16,316.0 | 2/6 | Quality regressions | 1/6 complete | Reject |
| v32 minimum-plus-two pool | 13,978.5 | -16.15% | 14,269.0 | 4/6 | Quality regression on q020 | 3/6 complete | Reject |
| v33 rank-budgeted paper-wide | 14,845.5 | -10.95% | 14,637.5 | 4/6 | Zero quality regressions, but token-count gate failed | 4/6 complete | Reject |
| v34 compact guardrailed guidance | 13,214.8 | -20.73% | 11,599.0 | 5/6 | Pass; zero quality regressions | 0/6 pairwise regressions; 5/6 absolutely complete | Select for holdout |
| v35 explicit own-method comparator | 9,985 on q022 only | -32.96% on probe | — | — | Probe mechanically valid | Remaining q022 role distinction still omitted | Reject before full cohort |
| v36 explicit role sentence | 30,539 on q022 only | +105.04% on probe | — | — | Mechanical verifier accepted semantically empty text | Summary and claims were one-character placeholders | Reject before full cohort |

## Untouched holdout decision

| Candidate | Mean tokens | Change | Median tokens | Median change | Cases reduced | Mechanical quality regressions | Manual semantic regressions | Frozen result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v28 baseline | 23,614.8 | — | 13,168.5 | — | — | 0 | — | Baseline |
| v34 compact guardrailed guidance | 21,499.8 | -8.96% | 11,305.5 | -14.15% | 4/6 | 0 | 0/6 | Reject: required at least 5/6 reductions |

v34 preserved answer quality in all six holdout pairs but was not promoted. Its q027 trajectory spent 72,473 tokens after exploring the skill and implementation before the bounded query. The baseline showed the same failure mode on q030 (67,202 tokens). The next independent treatment should preload consultation instructions and expose only dedicated query and submission tools; it requires a new one-way study and a new holdout.
