# Entity Graph: exact n-gram eligibility optimization

The isolated builder candidate passed **seven software checks** and a new
**1,024-record JSON runtime cell**, preserving every file in the retained
reference snapshot. It changes one function and freezes the entire consultant.
**Complete EnterpriseRAG qualification and a new retrieval score remain pending.**

## Change and correctness

The builder now counts disallowed tokens once per section. Each overlapping
n-gram checks its prefix-count boundaries before allocating a token tuple.
Excluded aliases, valid-window order, counts, frequencies, floating-point scores,
rounding and both local and global tie ordering remain unchanged.

The candidate passed 4,080 exact comparisons against both its parent and an
independent occurrence-counting oracle; 1,306 comparisons were nonempty. The
matrix covers both plan schemas, all 15 ordered n-gram ranges from 1 through 5,
four token-length thresholds and 34 public corpora. Two hand-counted tests
cover interrupted/excluded phrases and a lexical tie. These cases are software
coverage, not 4,080 independent benchmark tasks.

Four complete schema/layout cells passed 192 child commands: 16 builds,
16 independent validations, 32 nonempty paired query responses, eight deep
consultant inspections, 40 builder and 40 consultant corruption rejections,
and eight existing-output rejections. Exact artifacts and unchanged source
packages were checked. [Contract coverage](groups.md).

On one declared operation-count cell, stopword membership calls fell from
28,704 to 1,968 for the same 1,968 tokens, with equal output. This proves the
intended redundant checks were removed; it is not a native speedup estimate.

## Pinned runtime

| Operation | Elapsed seconds | Extraction seconds | Extraction calls |
| --- | ---: | ---: | ---: |
| build | 38.638 | 8.908 | 3 |
| validate | 11.456 | 2.962 | 1 |
| consult-deep | 9.205 | 4.263 | 1 |

The new candidate alone ran against the exact existing 1,024-record synthetic
JSON input, with 8,192-character bodies, a 12,000-character section cap and
1,200-candidate cap. Construction, independent validation and deep consultation
passed in Python 3.12.13 with the pinned image, 2 CPU and 6 GiB. All 19 output
files match the [retained reference](../entity-json-scaling-001/README.md).
The parent was not reexecuted. These are single observations with cProfile
overhead; nested function times must not be summed and the historical timings
do not establish a paired speedup. [CTA](cta.md).

## Retained EnterpriseRAG comparison

| Family | Retained nDCG@10 × 100 | Proposals / cap | Search |
| --- | ---: | ---: | --- |
| adaptive | 66.21 | 20 / 100 | Open |
| classical | 62.10 | 37 / 85 | Closed |
| embeddings | 63.51 | 6 / 40 | Closed |
| ensemble | Unavailable | 2 / 105 | Open |
| entity-graph | Unavailable | 4 / 80 | Open |
| graphify | 8.12 | 0 / 65 | Open |
| legacy | 72.38 | 16 / 55 | Closed |
| turso | 72.08 | 2 / 55 | Open |

The unchanged scores use 120 development questions, 112 retrieval-eligible
questions and 6,000 documents. They are frozen-category-weighted deterministic
retrieval results, separate from Luna answer quality, official Overall or a
public leaderboard rank. Three family searches are closed and five remain open.

This proposal increases cumulative claims from 86 to **87 of 585**, including
**4 of Entity's 80**. All five prior native first measurements stay consumed;
this candidate's exclusive first measurement remains unassigned. The two
historical pending measurements and every family stopping rule are preserved.
See the [accounting and treatment decision](../../../../../.specs/adr/0144-reuse-token-eligibility-in-entity-candidate-extraction.md).

The exact candidate is `sha256:1805605cb708f5e37f9f035fcc2eac397f3500d173ea34cf327433511e1e5df7`; its parent is
`sha256:15d7fd9ffc0e83a1585a901bf6a2ee8133d2c58407130e3c0918cb7acdf39cbc`. The other 251 package files are unchanged.
No canonical skill is promoted. Complete construction qualification, the
remaining catalogs, composed reference, paired all-500 comparison and one-way
independent whole-bundle acceptance remain unfinished.

[Aggregate](aggregate.json) · [CTA](cta.md) · [Groups](groups.md) · [E11](../README.md)
