# Turso generated expert: verified delivery boundary

**Changing only the generator's experimental Turso retrieval profile does not change the portable expert it produces.** Two real generation runs created byte-identical forty-file experts, including their complete knowledge trees. Their default query payloads were also identical. This confirms an installation boundary; it is not a failed EnterpriseRAG trial or a new retrieval score.

## Exact controlled generation

One run used the frozen E7 generator unchanged. The other used an isolated copy of its 252-file package, changing only `assets/retrieval-profile.json`: Turso search became `{"engine":"bm25","k1":1.2}`. This is the first declared BM25 setting, used here as a synthetic input-handling probe. It was not submitted to Harbor, ranked, retained, installed or added to the evolution history.

Both runs used the same twelve synthetic Markdown documents, source manifest, reviewed guidance, family, expert name and physical layout. Each passed the actual generator runtime smoke, native construction, independent deep validation, deterministic `--check` rebuild, generated runtime smoke, generated deep verification and skill package validation. Neither expert embeds the experimental profile or its helper.

For three queries per expert, removing only the generated citation and expert metadata recovered the exact native Turso CLI payload. Every returned citation resolved, and representative exact-record `get` calls returned the ledger body unchanged. All forty files in each expert remained unchanged by consultation.

## Three distinct consultation contracts

| Contract | Match and order |
| --- | --- |
| Generated Turso expert, default `records` mode | Native `records --contains`: whole query substring in title, body or canonical record JSON; ordered by concept ID |
| E7 Turso empty-profile `lexical-sql` route | Parameterized SQL: one presence point per query-token substring in title/body; ordered by score, then record ID |
| E7 Turso nonempty-profile `lexical-sql` route | Canonical database rows loaded once; exact-token BM25 in memory; ordered by score, then record ID |

| Synthetic query | Generated default results | E7 SQL results | E7 BM25 results | Generated order equals SQL | Generated order equals BM25 |
| --- | ---: | ---: | ---: | --- | --- |
| `quasar` | 10 | 10 | 9 | True | False |
| `photon` | 9 | 9 | 8 | True | False |
| `quasar photon` | 4 | 10 | 10 | False | False |

For `quasar photon`, the generated expert requires the complete phrase as a substring and returns four documents, whereas both E7 comparators return ten. Across these three controlled queries, the generated default differs from E7 SQL once and from E7 BM25 three times. These are mechanical set/order comparisons, not relevance judgments or estimates of an EnterpriseRAG score difference.

## Consequence for accepted delivery

The E7 bridge measures the explicit wrapper routes, and its source instructions describe applying that wrapper profile. If the joint bundle is accepted, an exact-package installation can deliver that experimental recipe with its measured scope. Such installation does not by itself make every generated expert inherit the wrapper behavior. The final report and any installation receipt must keep those claims separate.

Automatic profile inheritance would require a separately realized and tested integration, including native payloads, authoritative identities, physical citations, read-only behavior and matched route settings. It would change the evaluated package digest and cannot be described as the exact E7 package. No such integration, new study or promotion is performed by this audit. The empirical result here concerns Turso; portable Legacy and Graphify behavior requires its own parity evidence.

All inputs were synthetic and local. No benchmark query content, qrel, private validation or language model was used. The frozen generator, the original study inputs and the canonical repository skills were unchanged. Turso still requires its own original native Enterprise baseline and development search.

[Aggregate and evidence bindings](aggregate.json) · [Turso database and ranking audit](../turso-opportunity-001/README.md) · [Campaign](../README.md)
