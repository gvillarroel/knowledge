# Enterprise retrieval evolution sweep

The [evolution implementation](../evaluations/enterprise-evolution/) runs a new
prospective search over eight knowledge families. It preserves the stopped e5
study and uses its published development findings only as historical context.
The decisions are recorded in [ADR 0122](../.specs/adr/0122-enterprise-three-miss-evolution-sweep.md).

## What is being evolved

| Family | Treatment | Mutation strategies |
| --- | --- | --- |
| Legacy | Consultation | BM25 saturation, length normalization, title weight |
| Embeddings | Construction | Semantic segmentation, sentence context |
| Classical | Construction | Length normalization, BM25 saturation, title weight, expansion strength, relevance/diversity |
| Adaptive | Construction | Classical mechanisms plus aspect allocation |
| Entity Graph | Construction | Length normalization, BM25 saturation, graph reach, candidate-edge weight, section granularity |
| Ensemble | Construction | Classical mechanisms plus component allocation |
| Graphify | Consultation | Traversal depth, lexical/graph fusion, reciprocal-rank decay |
| Turso | Consultation | BM25 saturation, length normalization, title weight |

The fixed inventory contains 116 candidate variants. Each strategy stops after
three consecutive new candidates fail to improve the family's best qualified
nDCG@10, or when its finite variant list is exhausted. A gain resets the counter.
Duplicate complete profiles are skipped without execution or failure credit.
External failures remain unavailable and stop execution; integrity failures
remain failed candidates. These categories appear separately in the ledger.

The Graphify rank-decay variants explicitly set `lexical_weight=1.0` while
testing `rrf_k` values 5, 20 and 60. If a preceding fusion tactic retains another
lexical weight, these are compound mutations; they do not isolate decay at that
retained weight. Interpret the exact variant fields in the attempt ledger,
rather than the inventory rationale's shorthand about a retained mix.

Each control carries that family's best completely measured historical
Enterprise configuration. A fresh native measurement must reproduce the old
score before any new child executes. Historical gains are not counted again.

The installed `harbor-reflective-pareto-search` owns native staging, scoring,
comparison, archive lineage and the independent gate. The scheduler chooses
the next predeclared mutation and enforces the user's plateau rule. One native
trial contains all 40 Enterprise development questions for one family, so the
native per-family archive has a single aggregate case; query metrics are also
retained in native verifier diagnostics. This is not a multi-domain Pareto claim.

## Reproducibility and boundaries

The preparation command creates `tmp/e6/` exclusively and refuses to replace
an existing workspace. It freezes the complete skill package, mutation helper,
runtime bridge, native agent, task contracts, plans and model revision. Dataset
images derive from pinned, previously reviewed source images. The independent
curator must bind the inherited authoring plan, verify deterministic task replay,
exercise verifiers and approve the registered dataset locks before sealing.

Reproduction requires the retained local e5 baseline, curator/task artifacts,
model inventory and pinned MiniLM cache, plus the reviewed source Docker images.
Those inputs remain ignored and are not bundled with the public reports. The
registered execution uses Windows for source verification and candidate
realization, and WSL Ubuntu with Harbor 0.18.0 for native trials. The frozen
host/runtime paths are specific to this campaign; a different installation
requires a newly prepared and reviewed execution contract before running.

```powershell
python -B evaluations/enterprise-evolution/prepare.py
python -m pytest tests/test_enterprise_evolution_sweep.py
```

Preparation alone does not authorize native candidate execution. The organizer
must seal the exact protocol, baseline, execution contract and curator receipt;
then the evolution stage can run from Linux/WSL. `run.py` checks those bindings
before each dispatch. Reusing a completed job requires its exact native staged
skill source and matching locks; no completed candidate is rerun for selection.

The study is registered on Windows, so its absolute paths are verified there by
`study_guard.py`. The same official realizer also runs on Windows to avoid WSL
9P overhead while copying and hashing the skill bundle. Native Harbor executes
and verifies all trials in Linux. This changes orchestration cost, not agent
resources, task contents or the scoring implementation.

After independent qualification and review, seal and run the supervised phase:

```powershell
python -B evaluations/enterprise-evolution/seal.py --review tmp/e6-review/final
python -B evaluations/enterprise-evolution/launch.py development
python -B evaluations/enterprise-evolution/launch.py normalize
$env:MPLCONFIGDIR = Join-Path (Get-Location) 'tmp/e6/plot-cache'
python -B evaluations/enterprise-evolution/report.py publish --output evaluations/reports/evolution/e6/development-001
```

After reviewing that aggregate publication, create its standard comparison
contract, exact selected-family profiles, and all 18 retained-profile route
observations without reopening native jobs:

```powershell
python -B evaluations/build_enterprise_evolution_views.py --source evaluations/reports/evolution/e6/development-001/aggregates.json --output evaluations/reports/evolution/e6/catalog-001
```

Review and register `development-001` and `catalog-001` as separate
`evolution-report` evidence items on the running `evolve` stage, with role
`development`, before freezing selection. Once registered, keep both directories
immutable. Do not bind the mutable campaign navigation page as evidence.

The [campaign report](../evaluations/reports/evolution/e6/README.md) carries the
current execution, publication and independent-validation status. Register its
completed comparison contract in `evaluations/report-sources.json` before
regenerating the shared dataset, skill and CTA catalog. Historical contracts
retain their separate rows; a development maximum is not a replacement for
an independent result or evidence about the currently installed skill.

Every output path is append-only. Inspect native failures before taking further
action; these commands do not resume or replay a failed attempt. After all
families complete, `finalize.py prepare-selection` registers and freezes the
native winner. For a changed winner, `launch.py validation` executes the single
released gate and `finalize.py close-gate` records its terminal outcome.

After that terminal decision exists, publish the exact selected aggregate and
allowlisted acceptance fields. This command never reads the reserved tasks or
native gate diagnostics:

```powershell
python -B evaluations/build_enterprise_evolution_views.py --source evaluations/reports/evolution/e6/development-001/aggregates.json --terminal-decision tmp/e6/terminal-decision.json --selection tmp/e6/selection.json --output evaluations/reports/evolution/e6/terminal-001
```

For a changed finalist, register the reviewed terminal report on the running
`publish` stage and complete that stage. For an unchanged finalist, the frozen
workflow stops validation and publication without opening the reserved
portfolio; the development reports are already bound to `evolve`, and the
terminal projection documents that decision without changing those stages.
Unavailable gate metrics remain null/N/A, never inferred zero scores.

Two family lanes may execute at once. Within a lane, every next candidate is
derived from its retained incumbent. Agent trials have two CPU threads, the
existing 12 GiB ceiling, one attempt and zero retries. Network access is disabled.
Each trial performs two complete builds and matched validation before measuring
retrieval, including consultation treatments. LLM calls remain zero.

After the whole catalog sweep, one family and exact candidate are frozen for
a single terminal comparison on the reserved FiQA and SciFact cohorts. Both
source groups must avoid regression and preserve integrity. An unchanged
winner leaves the gate unopened. Private results never drive another child.
That gate measures transfer to its two reserved source groups; it does not
establish performance on previously unseen EnterpriseRAG questions.

## Reading results

Report scores are nDCG@10, Recall@10 and MRR@10 on the reduced internal workload.
Do not compare these percentages numerically with the official EnterpriseRAG
answer-quality scores. Construction and consultation treatments must retain
their labels, including the Turso BM25 helper's in-memory ranking after SQL
hydration. All source data, questions, relevance labels, model weights and
native traces stay in ignored paths. Public reports contain reviewed aggregates
by family, strategy, candidate attempt and dataset, plus the overall comparison.

[Back to the documentation index](README.md).
