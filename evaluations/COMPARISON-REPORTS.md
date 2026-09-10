# Skill Comparison Report Catalog

Catalog updated: 2026-09-10.

Newest included scored or audited evidence: 2026-09-10.

This is the entry point for reviewed reports that compare knowledge builders,
consultants, generated expert skills, retrieval routes, or storage variants. It
organizes existing evidence; it does not recompute scores or combine results
from different datasets, cohorts, models, runtimes, or metric contracts.

The generated [report hub](reports/README.md) adds a dataset-specific leader
table, [pages by skill](reports/skills/README.md), and a
[cost/time/quality view](reports/cta/README.md). It includes the new pinned
EnterpriseRAG reduced-corpus diagnostic and preserves the contracts below.

The current [Entity Graph token-automaton native outcome](reports/evolution/e11/entity-token-automaton-native-001/README.md)
adds the original component measurement to the [eight-family development comparison](reports/evolution/e11/entity-token-automaton-native-001/README.md#eight-family-comparison),
with [application/category availability](reports/evolution/e11/entity-token-automaton-native-001/groups.md)
and [CTA](reports/evolution/e11/entity-token-automaton-native-001/cta.md). The
120-question, 6,000-document contract remains separate from full-corpus
retrieval, generated-answer quality and the final all-500 comparison. Five
family searches and independent whole-bundle acceptance remain open.

The [stratified Enterprise evolution E7](reports/evolution/e7/README.md) extends
the all-family search to 120 development questions and 6,000 complete documents.
Its [coverage matrix](reports/evolution/e7/strategy-coverage.md) lists each
family's mutation channel, fixed primary route and mechanisms. Follow its
native progress snapshots for measured opportunities and stopping evidence;
the paired all-500 comparison enters the catalog only after completion.

The latest [Classical full-corpus run](reports/enterprise-classical-full/README.md)
covers all 511,962 documents and all 500 public questions. Retrieval metrics
average the 470 questions with original reference documents. Only Classical
BM25 was evaluated; its local row number is not a public leaderboard position.
The official GPT-5.4 answer and judge stages have a separately frozen protocol;
their completion state is recorded in that report. [CTA](reports/enterprise-classical-full/cta.md) and
[question categories](reports/enterprise-classical-full/categories.md) keep the
retrieval and answer-quality boundaries visible.
The [internal Luna arm](reports/enterprise-classical-full/luna.md) uses the same
500 inputs with Luna for both answering and judging. Its score is separate from
the public GPT-5.4 judge contract.

The completed [Enterprise evolution sweep e6](reports/evolution/e6/README.md)
adds 106 new candidate evaluations and eight fresh controls across eight
knowledge families. Its [primary-route comparison](reports/evolution/e6/catalog-001/comparison.md),
[exact retained profiles](reports/evolution/e6/catalog-001/profiles.md), and
[CTA report](reports/evolution/e6/development-001/CTA.md) retain a separate
development contract. The campaign page records the terminal decision and
independent-validation state. The catalog contains twelve retrieval contracts,
including the later incoming/G2 replay and the full-corpus Classical run.
Several Enterprise entries share a reduced corpus and do not represent
separate independent datasets.

The [agent-selected Enterprise source-skill study](reports/enterprise-source-skills/README.md)
uses a separate full-text, generated-answer contract. Its comparison is not pooled
with the retrieval contracts. The [ingestion scope correction](reports/enterprise-source-skills/ingestion-scope-20260907.md)
binds all 114 e6 trials to the historical title-only projection and narrows the
interpretation of those preserved scores.

The [public EnterpriseRAG reference](enterprise-rag-bench/reports/public-results-20260906.md)
contains the official 25-system leaderboard snapshot and additional published
experiments checked on 2026-09-06. These external answer-quality scores use
different contracts from the local skill retrieval comparison and are not
pooled into the local rankings.

For future improvements, the [skill evolution roadmap](../docs/knowledge-skill-evolution-roadmap.md)
and [readiness inventory](reports/evolution/20260906-readiness.md) identify
candidate priorities, measurement boundaries, and independent-validation
prerequisites. They are unscored planning artifacts and do not change the
published rankings.

## Reading order

| Question | Current report | Compared scope | Interpretation boundary |
| --- | --- | --- | --- |
| Has every family received an opportunity on stratified full-text EnterpriseRAG? | [Current E11 status](reports/evolution/e11/README.md), [family evidence index](../docs/enterprise-family-report-index.md) and [strategy coverage](reports/evolution/e7/strategy-coverage.md) | Eight families; 120 development questions; 6,000 complete documents; three consecutive misses per mechanism and repeated improving rounds | Declared variants, live attempts and completed searches remain separate; final all-500 measurement and the private gate have their own completion evidence |
| Which Enterprise retrieval profiles improved under the three-miss rule? | [Completed e6 campaign](reports/evolution/e6/README.md) and [stopping ledger](reports/evolution/e6/development-001/strategies.md) | Eight primary routes, 33 finite tactics, 106 new candidates and eight fresh controls | Exposed development queries on 985 documents; each tactic stops at three misses or finite exhaustion; separate terminal acceptance decision |
| Which direct retrieval routes perform best on the frozen GraphRAG paper workloads? | [`LATEST-REPORT.md`](LATEST-REPORT.md) and its [machine-readable contract](LATEST-REPORT.comparison.json) | Twenty-five compatible routes on the 60-question generalization contract, plus a separate 40-question contradiction contract | Retrieval only; the report cutoff is 2026-07-30 and it does not measure generated-answer correctness |
| How do all eight registered build/consult families compare on agent tokens? | [Semantic OKF two-stage token usage](semantic-okf-datasets/reports/20260730-semantic-okf-token-usage.md) | Eight builders and eight consultants, with construction and consultation reported separately | Several consultation arms contain runtime errors; incomplete responses cannot be interpreted as efficient answers |
| Does the direct multi-family generator reproduce the separate canonical skills? | [Canonical multi-family parity verification](integrated-semantic-okf-knowledge-skill/reports/20260813-parity-verification.md) | Eight families across three datasets and 960 bound question cells | Deterministic build, runtime, query, and citation parity; not model-judged answer quality |
| Does the direct Classical generator reproduce the separate Classical stack? | [Integrated Classical parity verification](integrated-classical-knowledge-skill/reports/20260813-parity-verification.md) | Three datasets, 120 questions, four Classical routes, and 480 query-route cells | Deterministic retrieval and citation parity; not model-judged answer quality |
| Does exact chunking reduce the deterministic context payload? | [Classical chunked context efficiency](semantic-okf-datasets/reports/20260814-classical-chunked-context-efficiency.md) and [JSON companion](semantic-okf-datasets/reports/20260814-classical-chunked-context-efficiency.json) | 120 questions across GraphRAG, Astro, and quantum error correction | The 83.34% token reduction is a deterministic estimate, not provider billing or semantic quality |
| Does exact chunking preserve live end-to-end consultation quality? | [Canonical versus exact-chunk development comparison](semantic-okf-classical-chunked-quality-luna-study-v2/publication/tables/development-comparison.table.md) | Six paired development cases under GPT-5.6 Luna | Candidate rejected; the study did not release its sealed independent cohorts |
| What is the latest semantic interpretation of every completed Classical chunking strategy? | [Superseding isolated R5 audit](semantic-okf-classical-isolated-quality-audit-luna-study-v3/publication/tables/superseding-isolated-all-strategies-r5.table.md) | Frozen answers from three six-case cohorts, reviewed one answer per call in three criterion orders | Retrospective and cohort-local; every non-canonical semantic gate remains rejected and no row is promotion eligible |
| How do the file, embedding, Turso, and Graphify storage variants differ? | [Storage version decision report](semantic-okf-storage-versions/comparison-report.md) | Build size/time, bounded operations, retrieval capabilities, and agent usability | Capability and workload selection report; it does not establish one universal winner |

## Classical chunking evidence chain

The Classical chunking reports answer different questions and must be read in
this order:

1. The [deterministic 120-question regression](semantic-okf-datasets/reports/20260814-classical-chunked-context-efficiency.md)
   passed exact reconstruction, retrieval parity, citation, and context-guard
   checks. It reduced context bytes by 80.42% and deterministic estimated
   tokens by 83.34%. This was an offline mechanical result.
2. The first [live paired development comparison](semantic-okf-classical-chunked-quality-luna-study-v2/publication/tables/development-comparison.table.md)
   reduced total Harbor tokens by 15.52%, cost by 20.36%, and mean agent
   latency by 29.20%, but regressed semantic quality in four of six cases and
   produced invalid evidence rows in two cases. The exact-chunk candidate was
   rejected before validation release.
3. The repair program evaluated the canonical consultant and completed
   chunking variants on cohort-local contracts. Its
   [complete strategy table](semantic-okf-classical-chunking-pareto-luna-study-v2/publication/tables/complete-solution-agnostic-all-strategies-r1.table.md)
   preserves native reward, token, and evidence-validity measurements. The
   final v27 treatment reduced mean tokens by 82.30% on its independent cohort
   and improved mechanical reward, but it failed the zero-regression semantic
   gate and was not promoted.
4. The later [isolated R5 audit](semantic-okf-classical-isolated-quality-audit-luna-study-v3/publication/tables/superseding-isolated-all-strategies-r5.table.md)
   reused the frozen answers and corrected the semantic review method. It is
   the current source for semantic counts. Its associated
   [methodology delta](semantic-okf-classical-isolated-quality-audit-luna-study-v3/publication/tables/methodology-and-result-delta-r5.table.md)
   explains every superseded review version and shows that the corrections
   changed evaluator results, not generated answers.

The outcome is deliberately split: exact chunking demonstrated substantial
mechanical efficiency, but none of the evaluated variants passed the strict
paired semantic non-regression gate. The evidence does not authorize promotion
of a chunked consultant.

## Supersession map

Use the following rules when older Classical chunking tables appear in links,
ADRs, or study indexes:

- Use the [isolated R5 audit](semantic-okf-classical-isolated-quality-audit-luna-study-v3/publication/tables/superseding-isolated-all-strategies-r5.table.md)
  for current semantic-quality counts across all completed strategies.
- Use the [R5 methodology delta](semantic-okf-classical-isolated-quality-audit-luna-study-v3/publication/tables/methodology-and-result-delta-r5.table.md)
  to audit why R1 through R4 were abandoned or superseded.
- Retain the repair study's
  [complete R1 table](semantic-okf-classical-chunking-pareto-luna-study-v2/publication/tables/complete-solution-agnostic-all-strategies-r1.table.md)
  for native reward, token usage, and evidence-validity measurements. Its
  semantic counts are historical because R5 used the stricter isolated method.
- Treat the repair study's
  [R2 quality table](semantic-okf-classical-chunking-pareto-luna-study-v2/publication/tables/solution-agnostic-answer-quality-r2.table.md),
  [independent-gate table](semantic-okf-classical-chunking-pareto-luna-study-v2/publication/tables/independent-gates.table.md),
  and [live development table](semantic-okf-classical-chunking-pareto-luna-study-v2/publication/tables/live-development-strategies.table.md)
  as append-only historical evidence, not the latest semantic interpretation.
- The explicitly named `historical-*` tables preserve earlier decisions and
  must not override a later append-only correction.

## Study publication indexes

The following generated indexes bind the reviewed publication projections to
their study ledgers and SHA-256 digests. They intentionally exclude raw tasks,
answers, jobs, traces, verifier diagnostics, local paths, and credentials.

| Study | Publication index | Progress represented by the index | Release state |
| --- | --- | ---: | --- |
| Initial live canonical versus exact-chunk comparison | [Index](semantic-okf-classical-chunked-quality-luna-study-v2/publication/index.md) · [JSON](semantic-okf-classical-chunked-quality-luna-study-v2/publication/index.json) | 3/5 stages complete | Validation sealed; no holdout release |
| Classical chunking semantic repair | [Index](semantic-okf-classical-chunking-pareto-luna-study-v2/publication/index.md) · [JSON](semantic-okf-classical-chunking-pareto-luna-study-v2/publication/index.json) | 2/4 stages complete | Validation released once; no holdout declared or released |
| Retrospective isolated semantic correction | [Index](semantic-okf-classical-isolated-quality-audit-luna-study-v3/publication/index.md) · [JSON](semantic-okf-classical-isolated-quality-audit-luna-study-v3/publication/index.json) | 2/2 stages complete | Retrospective audit; no validation or holdout release |

Study completion percentages describe workflow progress, not quality. A
development rejection or retrospective correction can be a final reportable
outcome even when a larger planned study did not continue to validation or
holdout.

## Dataset-specific route comparisons

These reports are useful transfer or domain evidence, but their ranks do not
combine into a single cross-dataset leaderboard:

| Dataset or domain | Report | Boundary |
| --- | --- | --- |
| Software architecture books | [All registered retrieval routes](software-architecture-books/reports/all-route-comparison.md) | Direct deterministic retrieval over 40 frozen questions; not answer quality |
| Data science, AI, and machine learning books | [All registered retrieval routes](data-science-ai-ml-books/reports/all-route-comparison.md) | Direct deterministic retrieval over a private-source corpus; the aggregate report is public, source content remains local |
| Quantum error correction papers | [Retrospective supervised expert comparison](quantum-error-correction-papers/reports/retrospective-supervised-expert-evaluation.md) | All qrels were exposed to profile construction; fixed-workload retrieval only and not promotion eligible |
| Astro documentation | [Retrieval comparison](semantic-okf-astro/reports/retrieval-comparison.md) | Dataset-specific deterministic retrieval evidence |
| Endocrine hygiene | [Retrieval comparison](semantic-okf-endocrine-hygiene/reports/retrieval-comparison.md) | Dataset-specific deterministic retrieval evidence |

## Report selection rules

- Compare alternatives only inside the same named dataset, cohort, task
  digest, model, runtime, attempt, candidate-budget, identity, and metric
  contract.
- Keep construction, deterministic retrieval, live consultation, semantic
  answer quality, storage capability, token usage, latency, and cost as
  separate causal layers.
- Treat infrastructure and agent errors as errors, never as semantic zeroes or
  efficiency wins.
- Use Harbor input tokens as totals that already include cached input; do not
  add cache tokens again.
- Prefer the latest append-only correction for the metric it corrects while
  retaining earlier digest-bound reports as historical evidence.
- Publish only reviewed aggregate projections. Raw Harbor jobs, tasks, answers,
  traces, diagnostics, and sealed validation or holdout internals remain local.

For the history of candidate creation, evolution controller use, and promotion
decisions, read
[`SKILL-EXPLORATION-AND-EVOLUTION.md`](SKILL-EXPLORATION-AND-EVOLUTION.md).
