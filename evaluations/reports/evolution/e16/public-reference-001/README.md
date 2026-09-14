# EnterpriseRAG public leaderboard recheck

Checked on 2026-09-14. This is an external reference check, with no new model
run, skill selection or benchmark evaluation.

The [official published aggregate CSV](https://huggingface.co/spaces/onyx-dot-app/EnterpriseRAG-Bench-Leaderboard/resolve/0c816c8559bb9734e13834813de0766152513758/data/final_display_data/leaderboard.csv)
is byte-identical to the repository's September 6 snapshot. All 25 rows and
numeric columns remain unchanged. The Space revision is
`0c816c8559bb9734e13834813de0766152513758`, last modified
`2026-08-28T21:53:59.000Z`; the CSV SHA-256 is
`1c8b45b62883b7cec6c022951caddfbd76f20b042ac9378dd5a9eb2f55a7e1e2`.

| Published position | Published strategy | Overall |
| ---: | --- | ---: |
| 1 | metor.com | 80.34 |
| 2 | CDL (Causal Dynamics Lab) | 78.95 |
| 3 | Troml | 76.79 |
| 8 | OpenAI File Search | 61.03 |
| 9 | Bash Agent (GPT-5.4) + GPT-5.4 | 52.63 |
| 10 | BM25 + GPT-5.4 | 50.60 |
| 19 | Vector (text-embedding-3-large) + GPT-5.4 | 37.72 |

See the [preserved complete public table](../../../../enterprise-rag-bench/reports/public-results-20260906.md)
for all 25 entries and the documented scoring and submission protocols. This
check fetched Space metadata and aggregate CSV data only. No question bank,
submitted answer or per-question judgment was fetched. The ignored local
receipt is `tmp/enterprise-next-preparation/e16-public-leaderboard-check-001/receipt.json`.

The E16 development and pending all-500 comparison measure retrieval nDCG@10
on a 6,000-document corpus. The separate [Classical/Luna measurement](../../../enterprise-classical-full/luna.md)
uses the full corpus and a Luna judge. Neither protocol supports assigning a
position among the official GPT-5.4-judged Overall results above. The external
recheck does not feed the frozen optimizer or change its selection policy.

[Report hub](../../../README.md).
