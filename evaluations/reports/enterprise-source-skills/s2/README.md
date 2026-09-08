# Enterprise: one unified expert versus nine agent-selected source skills

A fixed paired native Harbor comparison on 40 exposed questions and 985 complete source documents. GPT-5.6 Luna chooses the skills, queries, document reads, combinations, and final cited answer. All nine source experts are available for every treatment question.

[By application](sources/README.md) · [CTA](CTA.md) · [Question categories](categories.md) · [Machine-readable aggregates](report.json) · [Findings and retained checks](../../../../docs/enterprise-source-skills.md) · [Report hub](../../README.md)

| Metric | Unified expert | Nine source skills |
|---|---:|---:|
| Citation-gated final-evidence nDCG@10 | 22.12% | 19.26% |
| Raw final-evidence nDCG@10 | 84.26% | 82.37% |
| Reference document recall@10 | 81.71% | 79.90% |
| Reference source coverage | 83.96% | 79.58% |
| Exact citation validity | 83.18% | 76.17% |
| Required-fact coverage, conservative semantic review | 90.15% | 78.12% |
| Complete paired semantic reviews | 33/40 | 33/40 |
| Full-quality cases among reviewed pairs | 20/33 | 16/33 |
| All-40 fact-coverage bounds for missing judgments | 74.37%–91.87% | 64.45%–81.95% |
| Submitted answers | 38/40 | 36/40 |
| Mean agent time | 39.1 s | 56.0 s |
| Mean input + output tokens | 25102 | 53572 |

The source-skill arm changes citation-gated nDCG by -2.86 percentage points and semantic required-fact coverage by -12.03 points. Among complete review pairs, source skills improved 1 answer, regressed 13, and tied on 19; 0 had mixed outcomes.

The semantic means use 33 complete paired cases. 8 of the 80 reviewer outputs were unavailable under the frozen schema. Both arms of an affected question are excluded together; missing judgments are not scored as failures. The all-40 arithmetic bounds above allow every missing question to range from zero to full coverage. They are missing-data bounds, not confidence intervals. See [the availability decision](../../../../.specs/adr/0124-report-unavailable-semantic-review-pairs.md).

## Observed skill choice

The source-skill arm's opened-skill count distribution is 2 skills: 1 question, 3 skills: 15 questions, 4 skills: 24 questions. Opening, searching, reading, and citing are reported separately in the application views. There is no fixed per-question router and no relevance annotation in the agent catalog.

## Evidence and limits

| Native evidence-contract outcome | Unified expert | Nine source skills |
|---|---:|---:|
| No mechanical violation | 10 | 8 |
| Citation-contract failure | 28 | 28 |
| Missing structured submission | 2 | 4 |

The gap between raw and gated nDCG reflects strict quote/marker integrity. Missing submission is an agent output-contract failure; no infrastructure error or negative semantic judgment is inferred from it.

All 80 benchmark trials completed with 0 external errors. Ten bundles passed exact raw-body fidelity (6,291,040 original characters), independent validation, deterministic reconstruction, and native helper parity. Two generic full-text technical rehearsals verified actual tool flow and executor isolation before sealing; they are excluded from this table.

The two anonymous high-reasoning reviews per question use ADR 0109's existing semantic contract and conservative consensus. Citation validity is a mechanical check and does not establish semantic entailment. The semantic review is automated; answer-generation and reviewer models belong to the same model family.

The corpus is reference enriched (85 references plus 900 distractors), all questions come from one exposed organization/source family, and only one attempt per arm is available. Partitioning changes retrieval candidate domains and lexical statistics as well as instruction selection. No independent transfer, official Enterprise leaderboard score, or promoted default is established.

Historical e6 scores used title-only knowledge. See the [scope correction](../ingestion-scope-20260907.md); those scores cannot serve as a full-text baseline for this comparison.
