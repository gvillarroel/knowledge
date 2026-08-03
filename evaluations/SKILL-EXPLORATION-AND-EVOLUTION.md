# Skill Exploration and Evolution Index

Updated: 2026-08-03.

This is the durable entry point for answering two questions: which knowledge
skills work best on the repository's test datasets, and what was tried while
evolving them. It summarizes decisions and links to the exact reviewed reports;
it does not replace their metric contracts or raw evidence.

## Where to start

- [`LATEST-REPORT.md`](LATEST-REPORT.md) is the current ordered evaluation
  report and explains which rows are directly comparable.
- [`graphrag-unseen-generalization/STRATEGY-RECOMMENDATION.md`](graphrag-unseen-generalization/STRATEGY-RECOMMENDATION.md)
  gives the current quality, latency, and contradiction-search recommendations.
- This document records the major evolution lineages, attempted strategies,
  outcomes, and promotion boundaries.
- [`../docs/knowledge-skill-evolution-playbook.md`](../docs/knowledge-skill-evolution-playbook.md)
  defines the current process for future studies.

There is no universal best skill. A recommendation is valid only for the named
dataset, cohort, candidate budget, identity grouping, runtime, and metric
contract.

## Current evidence-backed choices

| Workload | Current choice | Evidence and limitation |
| --- | --- | --- |
| General direct retrieval, quality first | `build-semantic-okf-classical` plus `consult-semantic-okf-classical` in `association` mode | 99.60% nDCG@10, 100% Recall@10, and 664.65 ms P95 on the sealed 60-question GraphRAG direct-retrieval comparison. This measures retrieval, not generated-answer correctness. |
| General direct retrieval, balanced latency | `consult-semantic-okf-tantivy` over the evaluated frozen classical projection | 96.25% nDCG@10, 100% Recall@10, and 128.27 ms P95. A fresh matched `build-semantic-okf-tantivy` pair still requires a new sealed validation cohort. |
| Approximately 100 ms direct retrieval | Matched Tika/MALLET pair in `fusion` mode, experimental only | 91.28% nDCG@10 and 99.48 ms P95. It gives up quality and depends on preview Tika software. |
| Contradiction-source coverage | Specialized expert v45 | 92.50% Full evidence@10 on the scoped contradiction study. It is slower, retrospective, and not the general default. |
| Grounded generated answers across all eight registered families | No winner | The live GraphRAG matrix is incomplete and affected by provider and execution failures. The current report explicitly forbids an eight-family winner claim. |
| Lower-token Classical consultation | Keep the canonical baseline | Many candidates saved tokens, but none passed the non-regression and semantic gates. |

The complete rankings and selection rules are in the
[strategy recommendation](graphrag-unseen-generalization/STRATEGY-RECOMMENDATION.md).

## Evolution campaign ledger

| Date and lineage | Mutable layer and skills | Evolution strategy | Dataset and result | Decision | Detailed evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-07-20, Graphify builder | `build-semantic-okf-graphify`; consultant frozen | Bounded direct mutation search over graph labels and reciprocal cross-partition TF-IDF edges | The selected reciprocal K=1 graph raised all-40 Recall@10 from 68.5% to 77.3% and holdout Recall@10 from 77.1% to 91.7%. The frozen consultant still failed the Harbor answer contract. | Promote only the direct-retrieval builder implementation; do not claim an answer-compiler gain. | [`graphify-builder-evolution.md`](semantic-okf-harbor/reports/graphify-builder-evolution.md) |
| 2026-07-20, Graphify Next | `build-semantic-okf-graphify-next`; consultant frozen | Candidate realization, population search, reflective Pareto analysis, and all-evolver contract checks | The 4,096-character root search-text candidate won both development datasets and the mean holdout, but regressed the Astro holdout task. Other controllers either confirmed the development result or failed closed on incompatible evidence. | Retain the baseline under the zero-regression gate. | [`graphify-next-all-evolvers-20260720.md`](semantic-okf-harbor/reports/graphify-next-all-evolvers-20260720.md) |
| 2026-07-22 to 2026-07-23, Tantivy consultation | `consult-semantic-okf-tantivy` over frozen knowledge | Trace distillation across 15 proposal/configuration iterations, followed by disjoint holdout | Candidate S passed 4/4 development trials. Neither R nor S qualified on the two-question holdout; S also lost exact evidence on one case. | Reject the evolved consultant and keep the live skill unchanged. | [`trace-distillation-20260722.md`](semantic-okf-tantivy/reports/trace-distillation-20260722.md) |
| 2026-07-23, Tantivy query and builder follow-up | Tantivy consultant, then `build-semantic-okf-tantivy` with the consultant frozen | Separate trace-distillation rounds on a new endocrine-hygiene cohort plus canonical revalidation | The query candidate improved means but regressed one holdout cell. The builder passed its local hard holdout but regressed the canonical GraphRAG retrieval table. | Promote neither skill; stop the lineage after the third complete round. | [`trace-distillation-round3-endocrine-20260723.md`](semantic-okf-tantivy/reports/trace-distillation-round3-endocrine-20260723.md) |
| 2026-07-23, Tantivy population rehearsal | `consult-semantic-okf-tantivy` | Scalar population search | `identity-natural` ranked first on development at 0.851161 mean reward versus 0.548310 for baseline. No disjoint holdout was run. | Development selection only; no promotion. | [`consult-population-search-20260723.md`](semantic-okf-tantivy/reports/consult-population-search-20260723.md) |
| 2026-07-23, Tika/MALLET consultation | `consult-semantic-okf-tika-mallet` | Four cumulative trace-distillation rounds | Round 3 covered the recurring trace-supported failure patterns. Round 4 found no new mutation supported by at least two trials and two task identities; the candidate digest was unchanged. | Declare trace saturation for that cohort. The round-3 candidate remains staged, unranked, and unpromoted. | [`trace-distillation-consult-v4-saturation-20260723.md`](semantic-okf-tika-mallet/reports/trace-distillation-consult-v4-saturation-20260723.md) |
| 2026-07-27, Tika/MALLET/Tantivy consult-to-builder | `consult-semantic-okf-tika-mallet-tantivy`, then `build-semantic-okf-tika-mallet` | Trace distillation with one frozen layer at a time | Consult v42 improved one case but reduced the development pass count; builder v45 fixed runtime failures but passed only 1/3 reward thresholds. Both holdouts remained closed. | Reject both trace-distilled candidates. | [`trace-distillation-consult-builder-20260727.md`](semantic-okf-tika-mallet-tantivy/reports/trace-distillation-consult-builder-20260727.md) |
| 2026-07-27, qualified Tika/MALLET builder | `build-semantic-okf-tika-mallet`; consultant search evaluated separately | Reflective Pareto search with direct builder tasks and a sealed holdout | The v46 qualified-runtime builder scored 1.0 on both development cases and four holdout trials, with no regression. Consultation candidates failed development. | Promote the exact v46 builder digest; leave the consultant unchanged. | [`reflective-pareto-consult-builder-20260727.md`](semantic-okf-tika-mallet-tantivy/reports/reflective-pareto-consult-builder-20260727.md) |
| 2026-07-28, specialized experts v43-v48 | Snapshot-bound GraphRAG expert skills built with `build-specialized-skill` | Trace-derived fielded BM25, reflective Pareto search, knowledge-expertise planning, exact Ensemble reproduction, then bounded quality/trace fusion | V43 ranked 10/24; v44 rose to 3/24; v45 made a smaller same-rank gain; v46 reproduced Ensemble quality; v48 ranked 1/24 on the retrospective all-40 table but increased latency and reduced hard-cohort nDCG. | Preserve as experimental retrospective experts; no untouched holdout existed. | [`v44`](semantic-okf-specialized-experts/reports/v44-reflective-pareto-study-20260728.md), [`v45`](semantic-okf-specialized-experts/reports/v45-knowledge-expertise-study-20260728.md), and [`v48`](semantic-okf-specialized-experts/reports/v48-ensemble-quality-trace-study-20260728.md) |
| 2026-07-28, supervised-profile experts v51/v3 | GraphRAG and Astro snapshot-bound experts | Three manual, append-only profile generations: supervised n-grams, cached authoritative tokens, then primary-identity deduplication | Both reached their frozen exposed-workload ceilings with exact evidence and lower latency. On the later 60-question GraphRAG evaluation-only study, v51 reached only 41.03% nDCG@10 and 43.33% ranking stability. | Retrospective fixed-workload evidence only; do not promote or treat as a general default. | [`definitive-experts-20260728.md`](semantic-okf-specialized-experts/reports/definitive-experts-20260728.md) and [`LATEST-REPORT.md`](LATEST-REPORT.md) |
| 2026-07-29 onward, methodology ablation | Retrieval/chunking treatments, not one live skill | Preregistered offline ablation across 21 treatments | The first run was invalidated because hybrid latency omitted its component retrieval costs. The corrected study found different point winners for GraphRAG and QEC and a 14-treatment cross-domain Pareto frontier. | Continue the hypotheses, but select no repository-wide default and promote nothing. | [`attempt-00-invalid.md`](knowledge-methodology-proposal-experiments/reports/attempt-00-invalid.md) and [`offline-ablation-01.md`](knowledge-methodology-proposal-experiments/reports/offline-ablation-01.md) |
| Through 2026-08-03, Classical token optimization V1-V66 | `consult-semantic-okf-classical` and isolated runtime/compiler candidates | Compact navigation, answer kits, bounded sections, source-role plans, one-shot complete records, and controlled runtime hooks | Exact V34 saved 98.674426% of tokens but regressed semantics in 4/6 cases. Six V30 answers saved about 77%, and five passed all mechanical metrics, but every one failed independent semantic review. | No accepted lower-token version; validation and holdout stayed sealed. | [`20260802-classical-token-optimization-attempts.md`](semantic-okf-datasets/reports/20260802-classical-token-optimization-attempts.md) |
| 2026-07-17 onward, eight-family grounded campaign | All eight matched build/consult families | Successive provider-aware campaign designs and forensic rescoring | Campaign 01 produced only 32 evaluable responses from 320 artifacts; Campaign 02 stopped at quota; later campaigns were preparation or dry runs. | No balanced grounded winner. Preserve the attempts as operational evidence. | [`graphrag-papers-consult-campaign-evolution.md`](semantic-okf-datasets/reports/graphrag-papers-consult-campaign-evolution.md) |

## What is versioned

Git keeps the material needed to understand and reproduce a decision:

- dataset descriptors, task generators, schemas, and validators;
- reviewed aggregate reports and compact machine-readable companions;
- the skill name or digest, frozen controls, controller, cohort, metrics, gates,
  outcome, and limitations; and
- ADRs for durable selection, rejection, and promotion decisions.

Git does not keep every candidate skill copy or raw trial. Acquired data,
processed snapshots, generated candidates, Harbor jobs, traces, runtime trees,
and verifier diagnostics stay in ignored `raw/`, `processed/`, `generated/`,
`results/`, `runs/`, `artifacts/`, `runtime/`, or `trace-distillation/`
directories below `evaluations/`. Root-local convenience junctions such as
`baseline-skill/`, `generation-*`, and `.tantivy-*` are ignored as well.

Every future evolution summary should state what changed, which layer stayed
frozen, which skill and controller were used, the dataset and split boundary,
the attempts that materially changed the decision, the measured result, the
final disposition, and why the evidence does or does not support promotion.
