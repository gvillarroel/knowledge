# E7 final runtime readiness audit

These are conditional runtime estimates from six completed development jobs. They are not all-500 measurements, failures, quality scores or permission to change frozen execution inputs. The native pipeline continues unchanged. No native job, candidate or private gate was dispatched by this audit.

| Family | Configuration | Measured 120-query agent minutes | Weighted 500-query estimate minutes | Fastest-observed-query scenario minutes | Declared agent limit minutes |
| --- | --- | ---: | ---: | ---: | ---: |
| legacy | baseline | 1.24 | 1.54 | 1.31 | 60.00 |
| legacy | candidate-009 | 1.36 | 1.84 | 1.46 | 60.00 |
| embeddings | baseline | 17.27 | 40.06 | 37.07 | 60.00 |
| classical | baseline | 26.50 | 75.84 | 68.56 | 60.00 |
| classical | candidate-007 | 26.21 | 74.40 | 66.63 | 60.00 |
| adaptive | baseline | 22.33 | 57.54 | 26.93 | 60.00 |

The eight final task descriptors declare a 3,600-second agent limit, and the exact native adapter also passes 3,600 seconds to environment.exec. The final job template has no explicit timeout override. This audit checks all eight final family descriptors and the adapter; it does not resolve unstarted jobs through a new Harbor launch.

Every query is included in timing, including the eight development queries with no relevance references. Original category weights sum to 500 for all queries. Multiply each recorded query time by its frozen population-to-sample weight, sum all declared routes, and add the original double-build time and remaining measured agent overhead. The original query P95 values, exact route/query coverage and native qualification were checked before projecting.

Classical is projected to exceed the declared limit even for its unchanged baseline. This is a readiness concern, not an observed all-500 execution failure. Estimates for unfinished families or future selections are unavailable. Faster hardware, changed contention or different query costs could change actual runtime; these estimates have no confidence interval or causal claim.

If the original final stage actually fails its budget, preserve that terminal evidence and do not silently extend the deadline, retry a semantic outcome, omit a route or release the private gate. A necessary follow-up must use a separately registered and reviewed execution contract, preserve the frozen selection without retrospective reselection, and satisfy the maintained organizer validation boundary. No such follow-up study is initialized by this audit.

[Exact estimates, route and category contributions, assumptions and hashes](aggregate.json) · [Campaign](../README.md)
