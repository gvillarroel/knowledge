# ADR 0122: Bound Enterprise evolution by consecutive misses and a finite catalog

Date: 2026-09-07

Status: Accepted

## Context

The user requested continued EnterpriseRAG improvement: retain an evolution
strategy until it fails three times, then advance through evolution strategies
and knowledge-generation families. Study e5 is terminal and cannot be repaired
or used as a replacement for prospective candidate evaluation.

## Decision

Create a new prospective campaign. Use the maintained native Harbor reflective
Pareto controller as the single evolution owner. Here an evolution strategy is
a declared mutation mechanism, such as length normalization, semantic
segmentation or graph/lexical fusion. This campaign does not claim to execute
GEPA, trace distillation or operator coevolution under another algorithm's name.

Register all eight knowledge families and an ordered, finite catalog of 116
possible new candidates. A unique, evaluable child fails when it does not improve
its family's qualified incumbent nDCG@10 by more than 1e-12. A gain resets the
consecutive-failure counter. Three consecutive failures close that strategy;
exhausting its variants closes it with a different reason. Duplicate profiles
do not consume a trial or count as failures. Infrastructure failures stop the
campaign with unavailable fitness. Semantic integrity failures cannot win and
count as failed candidates. Never replay an already scored candidate.

Five families change construction plans. Legacy, Turso and Graphify use a
separately labeled consultation treatment because their builders expose no
corresponding plan. Each candidate changes only its family's profile asset;
the complete package, helper, builder, consultant and runtime are frozen.
Retain authoritative record identities and byte-identical independent builds.
The Turso consultation extension hydrates records through read-only SQL and
ranks them with the frozen BM25 helper; it is not an optimized SQL BM25 engine.

The baseline incorporates each family's best completely measured historical
Enterprise profile: MiniLM for Embeddings; reduced expansion for Classical;
reduced BM25 length normalization for Adaptive and Entity Graph; MiniLM plus
stronger titles for Ensemble; and unchanged Legacy, Graphify and Turso. Every
family receives a fresh native control that must reproduce its historical
score within 1e-12 before children may run. Completed controls and incumbents can be imported by the
owner at their exact staged source path, with complete task/agent/lock parity;
only a new child incurs a native job. Each family is an independent sequential
lane, with at most two simultaneous lanes and unchanged resource limits.

After all lanes finish, choose one qualified family incumbent by highest
Enterprise primary-route score, then fewer changed profile fields relative to
that family's control, then family ID.
Freeze that exact package before opening the reserved, previously unconsumed
FiQA and SciFact validation portfolio for that family. Require no source-family
regression, nonnegative mean gain and full integrity. Validation is terminal;
there is no subsequent mutation, reselection or additional holdout in this
study. An unchanged winner leaves validation unopened.

## Interpretation and publication

Enterprise development remains 40 previously exposed queries over a reduced,
reference-enriched 985-document corpus and one independence group. This measures
retrieval ranking, not the official full-corpus answer-quality leaderboard.
An exhausted finite catalog is not evidence that every possible algorithm has
been exhausted. Publish all attempts, plateaus, skipped duplicates, family
controls, winners and terminal gate status. Keep corpus, qrels, native traces,
candidate copies and model weights ignored; commit only source and reviewed
aggregate reports.

See the [operating guide](../../docs/enterprise-evolution-sweep.md).
