# EnterpriseRAG E14: six qualified starting profiles compared

Date: 2026-09-11. This fixed checkpoint combines the six published family reports through the Classical starting qualification. It compares their retained profiles on the same 120 stratified questions, 112 retrieval-eligible questions, eligible population weight 470 and 6,000 complete documents. Entity Graph and Ensemble have no qualified published score in this checkpoint.

**Legacy has the highest aggregate retained nDCG@10, but the observed leaders differ by application.** Embeddings leads on Confluence, GitHub and Slack; Classical on Fireflies and Linear; Turso on Gmail and HubSpot; and Legacy on Google Drive and Jira. These are descriptive development results from the existing profiles. They do not establish a new evolution improvement, an accepted deployment choice or a tested application-routing strategy.

## Retained quality

Quality metrics below use a 0-100 display scale. Each family uses its registered primary route and retained role; construction and consultation treatments are not substituted.

| Family | Retained role | Primary route | nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 |
| --- | --- | --- | --- | --- | --- | --- |
| [Legacy](../legacy-starting-qualified-001/README.md) | retained-start | lexical | 72.38 | 81.99 | 71.51 | 76.43 |
| [Turso](../turso-starting-qualified-001/README.md) | retained-start | lexical-sql | 72.08 | 82.51 | 71.61 | 77.26 |
| [Adaptive](../adaptive-starting-qualified-001/README.md) | retained-start | adaptive | 66.21 | 74.02 | 67.37 | 69.27 |
| [Embeddings](../embeddings-starting-qualified-001/README.md) | baseline | hybrid | 63.51 | 80.82 | 61.59 | 75.61 |
| [Classical](../classical-starting-qualified-001/README.md) | retained-start | fusion | 62.10 | 64.17 | 66.38 | 57.82 |
| [Graphify](../graphify-starting-qualified-001/README.md) | baseline | search | 8.12 | 14.85 | 6.71 | 12.53 |
| Entity Graph | Pending | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| Ensemble | Pending | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |

## Applications

Application membership can overlap; these rows must not be added together. Scores retain the frozen population weights within each group. The listed leader uses the unrounded score, treating absolute differences of at most 1e-12 as ties.

| Group | Questions | Eligible | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Observed leader |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| confluence | 39 | 39 | 69.99 | 69.70 | 68.09 | 70.99 | 60.05 | 9.82 | Embeddings |
| fireflies | 9 | 9 | 77.65 | 78.19 | 69.60 | 56.10 | 78.91 | 4.75 | Classical |
| github | 12 | 12 | 64.76 | 62.58 | 62.71 | 67.29 | 57.63 | 11.03 | Embeddings |
| gmail | 10 | 10 | 72.19 | 72.52 | 71.15 | 49.64 | 50.07 | 16.88 | Turso |
| google_drive | 14 | 14 | 76.29 | 73.08 | 68.73 | 66.33 | 62.33 | 17.72 | Legacy |
| hubspot | 9 | 9 | 74.14 | 75.27 | 59.97 | 63.68 | 56.90 | 0.00 | Turso |
| jira | 26 | 26 | 79.77 | 77.80 | 69.16 | 65.37 | 65.61 | 5.45 | Legacy |
| linear | 15 | 15 | 83.06 | 82.16 | 81.33 | 69.72 | 83.23 | 12.83 | Classical |
| slack | 24 | 24 | 56.20 | 56.36 | 50.16 | 62.80 | 46.68 | 2.82 | Embeddings |

## Question categories

Category groups partition all 120 questions. The two groups without retrieval references retain unavailable scores, rather than zero scores.

| Group | Questions | Eligible | Legacy | Turso | Adaptive | Embeddings | Classical | Graphify | Observed leader |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| basic | 24 | 24 | 84.80 | 84.44 | 84.72 | 71.54 | 79.17 | 10.13 | Legacy |
| completeness | 12 | 12 | 55.71 | 55.53 | 62.90 | 52.20 | 31.00 | 16.69 | Adaptive |
| conflicting_info | 4 | 4 | 100.00 | 97.99 | 96.26 | 78.30 | 90.33 | 18.72 | Legacy |
| constrained | 8 | 8 | 87.84 | 88.05 | 80.70 | 86.92 | 71.46 | 6.05 | Turso |
| high_level | 4 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| info_not_found | 4 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| intra_document_reasoning | 12 | 12 | 100.00 | 100.00 | 100.00 | 82.89 | 100.00 | 6.10 | Legacy, Turso, Adaptive, Classical |
| miscellaneous | 8 | 8 | 92.88 | 92.88 | 87.50 | 90.77 | 87.50 | 18.11 | Legacy, Turso |
| project_related | 12 | 12 | 63.62 | 60.68 | 60.27 | 71.66 | 54.96 | 9.44 | Embeddings |
| semantic | 32 | 32 | 40.20 | 40.83 | 20.22 | 32.90 | 22.53 | 1.35 | Turso |

The application groups contain 9-39 questions; category groups contain 4-32. No statistical significance test or uncertainty interval was computed. Some observed leads are small, such as Classical over Legacy on Linear. No subgroup leader has been selected as a new incumbent, and combining the per-group leaders into a router has not been evaluated.

## Cost, time and quality

This table describes the one retained native job for each qualified family, not all starting roles, the whole family search or total campaign wall time. Build time covers the verifier's two builds. Timings were observed on a shared host and do not establish an isolated causal speed advantage.

| Family | Job seconds | Agent seconds | Two-build seconds | Query P95, ms | Knowledge bytes | nDCG@10 |
| --- | --- | --- | --- | --- | --- | --- |
| [Legacy](../legacy-starting-qualified-001/cta.md) | 123.980 | 77.135 | 60.576 | 98.090 | 180,168,866 | 72.38 |
| [Turso](../turso-starting-qualified-001/cta.md) | 246.684 | 195.422 | 175.684 | 102.276 | 842,070,178 | 72.08 |
| [Adaptive](../adaptive-starting-qualified-001/cta.md) | 1,327.367 | 1,277.898 | 562.077 | 8,479.284 | 557,899,136 | 66.21 |
| [Embeddings](../embeddings-starting-qualified-001/cta.md) | 1,047.799 | 1,000.296 | 580.000 | 1,988.105 | 249,909,785 | 63.51 |
| [Classical](../classical-starting-qualified-001/cta.md) | 1,571.806 | 1,522.887 | 578.193 | 2,041.407 | 557,897,958 | 62.10 |
| [Graphify](../graphify-starting-qualified-001/cta.md) | 3,086.715 | 3,037.652 | 2,920.905 | 830.242 | 240,091,223 | 8.12 |

Each selected native job reports zero model calls and USD 0.00 provider cost. Host compute and orchestration are unpriced, so complete monetary cost is unavailable. There is no Luna answering or judging stage in this comparison.

## Evidence and remaining work

Every cell is copied or deterministically derived from the retained role of a pinned published aggregate. The six inputs share the same execution contract and workload denominators; all 20 group identities and per-family group denominators agree. Each category-weighted total reproduces the corresponding retained native score. The selected native records have full evidence integrity, zero execution errors, zero retries and 252 verified staged skill files each. Source SHA-256 commitments and unrounded values are preserved in [aggregate.json](aggregate.json).

This report dispatches no native jobs, creates no proposals, selects no candidate and opens no private gate. The original family reports preserve all measured starting roles, inherited charges, recorded stops and native provenance. The remaining family qualifications and inherited searches, paired joint replay, frozen whole bundle, all-500 comparison and independent acceptance still govern completion. No generated-answer Overall score or public leaderboard position is assigned.

### Pinned source reports

- [Legacy quality](../legacy-starting-qualified-001/README.md), [application/category groups](../legacy-starting-qualified-001/groups.md), [CTA](../legacy-starting-qualified-001/cta.md) and [aggregate](../legacy-starting-qualified-001/aggregate.json).
- [Turso quality](../turso-starting-qualified-001/README.md), [application/category groups](../turso-starting-qualified-001/groups.md), [CTA](../turso-starting-qualified-001/cta.md) and [aggregate](../turso-starting-qualified-001/aggregate.json).
- [Adaptive quality](../adaptive-starting-qualified-001/README.md), [application/category groups](../adaptive-starting-qualified-001/groups.md), [CTA](../adaptive-starting-qualified-001/cta.md) and [aggregate](../adaptive-starting-qualified-001/aggregate.json).
- [Embeddings quality](../embeddings-starting-qualified-001/README.md), [application/category groups](../embeddings-starting-qualified-001/groups.md), [CTA](../embeddings-starting-qualified-001/cta.md) and [aggregate](../embeddings-starting-qualified-001/aggregate.json).
- [Classical quality](../classical-starting-qualified-001/README.md), [application/category groups](../classical-starting-qualified-001/groups.md), [CTA](../classical-starting-qualified-001/cta.md) and [aggregate](../classical-starting-qualified-001/aggregate.json).
- [Graphify quality](../graphify-starting-qualified-001/README.md), [application/category groups](../graphify-starting-qualified-001/groups.md), [CTA](../graphify-starting-qualified-001/cta.md) and [aggregate](../graphify-starting-qualified-001/aggregate.json).

[E14 overview](../README.md) · [Dataset view](../../../datasets/enterprise-rag-stratified-development-120.md) · [By skill](../../../skills/README.md) · [CTA index](../../../cta/README.md)
