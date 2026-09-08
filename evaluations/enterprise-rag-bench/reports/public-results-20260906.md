# EnterpriseRAG-Bench public results reference

Checked: 2026-09-06. Official Space revision last updated: 2026-08-28.

This is an external published-results reference. No system was rerun for this note. The official 500-question answer-quality contract and this repository's reduced retrieval experiment remain separate.

## Official public leaderboard

| Pos. | Pair / strategy | Overall | Correctness | Completeness | Document recall | Invalid extra docs |
|---:|---|---:|---:|---:|---:|---:|
| 1 | metor.com | 80.34 | 82.00% | 86.22% | 85.53% | 4.96 |
| 2 | CDL (Causal Dynamics Lab) | 78.95 | 82.00% | 85.16% | 80.54% | 14.08 |
| 3 | Troml | 76.79 | 83.80% | 81.84% | 86.55% | 12.65 |
| 4 | Skyller | 71.93 | 77.00% | 79.14% | 81.60% | 8.86 |
| 5 | OpenClaw | 68.22 | 81.60% | 72.86% | 79.02% | 0.47 |
| 6 | SovraRAG.ch | 65.61 | 74.60% | 72.37% | 78.80% | 8.87 |
| 7 | fgroo | 63.27 | 71.00% | 71.03% | 72.50% | 0.63 |
| 8 | OpenAI File Search | 61.03 | 69.80% | 67.87% | 71.65% | 15.70 |
| 9 | Bash Agent (GPT-5.4) + GPT-5.4 | 52.63 | 60.60% | 61.12% | 55.76% | 2.00 |
| 10 | BM25 + GPT-5.4 | 50.60 | 68.80% | 55.95% | 68.41% | 9.01 |
| 11 | RAGFlow | 50.24 | 56.00% | 58.74% | 63.05% | 4.61 |
| 12 | Amazon Q (Kendra) | 48.96 | 55.40% | 60.65% | 70.38% | 1.49 |
| 13 | Azure AI Search | 48.42 | 56.40% | 57.63% | 64.25% | 3.25 |
| 14 | hRAG | 44.74 | 52.60% | 54.38% | 69.65% | 9.01 |
| 15 | CortexDB-KZ | 42.04 | 47.40% | 49.21% | 56.24% | 9.20 |
| 16 | Vertex AI Search | 41.87 | 49.20% | 55.45% | 61.76% | 4.05 |
| 17 | xFloor.ai | 40.01 | 53.00% | 47.47% | 61.26% | 0.73 |
| 18 | NVIDIA AI Blueprints | 37.73 | 59.60% | 45.20% | 72.61% | 7.72 |
| 19 | Vector (text-embedding-3-large) + GPT-5.4 | 37.72 | 51.40% | 42.94% | 46.03% | 9.32 |
| 20 | AnythingLLM | 35.58 | 47.80% | 44.59% | 40.50% | 3.31 |
| 21 | Weaviate Verba | 34.48 | 41.40% | 44.90% | 51.98% | 1.81 |
| 22 | Cymatix-Context | 33.93 | 42.20% | 42.74% | 50.70% | 12.99 |
| 23 | LlamaIndex (default configs) | 27.20 | 32.40% | 37.76% | 30.56% | 1.49 |
| 24 | LangChain (default configs) | 24.98 | 31.00% | 35.65% | 36.39% | 3.15 |
| 25 | Open WebUI + Chroma | 24.89 | 32.40% | 35.86% | 43.23% | 2.62 |

The table preserves all 25 rows and the units of the [official leaderboard](https://huggingface.co/spaces/onyx-dot-app/EnterpriseRAG-Bench-Leaderboard). Scores are imported from its [fixed-revision CSV](https://huggingface.co/spaces/onyx-dot-app/EnterpriseRAG-Bench-Leaderboard/resolve/0c816c8559bb9734e13834813de0766152513758/data/final_display_data/leaderboard.csv), retained as [a local aggregate snapshot](official-leaderboard-20260906.csv). The companion [table contract](public-results-20260906.comparison.json) validates every numeric cell.

Overall is on a 0–100 scale: average answer completeness when an answer is correct, and zero otherwise. It is not nDCG or the product of the separately averaged correctness and completeness columns. Invalid extra docs is an average document count, not a percentage. See the [benchmark paper, Section 5](https://arxiv.org/html/2605.05253v1#S5).

The [official repository](https://github.com/onyx-dot-app/EnterpriseRAG-Bench#leaderboard) excludes Onyx's own product to avoid a conflict of interest and requires reproducible submissions. A platform name identifies the submitted configuration; it does not summarize every possible configuration of that platform.

## Baseline interpretation

The [original experiments, Section 6](https://arxiv.org/html/2605.05253v1#S6) use OpenSearch BM25 and Qdrant vector retrieval with OpenAI text-embedding-3-large (3,072 dimensions), both at Top-10. The Bash agent explores files iteratively and selects a variable document count within a ten-minute budget. All three use GPT-5.4 for answering and evaluation. BM25 leads these baselines in correctness and recall; the agent has the highest Overall score. The leaderboard CSV retains more precision than the paper's table.

## Additional author-reported results

These publications are absent from the inspected official CSV. Their different protocols do not form another common ranking.

- [MemOnDemand, Table 1](https://arxiv.org/html/2608.22141#S5.T1): **72.88 Combined**, 80.00% correctness, 74.28% completeness, and 48.77% document recall on 500 questions and the full 618M-token collection. Its comparison reference called LB#1 is 68.22, an older leaderboard value; it is not the current official leader. These are the authors' reported measurements.

- [MegaMem, Table 3](https://arxiv.org/html/2608.22137#S5.T3): **82.26 Overall**, 86.50% correctness, 86.98% completeness, and 81.90% document recall for the final configuration. The stated headline protocol uses 400 validation questions and 10M persistent-memory tokens. Its reduced protocol cannot establish a lead over the full-corpus official submissions. Table 4 repeats those full-configuration numbers while labeling its ablation as 500 questions; this note therefore uses only Table 3's declared scope and does not merge the two protocols.

- [Omni's released verification artifacts](https://huggingface.co/datasets/getomnico/omni-enterprise-rag-bench): **63.95508 Overall** for the base 500-question DeepSeek V4 Pro run and **68.07302** after a documented GPT-5.4 adjustment. The final merge selects 21 revised answers and two revised judgments; retrieved document IDs are unchanged. The adjusted score is not a single unmodified run and is not present in the inspected official leaderboard.

## Relationship to the local skill comparison

The [local comparison](20260906-v2/final-report.md) scores 18 routes over 40 questions and 985 documents. Its best nDCG@10 is 59.40% for Entity Graph / Lexical; its best Recall@10 is 64.56% for Classical / BM25. The local embedding backend uses deterministic hashing, while the official vector baseline uses a trained model. Neither the workload nor the scoring contract supports subtracting those values from official Overall scores or ranking local skills among the official systems. The local run has no generated-answer Overall score.

## Provenance and verification

- Official Space revision: `0c816c8559bb9734e13834813de0766152513758`.
- Space last-modified timestamp: `2026-08-28T21:53:59.000Z`.
- CSV SHA-256: `1c8b45b62883b7cec6c022951caddfbd76f20b042ac9378dd5a9eb2f55a7e1e2`.
- The Space declares the MIT license. This snapshot contains published aggregates only.
- All 25 system labels, row order, and five numeric columns were checked against the pinned CSV.
- No raw question bank, gold answers, submitted answers, or per-question evaluations were fetched for this note.

[Dataset guide](../../../docs/evaluation-datasets-and-reports.md) · [Local dataset overview](../README.md) · [Comparison catalog](../../COMPARISON-REPORTS.md)
