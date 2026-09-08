# EnterpriseRAG: Classical on the complete corpus

**Retrieval complete: 500/500 questions against all 511,962 documents.** GPT-5.4 stopped after 317 preserved answers because Copilot returned quota errors, so its Overall score and public-table position are unavailable. The completed [internal Luna measurement](luna.md) scores **48.33/100 Overall** over all 500 answers, with Luna as both answer generator and judge.

[Internal Luna measurement](luna.md) · [CTA](cta.md) · [Question categories](categories.md) · [Aggregate evidence](aggregate.json) · [Table contract](comparison.json) · [Frozen configuration](reproduction.json) · [Execution guide](../../../docs/enterprise-classical-full-corpus.md) · [Classical skill](../../../skills/consult-semantic-okf-classical/SKILL.md) · [Report hub](../README.md)

## Retrieval result

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Classical / BM25 | 59.03% | 67.97% | 59.53% | 62.34% | 286.40 ms |

Position 1 enumerates the only locally measured route. It is not a public leaderboard rank. Quality values use a 0–100 scale and average the 470 questions with original reference documents. All 500 questions contribute to latency. The 10 high-level and 20 information-not-found questions remain in the answer workload and are excluded from retrieval-quality means.

The run uses unchanged Classical normalization, tokenization, BM25 parameters and exact scalar score/tie ordering through a disk-backed execution adapter. Every source body is preserved; global term frequencies and field lengths use the entire corpus. This is direct Classical/BM25 retrieval, not a complete Semantic OKF/RDF package or autonomous agent skill selection.

## Public leaderboard comparison

The [official leaderboard](https://huggingface.co/spaces/onyx-dot-app/EnterpriseRAG-Bench-Leaderboard) was checked on 2026-09-08 and still has revision `0c816c8559bb9734e13834813de0766152513758`. Its 25 published rows match the [preserved public reference](../../enterprise-rag-bench/reports/public-results-20260906.md). The published BM25 + GPT-5.4 baseline is tenth with Overall **50.60**, while metor.com leads with **80.34**.

Our relative position cannot be calculated from this retrieval result. Official Overall is the mean of per-question correctness multiplied by completeness after the official GPT-5.4 answer and judge workflow. Even the leaderboard document-recall column uses its correction procedure, so it is not an interchangeable baseline for the original-qrel recall above.

The exact upstream answer prompt, source formatter, citation stripping, correction, fact checks and holistic correctness evaluator are bound to the pinned upstream revision. GPT-5.4 made 319 calls: 317 completed and two returned HTTP 429 quota errors. The executor reported 315 collected answers before draining two in-flight successful calls; all 317 answer files are preserved. No judge ran, no partial answer score was calculated, and no failed response was counted as a semantic zero. The [aggregate evidence](aggregate.json) preserves usage, execution time and the frozen binding.

The complete Luna run scores **48.33 Overall**, **70.20% correctness** and **52.75% completeness**. Its internal scoring uses Luna rather than the public GPT-5.4 judge, so the score cannot establish a public-table rank. A future compatible local comparison would still require maintainer verification for an official listing.

## Corpus and verification

| Application | Physical documents |
|---|---:|
| confluence | 5,189 |
| fireflies | 10,173 |
| github | 8,052 |
| gmail | 121,390 |
| google-drive | 25,108 |
| hubspot | 15,017 |
| jira | 6,120 |
| linear | 35,308 |
| slack | 285,605 |

All four original-ID collisions are preserved as eight physical records. One colliding ID appeared twice in one question. Before inference, every first-occurrence citation was verified against the pinned original JSON path and complete upstream export text. The public answer input deduplicates the one later physical alias without refill or reordering: 4,999 unique citations across 500 questions, with nine documents in the affected answer context. The original physical rankings and retrieval metrics remain immutable.

The adapter passed exact rank and score parity on 53 ordinary, non-benchmark query pairs over the previously validated 985-document snapshot, plus synthetic global-frequency, Unicode, repeated-term, length, tie and empty-token cases. Index hashes were verified before and after the 500-query pass. Queries, qrels, source bodies, per-question results and model responses remain ignored.

Frozen retrieval binding SHA-256: `c2cbf0e7ae80b7b1de7ddad19ca0724edc8cb0fd661a9b14e568fc32de78d72b`. The aggregate companion binds the corpus archive, questions, index, code and execution receipts.

## Relationship to the preceding generator report

The [incoming/G2 comparison](../enterprise-generator-g2/README.md) used 985 complete documents and 40 questions. Its 97.85 Classical nDCG is not a full-corpus score. The corpus and question population change here, so the difference does not measure a generator regression or improvement.

The canonical Classical packages are byte-identical to those embedded in G2. No skill mutation, search for a better configuration, semantic retry, or private acceptance gate was performed here.

After the earlier conditional no-push decision, the user explicitly requested an unconditional push to main. That push completed as `d52f3c8b3df0d4829797ce28fcd50b03e1b32bbe`; it does not change the preceding unchanged-retrieval finding.
