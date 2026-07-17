# Adaptive Skill Population — Generation 0

The frozen benchmark passed before evaluation. Candidate 00 remained untouched. Candidates 01–09 were isolated standalone build/consult pairs; every pair processed the same 15 Markdown papers and 15 claim ledgers, independently validated 831 reviewed answer bindings, reproduced an identical 891-file tree on a second build, preserved the authoritative core, left consultation read-only, and retained the incumbent all-40 adaptive retrieval scores.

The table uses the predeclared fitness contract and three sequential executions per hard question. The raw append-only reports remain ignored; `generation-000-summary.json` is the compact machine-readable result.

| Candidate | Answer policy | Fitness | Answer claims@30 | Negatives@30 | Required papers@30 | Valid evidence | Mean ms | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 00 | Untouched incumbent; no verified evidence pack | 0.00 | n/a | n/a | n/a | fail | n/a | Discard |
| 01 | Full record, no cap | 79.47 | 53.5% | 66.7% | 90.5% | 100% | 305.6 | Discard |
| 02 | Full record, cap 3 per paper | **81.56** | 56.0% | 67.5% | **100%** | 100% | 319.6 | **Keep** |
| 03 | Interpretation only, no cap | 81.21 | 55.5% | 71.7% | 93.0% | 100% | 304.8 | Discard |
| 04 | Interpretation only, cap 3 | 81.09 | 51.5% | 71.7% | **100%** | 100% | 303.2 | Discard |
| 05 | Equal dual view, no cap | 79.40 | 55.5% | 72.5% | 95.5% | 100% | 581.5 | Discard |
| 06 | Equal dual view, cap 3 | 79.30 | 54.0% | 71.7% | 98.0% | 100% | 559.8 | Discard |
| 07 | Full 2:1 interpretation, cap 3 | **81.46** | **60.0%** | **75.0%** | 98.0% | 100% | 590.4 | **Keep** |
| 08 | Full 3:1 interpretation, cap 3 | 81.44 | **60.0%** | **75.0%** | 98.0% | 100% | 595.5 | Discard |
| 09 | Full 2:1 interpretation, cap 4 | 80.28 | 57.5% | **75.0%** | 95.5% | 100% | 604.9 | Discard |

Candidate 02 wins the scalar score through complete paper coverage and near-single-view latency. Candidate 07 is the complementary survivor because it retrieves the most exact atomic claims and important negatives. Candidate 08 is dominated by candidate 07. The data also show that paper-aware diversification, not interpretation-only ranking by itself, is the repeatable improvement.

The all-40 adaptive route remained at Recall@10 `0.8381619769`, MRR@10 `0.9583333333`, nDCG@10 `0.8342720300`, and evidence validity `1.0`. Therefore the answer-evidence gains did not trade away ordinary retrieval quality.
