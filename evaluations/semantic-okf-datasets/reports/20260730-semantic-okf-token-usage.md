# Semantic OKF two-stage token usage

This report covers **all eight registered build/consult strategy pairs**. Its primary matrix contains **16 newly submitted, qualified builder-direct trials** and reused **48 existing same-question consult-only calls**. Construction and consultation remain separate units.

## Results at a glance

- Lowest construction cost: **Classical**, 5,734.50 tokens per folder.
- Highest construction cost: **Graphify**, 9,836.00 tokens per folder.
- Lowest observed submitted-query cost: **Graphify**, 325,279.00 tokens, with 6/6 runtime errors.
- Highest observed submitted-query cost: **Entity Graph**, 2,433,148.67 tokens, with 3/6 runtime errors.

Among strategies with zero runtime errors, **Legacy** used the least (1,585,536.83) and **Turso** used the most (2,109,545.83) per submitted query.

Harbor input already includes cached input. Total is input plus output; cache is displayed separately and is never added twice.

## Knowledge-folder construction: all registered strategies

Contract: `graphrag-papers-40`, `openai-codex/gpt-5.3-codex-spark`, Pi `0.73.1`, `high` thinking. Each strategy has two independent builder calls and two validated folders. Combined build-and-consult trials are excluded.

| Rank (low→high) | Strategy | Calls | Folders | Qualified | Mean input/folder | Mean cache/folder | Mean output/folder | Mean total/folder |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Classical | 2 | 2 | 2/2 | 4,686.50 | 2,112.00 | 1,048.00 | 5,734.50 |
| 2 | Entity Graph | 2 | 2 | 2/2 | 5,002.50 | 2,240.00 | 1,296.50 | 6,299.00 |
| 3 | Embeddings | 2 | 2 | 2/2 | 5,625.00 | 2,496.00 | 918.00 | 6,543.00 |
| 4 | Adaptive | 2 | 2 | 2/2 | 5,816.00 | 3,264.00 | 1,066.00 | 6,882.00 |
| 5 | Legacy | 2 | 2 | 2/2 | 5,859.00 | 3,264.00 | 1,144.50 | 7,003.50 |
| 6 | Ensemble | 2 | 2 | 2/2 | 5,991.00 | 1,856.00 | 1,300.00 | 7,291.00 |
| 7 | Turso | 2 | 2 | 2/2 | 7,327.50 | 3,776.00 | 1,229.50 | 8,557.00 |
| 8 | Graphify | 2 | 2 | 2/2 | 8,009.00 | 4,352.00 | 1,827.00 | 9,836.00 |

Construction rank is based on mean total tokens per generated folder. Every primary row passed artifact integrity, record identity, independent validation, cross-replicate inventory identity, command coverage, and workflow-safety gates.

## Consultation: all registered strategies

Contract: `graphrag-papers-40` `holdout` questions q005, q010, q015, q020, q025, q029; `openai-codex/gpt-5.3-codex-spark`, Pi `0.73.1`, `high` thinking. Every strategy received the same six questions. Failed attempts remain in the denominator because they consumed tokens.

| Rank (low→high) | Strategy | Queries | Runtime errors | Complete | Mean input | Mean cache | Mean output | Mean total/submitted query | Mean total/complete response |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Graphify | 6 | 6 | 0 | 321,910.33 | 284,757.33 | 3,368.67 | 325,279.00 | — |
| 2 | Ensemble | 6 | 6 | 0 | 1,075,284.17 | 969,834.67 | 24,215.33 | 1,099,499.50 | — |
| 3 | Embeddings | 6 | 1 | 5 | 1,381,168.17 | 1,231,957.33 | 15,976.17 | 1,397,144.33 | 1,517,508.60 |
| 4 | Classical | 6 | 1 | 5 | 1,521,469.83 | 1,407,530.67 | 17,535.50 | 1,539,005.33 | 1,419,480.80 |
| 5 | Legacy | 6 | 0 | 6 | 1,573,616.17 | 1,448,832.00 | 11,920.67 | 1,585,536.83 | 1,585,536.83 |
| 6 | Adaptive | 6 | 2 | 4 | 1,856,426.33 | 1,755,605.33 | 15,218.33 | 1,871,644.67 | 1,612,571.75 |
| 7 | Turso | 6 | 0 | 6 | 2,083,327.00 | 1,960,640.00 | 26,218.83 | 2,109,545.83 | 2,109,545.83 |
| 8 | Entity Graph | 6 | 3 | 3 | 2,411,379.00 | 2,289,301.33 | 21,769.67 | 2,433,148.67 | 1,614,260.00 |

Graphify and Ensemble are the two lowest observed submitted costs, but both are 0/6 complete. They are cheap because the runtime stopped early, not because they delivered efficient answers. Complete-response means are diagnostic because strategies with failures completed different question subsets. The zero-error comparison contains Legacy and Turso.

## All deterministic direct-retrieval routes

All 25 registered direct-retrieval helpers use **0 LLM tokens per retrieval invocation**. This unit covers only deterministic retrieval; it excludes a later answer-generation agent.

| Strategy | LLM calls/retrieval | LLM tokens/retrieval |
|---|---:|---:|
| Classical association | 0 | 0 |
| Classical fusion | 0 | 0 |
| Adaptive fusion | 0 | 0 |
| Ensemble `robust` | 0 | 0 |
| Classical topic | 0 | 0 |
| Specialized expert early confidence-gated hybrid | 0 | 0 |
| RustMallet association | 0 | 0 |
| RustMallet fusion | 0 | 0 |
| RustMallet topic | 0 | 0 |
| RustMallet BM25 | 0 | 0 |
| Classical BM25 | 0 | 0 |
| Ensemble `fast` | 0 | 0 |
| Specialized expert Ensemble quality + trace v48 | 0 | 0 |
| Tantivy BM25 | 0 | 0 |
| Entity Graph lexical | 0 | 0 |
| Embeddings lexical | 0 | 0 |
| Tika/MALLET fusion | 0 | 0 |
| Entity Graph fusion | 0 | 0 |
| Entity Graph entity | 0 | 0 |
| Entity Graph traversal | 0 | 0 |
| Tika/MALLET/Tantivy fusion | 0 | 0 |
| Embeddings hybrid | 0 | 0 |
| Legacy lexical | 0 | 0 |
| Embeddings vector | 0 | 0 |
| Specialized expert supervised profiles v51 | 0 | 0 |

## Historical builder diagnostics

These earlier builder-direct rows use `openrouter/openai/gpt-5.4-mini` and are retained for audit. They are not mixed into the primary eight-family ranking.

| Methodology | Strict | Trials | Folders | Mean total/folder |
|---|---|---:|---:|---:|
| Classical direct builder | no | 2 | 4 | 74,573.25 |
| Tika/MALLET v46 qualified-runtime builder | yes | 6 | 12 | 111,307.67 |

## Historical controlled consultation pilot

The earlier baseline/evolved pilot remains available as a separate diagnostic and is not the primary registered-family ranking.

| Methodology | Generation | Queries | Errors | Mean total/query |
|---|---|---:|---:|---:|
| legacy | baseline | 3 | 0 | 1,282,298.00 |
| legacy | evolved | 3 | 0 | 825,345.00 |
| embeddings | baseline | 3 | 0 | 437,009.33 |
| embeddings | evolved | 3 | 0 | 342,679.00 |
| classical | baseline | 3 | 0 | 890,187.00 |
| classical | evolved | 3 | 0 | 395,095.67 |
| adaptive | baseline | 3 | 0 | 1,379,051.33 |
| adaptive | evolved | 3 | 0 | 336,834.33 |
| entity-graph | baseline | 3 | 1 | 1,387,746.67 |
| entity-graph | evolved | 3 | 0 | 997,847.67 |
| ensemble | baseline | 3 | 1 | 386,471.67 |
| ensemble | evolved | 3 | 0 | 586,646.33 |

## Uneven GraphRAG archive diagnostic

The current artifact archive has 209 answer-emitting trials with complete usage. Coverage is uneven, so these rows are not a methodology ranking. Models remain separate.

| Strategy | Model | Complete responses | Mean input | Mean cache | Mean output | Mean total/response |
|---|---|---:|---:|---:|---:|---:|
| adaptive | `openai-codex/gpt-5.3-codex-spark` | 5 | 1,960,390.60 | 1,865,472.00 | 19,960.00 | 1,980,350.60 |
| classical | `openai-codex/gpt-5.3-codex-spark` | 6 | 1,921,402.00 | 1,807,680.00 | 19,208.33 | 1,940,610.33 |
| embeddings | `openai-codex/gpt-5.3-codex-spark` | 4 | 1,388,172.25 | 1,258,560.00 | 20,614.50 | 1,408,786.75 |
| entity-graph | `openai-codex/gpt-5.3-codex-spark` | 4 | 2,368,480.75 | 2,222,016.00 | 24,147.75 | 2,392,628.50 |
| legacy | `openai-codex/gpt-5.3-codex-spark` | 7 | 2,079,186.57 | 1,954,560.00 | 24,986.14 | 2,104,172.71 |
| tika-mallet-canonical-text | `openai-codex/gpt-5.3-codex-spark` | 2 | 1,407,214.00 | 1,286,464.00 | 21,404.50 | 1,428,618.50 |
| tika-mallet-canonical-text-v2 | `openai-codex/gpt-5.3-codex-spark` | 5 | 1,183,403.60 | 1,080,089.60 | 29,363.20 | 1,212,766.80 |
| tika-mallet-canonical-text-v3 | `openai-codex/gpt-5.3-codex-spark` | 29 | 660,636.72 | 605,175.17 | 13,117.90 | 673,754.62 |
| tika-mallet-tantivy-canonical-text | `github-copilot/gpt-5.4` | 3 | 1,315,750.00 | 1,208,149.33 | 18,368.00 | 1,334,118.00 |
| tika-mallet-tantivy-canonical-text | `openrouter/google/gemini-2.5-flash` | 17 | 468,930.71 | 231,778.71 | 25,168.94 | 494,099.65 |
| tika-mallet-tantivy-canonical-text | `openrouter/openai/gpt-5.4-mini` | 121 | 280,809.01 | 246,094.28 | 14,610.61 | 295,419.62 |
| turso | `openai-codex/gpt-5.3-codex-spark` | 6 | 2,083,327.00 | 1,960,640.00 | 26,218.83 | 2,109,545.83 |

## Limitations

- Each registered family has two independent single-folder builder calls. Their same-environment folder inventories must be byte-identical, and the per-folder mean has no cross-folder orchestration amortization.
- The consultation ranking measures submitted-query cost. Graphify and Ensemble look inexpensive only because all six of their common trials ended in runtime errors; use the separate zero-error comparison for an operational choice.
- The common consultation matrix is a legacy Harbor campaign with equal tasks, model, Pi version, and thinking level, but it predates the immutable runtime input-binding v2 contract.
- Construction and consultation are different causal stages and remain separate rankings even though their primary rows use the same model and corpus.
- Token rank does not measure wall-clock latency, CPU, memory, storage, or provider price. Script-heavy builders can use few agent tokens while performing substantial local computation.
- The 25 direct-retrieval routes make no LLM call themselves. Their zero-token unit excludes any later grounded answer generation and must not be substituted for consultant cost.
- Two stopped builder rehearsals are excluded from the primary matrix: one amortized two folders inside a call and timed out on Embeddings; the next compared output bytes against a snapshot produced in a different environment. Their partial or non-comparable costs are not strategy means.
- Historical builder and consultation tables use other contracts or uneven archives and remain supplemental rather than part of the eight-family primary ranking.
