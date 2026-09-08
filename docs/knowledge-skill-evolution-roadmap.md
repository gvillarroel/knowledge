# Knowledge skill evolution roadmap

Research date: 2026-09-06. Status: proposed development program; no new candidate,
evolution run, acceptance decision, or score improvement is claimed here.

This roadmap applies the existing [evolution playbook](knowledge-skill-evolution-playbook.md)
to the repository's current skills and [dataset-specific rankings](../evaluations/reports/README.md).
The accompanying [readiness inventory](../evaluations/reports/evolution/20260906-readiness.md)
records the inspected target versions and execution prerequisites. It is a
research artifact, not a registered study or a promotion receipt.

## Recommended direction

Improve retrieval implementations and index construction first, then improve
agent consultation instructions in a separately measured stage. Use native
Harbor evidence, trace-supported mutation contracts, and reflective Pareto
search to preserve useful alternatives. Use GEPA for a later instruction-only
stage when grounded answer quality is the measured objective.

The objective is a reproducible paired improvement over the same frozen
baseline on a named dataset and contract. A higher ordinal rank by itself is
insufficient: another row can move, and the internal tables contain different
metrics, workloads, exposure histories, and resource conditions.

## What the current measurement actually executes

The [EnterpriseRAG runner](../evaluations/enterprise-rag-bench/run_comparison.py)
builds eight matched families and delegates scoring to the
[direct-route evaluator](../evaluations/private-book-strategy-comparison/scripts/evaluate_all_routes.py).
That evaluator imports Python retrieval implementations and calls them directly.
It does not ask an agent to read `SKILL.md`, retrieve evidence, and answer.
Consequently, an instruction-only edit cannot change these retrieval results.

Two routes have a further attribution limitation. Legacy uses the evaluation
comparator's `LegacyLexicalIndex`; Turso uses a benchmark-local token-overlap SQL
comparator. Their scores do not measure the complete consultation behavior of
their corresponding skills. A new agentic or SQL retrieval treatment needs a
separately identified route and a frozen contract.

The current runner also binds canonical skill paths. Before optimizing an
isolated candidate, add and verify a candidate-aware execution bridge: stage
the exact candidate package through the native Harbor job, attest which runtime
bytes were imported, and prove baseline parity. Freeze this adapter before
search. Changing a configured skill path while still importing the canonical
runtime would produce an invalid candidate comparison.

| Track | Mutable target | Fixed components | Primary evidence |
| --- | --- | --- | --- |
| Construction | One builder, its declared plan, or derived index construction | Matched consultant, evaluator, source corpus, model and runtime except the declared treatment | Retrieval quality plus build resources and artifact validity |
| Retrieval consultation | One consultant's retrieval implementation | Exact processed snapshot and builder; other routes remain controls | Paired retrieval vectors, evidence identities, and query resources |
| Agent consultation | One consultant's instructions | Knowledge snapshot, retrieval runtime, agent model, tools, and judge contract | Grounded answers, completeness, unsupported claims, abstention, tokens and time |
| Generated expert | One generator or one generated expert, explicitly chosen | The other layer and its allowed source boundary | Native task outcomes and independent semantic review |

Changing a builder parameter and a consultant algorithm together is a separate
combined treatment. It cannot establish which component caused an improvement.

## Priorities grounded in current capabilities

These are hypotheses for new development evidence, not diagnoses inferred from
protected final-evaluation cases. The
[EnterpriseRAG diagnostic](../evaluations/enterprise-rag-bench/reports/20260906-v2/final-report.md)
is an exposed, reference-enriched 40-question workload. On that contract,
entity-graph lexical retrieval reaches 59.40% nDCG@10, embedding lexical
retrieval 59.07%, and the hashing-vector route 32.64%. This motivates testing a
learned embedding backend; it does not establish why an individual query fails
or predict an improvement on the full benchmark.

| Priority / family | First bounded hypothesis | Correct mutation boundary | Evidence required before selection |
| --- | --- | --- | --- |
| 1. Embeddings | Compare a pinned learned dense model with the existing 384-dimensional hashing control, keeping chunking fixed | Builder embedding configuration; matched consultant stays frozen | Recall and early-rank gains, exact model identity, CPU/GPU and cache strata, build/query cost |
| 2. Classical | Test one indexing or BM25 parameter at a time; separately test source-grounded title/section context in derived search text | Builder plan or derived index code | Paired nDCG and recall; effects on short queries, terminology, and distractors; unchanged authoritative evidence |
| 3. Adaptive | Calibrate existing aspect expansion and protected full-query fusion using eligible development failures | Existing builder policy parameters, or a separately frozen consultant-code stage | Query-intent dilution and case regressions; full-query protection remains enforceable |
| 4. Ensemble | Calibrate existing route weights and selective reranking; later compare a bounded cross-encoder | One declared policy or consultant-code treatment | Complementary case wins, ranking disagreement, incremental latency and model cost |
| 5. Entity graph | Bound graph expansion and assess when lexical evidence should anchor retrieval | One builder extraction policy or one consultant traversal policy per stage | Multi-source recall without false entity matches; every returned claim retains its source identity |
| 6. Graphify | Test bounded neighborhoods and source/type-aware retrieval on eligible graph tasks | One graph construction or graph search treatment | Retrieval completeness and noise, graph build resources, provenance validity |
| 7. Turso | Define a genuine retrieval/query treatment beyond the existing lexical SQL comparator | Explicit new route with its implementation staged and attested | Baseline parity before search, read-only queries, exact document IDs and comparable resource accounting |
| Control. Legacy | Keep the simple lexical comparator as a stable control; test full skill behavior only in the agent track | No simultaneous comparator and instruction mutation | Detect regressions that more complex routes introduce |

The [embedding builder](../skills/build-semantic-okf-embeddings/SKILL.md) already
supports Sentence Transformers with a pinned model revision and local cache.
The first treatment does not require inventing a new backend. Its model must
be selected and cached before the frozen job; network downloads are not an
implicit part of evaluation. Dense embeddings are distinct from additional
sparse or multi-vector features that would need their own integration.

Adaptive and Ensemble already implement protected fusion, deduplication, and
multiple retrieval signals. Re-adding those mechanisms is not a new treatment.
The [current build plans](../evaluations/private-book-strategy-comparison/scripts/prepare_strategy_bundles.py)
also expose indexing and reranking parameters. Changes to these plans require
a newly built and validated snapshot, even when the consultant is unchanged.

For specialized and integrated generators, first establish an improvement in
the canonical family. Propagate accepted bytes through their existing
generation/parity workflow. Do not manually diverge copied family assets, use
cross-skill imports, or treat the specialized expert's supervised QEC score as
evidence of transfer to unseen questions.

## Dataset eligibility and the next validation boundary

This audit does not certify an available unseen validation cohort. Historical
split labels, ignored files, or a new random seed cannot supply that guarantee.
The [evaluation-only registry](../evaluations/evaluation-only-registry.json)
has priority over a dataset's convenience or its published rank.

| Current report dataset | Exposure or policy boundary | Permitted role in the proposed program |
| --- | --- | --- |
| EnterpriseRAG reduced corpus, 40 | Exposed retrospective diagnostic; 985 reference-enriched documents from one synthetic company | Historical reference; a curator must explicitly authorize any development reuse and establish new independent evaluation families |
| Software architecture books, 40 | Published full-workload comparison; previous development/hard labels do not establish a fresh gate | Historical reference; eligible development reuse only after provenance review |
| Data science / AI / ML books, 40 | Published full-workload comparison with the same exposure concern | Historical reference; eligible development reuse only after provenance review |
| Astro, 40 | Historical results cover the train/dev/holdout-labelled workload | Historical reference; old labels cannot certify an untouched gate |
| Endocrine hygiene | Existing published evaluation history; fresh validation readiness not verified | Historical reference pending explicit exposure and access audit |
| Quantum error correction, 40 | All 40 qrels were exposed to supervised-profile construction; the published 100% is in-sample | Fixed-workload diagnostic only; no unseen-query or promotion claim |
| tau3 banking knowledge, 97 | Retrospective oracle-context diagnostic, distinct from official conversations | Retrieval diagnostic only; new conversation and grounded-answer contracts are required for broader claims |
| GraphRAG generalization, 60 | Registered evaluation-only; optimizer-visible use is forbidden | Preserve aggregate reporting and the registered final-evaluation restriction; never use for diagnosis, mutation, selection, or validation fitness |
| GraphRAG contradictions, 40 | Registered evaluation-only with the same restrictions | Preserve aggregate reporting and the registered final-evaluation restriction; never use for diagnosis, mutation, selection, or validation fitness |

The original GraphRAG 40-question development history is a different cohort
from the protected 60- and 40-question final-evaluation cohorts. Similar names
do not transfer development eligibility between them.

Author the next study's semantic families before materializing tasks, following
the [dataset authoring contract](../skills/harbor-author-evaluation-datasets/SKILL.md).
Keep related sources, templates, oracle lineages, and near-duplicates in the
same partition. For EnterpriseRAG, eight question categories are not eight
independent companies. The other 460 upstream questions are not automatically
an independent family either. A transfer claim needs additional independently
curated source families; a same-corpus question test supports a narrower claim
and still has to satisfy the organizer's family-disjointness contract.

Assign independent validation to a curator or access-controlled execution
context that the optimizer cannot inspect. `.gitignore` controls tracking; it
does not seal local files, remove prior Git history, or revoke knowledge already
seen. Register and digest-lock development and validation, and declare the
downstream gate, before any evolution stage. Add a third holdout when required
by the chosen controller or the claim.

## Ordered execution proposal

1. **Make the experiment eligible.** Audit exposure, author enough independent
   families, register the splits, freeze the protocol and evaluator, and verify
   candidate-path execution. Require deterministic rebuilds, oracle quality
   gates, leakage checks, and a redacted dry-run receipt before live Harbor.
2. **Measure the current baseline.** Use the exact package and knowledge
   digests, matched build/consult mode, fixed hardware, and the same cases for
   each candidate. Treat repeated deterministic searches as stability checks,
   not additional independent questions.
3. **Create an evidence-bound mutation plan.** Export sanitized, development-only
   failure classifications with source digests. Keep raw questions, expected
   IDs, answers, and hidden task content out of the planner and candidate.
   Aggregate leaderboard rows cannot substitute for this case-level evidence.
4. **Realize a small portfolio.** Preserve the incumbent plus at most four
   children, each with one mechanism. Retain a conservative child and a
   complementary alternative. The initial pilot should freeze the embedding
   consultant and vary the builder, testing a learned model first while holding
   chunking fixed. Context and chunking hypotheses belong in separate children.
5. **Evaluate and select on development only.** Use reflective Pareto search as
   the single controller for this code/index stage. Keep at most two development
   generations in the proposed pilot. Predeclare native calls, model/token
   spend, and wall-time caps; the controller does not itself guarantee a total
   campaign budget. Stop without a winner when quality, integrity, or budget
   requirements are not met.
6. **Freeze one candidate and open validation once.** Run the frozen baseline
   and candidate under the identical gate. Do not mutate, rerank, switch to an
   alternate child, or distill traces in response to that gate. A failed or
   feedback-informed revision needs a new study and fresh validation. Run any
   declared third holdout only after validation passes.
7. **Publish and, when justified, promote.** Verify production bytes against the
   accepted candidate, refresh integrated-generator parity, write the decision
   ADR, and publish reviewed aggregates with the exact scope of improvement.
   The next optimization cycle must preserve the same one-way boundary.

Use `harbor-maximize-knowledge-expertise` to plan only after suitable sanitized
development evidence exists; it neither mutates nor scores. Use
`harbor-realize-skill-candidate` for exact bounded edits,
`harbor-trace-distillation` for supported lessons, and
`harbor-reflective-pareto-search` for selection. Trace preparation may precede a
Pareto stage, but it must not introduce a second selection controller in the
same stage. The [playbook](knowledge-skill-evolution-playbook.md) defines their
ordering and required evidence.

For the later instruction-only stage, `harbor-evolve-skill` is the local GEPA
wrapper. Its current schema 2 requires three disjoint splits: evolution,
validation, and holdout. Do not supply only two because the broader organizer
allows an optional holdout. GEPA's optimizer-visible `valset` is selection data,
so it must map to local development/evolution, never to the independently sealed
validation gate. The wrapper edits `SKILL.md`; code changes use the separate
realization/Pareto route.

## Score gains without hiding regressions

Choose one primary quality metric per contract before search. For the current
EnterpriseRAG retrieval contract that is nDCG@10, accompanied by Recall@10 and
MRR@10. Tasks requiring several sources also need full required-evidence
coverage. Do not average these values with official EnterpriseRAG answer
Overall scores or semantic judge rewards.

Report the candidate-minus-baseline delta, the practical improvement threshold
declared in the protocol, and uncertainty from a paired analysis clustered by
independent semantic family. Assess sample size and detectable effect using
development evidence before releasing validation. With only one source family,
do not present repeated queries or category-level resampling as evidence of
cross-domain statistical confidence.

Keep hard gates for evidence identities, valid locators, artifact contracts,
and forbidden semantic regressions. Track per-family and per-task-type
regressions alongside the average. Maintain a Pareto view of quality, build
resources, query P95, agent tokens, and cost, using comparable hardware/cache
strata. Missing or failed outcomes remain unavailable; they are not cheap wins.
Declare live model prices and token accounting in the experiment rather than
reusing a historical dollar amount.

Agent-answer evaluation needs grounded correctness, completeness, unsupported
claims, contradiction handling, and justified abstention. Follow the
[isolated semantic-audit decision](../.specs/adr/0111-adopt-isolated-replicated-semantic-answer-audits.md):
one anonymized answer per review call, repeated criterion orders, and calibrated
controls. Mechanical reward or context-token reduction cannot establish an
answer-quality improvement. The earlier
[methodology decision](../.specs/adr/0081-merge-empirical-methodology-controls-without-promoting-retrieval-defaults.md)
also cautions against promoting one chunking default from exposed workloads.

## How the research supports these choices

- **GEPA:** reflective instruction search and a Pareto frontier fit the existing
  Harbor workflow. Its reported gains on other tasks are motivation, not an
  expected improvement for these datasets. [Primary paper](https://arxiv.org/abs/2507.19457)
  and [official DSPy GEPA overview](https://dspy.ai/api/optimizers/GEPA/overview/).
- **Contextual retrieval:** source-grounded chunk context can improve search
  signals before retrieval. Test this in derived indexes while preserving the
  authoritative original and recording the origin of any generated context.
  Never derive context from benchmark questions or qrels.
  [Anthropic engineering report](https://www.anthropic.com/engineering/contextual-retrieval).
- **Learned retrieval and reranking:** BGE documents dense, sparse, and
  multi-vector retrieval, while cross-encoders score query/document pairs at
  additional computational cost. Dense model replacement and bounded reranking
  are separate experiments; more complex modes require explicit support.
  [BGE-M3 reference](https://github.com/FlagOpen/FlagEmbedding/blob/master/research/BGE_M3/README.md)
  and [official reranker examples](https://github.com/FlagOpen/FlagEmbedding/blob/master/examples/inference/reranker/README.md).
- **Iterative retrieval:** IRCoT supports investigating multi-step retrieval for
  multi-hop questions. This belongs in an agent consultation contract with tool
  and token limits, after the direct retrieval baseline is reliable.
  [Primary paper](https://arxiv.org/abs/2212.10509).
- **Alternative prompt search:** MIPRO jointly optimizes instructions and
  demonstrations. It is a possible later comparison, not a reason to replace
  the established Harbor/GEPA stack or expose evaluation examples in a skill.
  [Primary paper](https://arxiv.org/abs/2406.11695).

## Reporting and immediate handoff

Keep raw datasets, candidates, trajectories, and case-level outputs local under
their declared access policy. Publish reviewed aggregates through the existing
[report catalog](../evaluations/COMPARISON-REPORTS.md) and
[data/report workflow](evaluation-datasets-and-reports.md). Each new comparison
must bind the parent and candidate, dataset and split, evaluator, model,
hardware, primary metric, and acceptance outcome. Preserve a machine-readable
companion and separate dataset, skill, and CTA views. Keep incompatible runs in
separate tables; do not add this unscored roadmap as a leaderboard source.

The next executable milestone is a candidate-aware, parity-verified baseline
and a registered study with independent validation. The current
[readiness inventory](../evaluations/reports/evolution/20260906-readiness.md)
is the handoff for that preparation. It deliberately does not fabricate a
formal planner campaign, case failure pack, model budget, or promotion result.

[Back to the documentation index](README.md).
