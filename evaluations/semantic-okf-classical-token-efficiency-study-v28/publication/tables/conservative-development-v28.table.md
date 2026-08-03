| Treatment | Cases | Total native tokens | Mean native tokens | Median native tokens | Mean change vs canonical | Numeric regressions | Cases with numeric regression | Cases with semantic regression | Accepted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Frozen canonical Classical | 6 | 6,015,810 | 1,002,635.0 | 779,410.0 | baseline | 0 | 0 | 0 | Control only |
| Exact V20 | 6 | 130,674 | 21,779.0 | 17,307.0 | -97.8278% | 16 | 2 | 4 | No |
| Exact V21 | 6 | 110,526 | 18,421.0 | 17,189.5 | -98.1627% | 23 | 3 | 5 | No |
| Preferred-margin v2 | 6 | 99,338 | 16,556.3 | 16,042.0 | -98.3487% | 19 | 3 | 3 | No |

Native tokens are provider-reported input plus output tokens; cache input is already a subset of input and is not added again. Every candidate completed 6/6 cases without errors or observed retries and was cheaper in every paired case. Acceptance is nevertheless fail-closed: every candidate had both paired numeric and independently reviewed semantic regressions, so no development winner was frozen and validation and holdout remained sealed.
