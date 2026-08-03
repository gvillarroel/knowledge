# Dense paper overview v28 final result

Decision: **not promoted**.

| Cohort | Cases | Classical mean tokens | v28 mean tokens | Change | Automatic quality regressions | Manual semantic completion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Development | 6 | 1,631,368.5 | 15,730.3 | -99.04% | 0 | Not independently audited |
| Untouched holdout | 4 | 1,162,797.5 | 16,470.0 | -98.58% | 0 | 2/4 |

The strict mechanical gate passed and every holdout case used fewer tokens. A post-gate review of each isolated task nevertheless found two incomplete multi-part answers. The single query-dense section could omit a distant requested dimension even when the selected paper and evidence locator were correct. v28 remains positive token-efficiency evidence, but it is not a semantic non-regression promotion.
