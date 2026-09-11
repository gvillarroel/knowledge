# Entity Graph traversal adjacency reuse: native EnterpriseRAG outcome

The exact Entity Graph traversal adjacency reuse did not qualify in its original native measurement (AgentTimeoutError). **No qualified EnterpriseRAG retrieval score is assigned.** The original execution record is preserved; the existing family scores stay unchanged.

This measurement uses the frozen exposed development workload: **120 questions,
112 retrieval-eligible questions and 6,000 documents**. Scores below are
frozen-category-weighted nDCG@10 multiplied by 100. They are deterministic
retrieval measurements, not generated-answer quality, official Overall,
public leaderboard positions or the final all-500 comparison.

## Eight-family comparison

The ordered rows contain qualified development measurements. This is the
observed internal retrieval order on the shared exposed subset.

| Position | Family | Weighted nDCG@10 x100 |
| ---: | --- | ---: |
| 1 | Legacy | 72.38 |
| 2 | Turso | 72.08 |
| 3 | Adaptive | 66.21 |
| 4 | Embeddings | 63.51 |
| 5 | Classical | 62.10 |
| 6 | Graphify | 8.12 |

The six previously qualified family scores come from the
[original starting comparison](../starting-terminal-001/README.md).
Any score added here belongs to the exact Entity Graph construction component.
It does not replace the failed original common reference or establish an
accepted composed package. The table does not select or promote a candidate.

## Search coverage for all eight families

| Family | Starting baseline | Best observed development score | Search state |
| --- | ---: | ---: | --- |
| Legacy | 61.11 | 72.38 | Closed; retained history |
| Turso | 45.43 | 72.08 | Open |
| Adaptive | 60.04 | 66.21 | Open |
| Embeddings | 63.51 | 63.51 | Closed; retained history |
| Classical | 55.04 | 62.10 | Closed; retained history |
| Graphify | 8.12 | 8.12 | Open |
| Ensemble | Unavailable | Unavailable | Open; construction unavailable |
| Entity Graph | Unavailable | Unavailable | Open; construction unavailable |

Unavailable measurements remain explicit in this coverage table. Search
closure and package acceptance are separate from the numerical ordering above.

## Exact treatment and outcome

The sealed candidate is
`sha256:37015e173891f7a267b9cd8ffd88567a8f8200dccdea7827180df4e375770f66`.
Its parent is the consumed Entity consultant n-gram eligibility candidate,
`sha256:cdbcc0e33b9ba6235f0ae6d7505826c0ed71768e1497c468bf63a9b0810ed591`.
Only the consultant's `_entity_graph_snapshot.py` changes. A one-entry cache
reuses traversal adjacency under the existing lock, binding weak snapshot
identity and the root/index/core/plan digests. It releases the previous graph
before replacement. Edge order, parallel edges, both self-loop insertions,
traversal arithmetic, evidence, routes and query-cache behavior are preserved.
All 251 other package files, including every builder file, remain unchanged.
The [software and pinned-runtime report](../entity-traversal-adjacency-reuse-001/README.md)
preserves eight checks, 192 exact traversal comparisons, 96 concurrent
comparisons and four complete schema/layout cells. Its separate 1,024-record
runtime replay returned all 48 retained reference responses exactly across
four routes, constructing adjacency once with zero full-query-cache hits.
The profiled query times of 15.727 and 7.785 seconds are sequential software
observations, not a replicated native speedup, a peak-memory estimate or a
retrieval quality gain. The original parent runtime was not repeated.

The task retains both complete builds, independent validation, all four
retrieval routes, fixed resources and zero retries. The original dispatcher,
native artifacts, maintained report and qualification outcome are preserved in
the [source-bound aggregate](aggregate.json). The ordinary organizer stage is
**stopped**, sequence 7; no private data was released.
The maintained reporter's 0.80 display threshold is separate from execution
qualification and the future independent acceptance gate.

The original native job reached `AgentTimeoutError` at the unchanged 3,600-second agent limit. No qualified retrieval score was produced. The original dispatcher exit, maintained report and qualification refusal are preserved. A native summary mean of zero with no scored trials is not a retrieval result and is excluded from the family comparison.

The two complete build logs and both standalone validation logs reported
**pass**, **valid** and zero errors in the snapshot completed at
**2026-09-11T08:36:31.202088+00:00**. Four existing files were copied from the original
trial container. The declared copy arguments, exact original tool observation
and all file digests are preserved in the aggregate. No additional build,
validator, query or native trial was executed for this observation.

These dated phase logs do not establish complete tree equality, phase timings,
later query completion or final qualification. Static inspection of the exact
frozen bridge confirms that it loads one snapshot and retains it in closures
across all modes and questions, so adjacency reuse has an opportunity in the
native execution. That source fact is not a measured native speedup.

Artifact, traversal, query-cache and rejection behavior remain supported by
the software and pinned-runtime fixtures. This single native attempt does not
establish a causal speedup, memory reduction or paired quality gain over a
qualified parent.

See the [application/category breakdown](groups.md) and [cost and time report](cta.md).
Missing quality or usage values stay unavailable. One native trial is not 120
independent execution replications, and the exposed subset overlaps the later
500-question reporting workload.

## Opportunity accounting

| Family | Proposals charged / cap | Remaining within family cap | Historical pending first measurements |
| --- | ---: | ---: | ---: |
| Adaptive | 20 / 100 | 80 | 1 |
| Classical | 37 / 85 | 48 | 0 |
| Embeddings | 6 / 40 | 34 | 0 |
| Ensemble | 2 / 105 | 103 | 0 |
| Entity Graph | 7 / 80 | 73 | 0 |
| Graphify | 0 / 65 | 65 | 0 |
| Legacy | 16 / 55 | 39 | 0 |
| Turso | 2 / 55 | 53 | 1 |

| Family | Completed historical variant attempts | Unavailable originals | Pending first measurement | Subsequent qualification proposals |
| --- | ---: | ---: | ---: | ---: |
| Adaptive | 18 | 1 | 1 | 0 |
| Classical | 36 | 1 | 0 | 0 |
| Embeddings | 6 | 0 | 0 | 0 |
| Ensemble | 0 | 0 | 0 | 2 |
| Entity Graph | 0 | 0 | 0 | 7 |
| Graphify | 0 | 0 | 0 | 0 |
| Legacy | 16 | 0 | 0 | 0 |
| Turso | 1 | 0 | 1 | 0 |

The inherited 81 proposals consist of **77 completed variant attempts, two
permanently unavailable originals and two pending first measurements**.
Completed attempts include execution errors; they are not all qualified
quality measurements. Nine subsequent component proposals bring the total to
90. Baseline measurements are separate from these variant counts.

Legacy stopped after its second catalog round and Classical after its third
round without improvement. Embeddings retained its qualified baseline after
six construction timeouts in its first round. Those timeouts do not establish
six measured quality losses. These are the recorded stops of the declared
catalogs, not proof that every possible future operator has been exhausted.

Adaptive's pending `b=0.25` proposal and Turso's pending `k1=0.6` proposal must
receive their original first measurements before new proposals in those
families. The unavailable Adaptive and Classical originals remain excluded.
Graphify has a qualified fixed-builder baseline but no completed catalog
variants. Entity's seven component proposals and Ensemble's two concern
construction feasibility; they do not close either family's ranking search.
The [historical terminal accounting](../../e8/terminal-001/README.md) and
[catalog coverage](../../e7/strategy-coverage.md) preserve the source context.

The total remains **90 of 585**: 81 inherited proposals, two Ensemble
construction proposals and seven Entity Graph component proposals. This
checkpoint records 1 consumed
first measurement and adds no proposal or evaluable quality miss. Closed unused capacity is not transferable. All
historical closed, pending and unavailable entries remain unchanged; unavailable
originals are never reissued. A mechanism closes after three consecutive unique
evaluable misses, subject to the declared five-round limit.

Five searches remain open. Every remaining construction component must
qualify before the exact composed reference and twelve fresh starting
roles can run. The
remaining work then includes pending Adaptive and Turso measurements, the five
catalogs, joint replay, exact bundle freeze, paired all-500 evaluation and the
reserved independent whole-bundle acceptance gate. Canonical skills remain
unchanged; the overall improvement task is incomplete.

[E11 overview](../README.md) · [Family report index](../../../../../docs/enterprise-family-report-index.md)
