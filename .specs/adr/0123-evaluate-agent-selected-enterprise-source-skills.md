# ADR 0123: Evaluate agent-selected Enterprise source skills

## Status

Accepted for a fixed, development-only comparison on 2026-09-07.

## Context

The completed Enterprise e6 campaign measured deterministic retrieval families
over a shared 985-document reduced corpus. It did not measure a language model
choosing among application-specific expert skills or synthesizing final answers.
The user requested one expert per application, all available to each task agent,
with autonomous selection and combination.

Preparation exposed a v1 ingestion defect: the structured manifest declared a
body schema but did not map body through `fields`. Canonical adapters intentionally
retain explicitly mapped fields. The first preparation (`s1`) therefore held
985 title-only records (59,742 rendered characters), while raw source bodies
contain 6,291,040 characters. Its two technical model rehearsals are preserved
and excluded from benchmark results; no benchmark comparison was sealed or run.
An earlier UTF-8 verifier fault was also preserved and diagnosed by replaying the
same technical responses. Neither issue is a skill-quality observation.

Start `s2` from new inputs with `fields: {body: documentText}` and a corresponding
ontology property. Require exact raw-to-ledger body equality and full rendered
body presence in retrieval text for every record. Do not rewrite v1 prepared data
or sealed e6 evidence. Publish an additive scope correction for affected historical
title-based retrieval scores. Those scores cannot serve as a full-text baseline.

## Decision

Use the direct multi-family generator accepted in ADR 0103 to build ten immutable
Embeddings experts: one unified control and nine source-scoped experts for
Confluence, Fireflies, GitHub, Gmail, Google Drive, HubSpot, Jira, Linear, and Slack.
Keep source identity, the 985 original records, record chunking, the pinned MiniLM
revision, and hybrid consultation fixed. Generate application guidance from
source roles, never from benchmark questions or relevance annotations.

Compare two fixed skill-loading treatments with native Harbor 0.18.0:

- one unified generated expert;
- all nine source experts, with catalog metadata initially visible and full
  instructions loaded when the model opens a skill.

The model is Pi 0.84.2 / openai-codex/gpt-5.6-luna with low reasoning. Every one of
the forty exposed Enterprise questions receives a fresh session in each arm.
The native agent offers only skill opening, exact generated-helper hybrid search,
authoritative document reading, and answer submission. The model chooses sources,
query reformulations, and combinations. It receives no oracle routing hints.
This is a constrained agent evaluation, not the general Pi shell-agent treatment.

The knowledge executor runs without network access; model transport runs outside
that container and exposes no filesystem or general network tool to the model.
Provider authentication stays in an ignored project-local transport directory.
The verifier runs separately and is the only task environment receiving gold
answers, qrels, and all-source citation reference text. Native skill staging binds
the actual generated experts; generated helpers revalidate their immutable bytes.

Each question permits one attempt, no retries, eighteen model rounds, twelve
searches, twelve record reads, and forty tool calls. Each search returns ten
documents and each read returns at most 24,000 characters with explicit pagination.
Two trials per arm may execute concurrently. The maximum development population
is eighty native trials; provider or infrastructure failures remain errors.
Two new full-text native technical rehearsals precede sealing and use one separate, generic
two-source citation request. They are excluded from benchmark quality. Preserve
their original outputs and any superseding verifier-only technical audits.

The native primary metric is final-evidence nDCG@10 gated on citation integrity.
Report raw nDCG, reference recall, source coverage, exact citation validity,
selected/consulted/cited skills, tokens, estimated provider cost, and latency
separately. This metric is not answer correctness or the official full-corpus
Enterprise score. Partitioning also changes the retrieval candidate domain and
lexical statistics, so the observed treatment effect includes these effects.

Apply ADR 0109's solution-agnostic, counterbalanced semantic review after all
responses are frozen: the authored Enterprise answer facts are required points,
the reference answer supplies semantic context, and two independent high-reasoning
Luna reviews see reversed anonymous answer order. Preserve disagreement and use
the existing conservative consensus code. This remains automated, within-source
evidence, not independent human certification or an official leaderboard score.

This is a fixed comparison, with no evolution controller, candidate selection,
installation, or promotion. All forty questions belong to one already exposed
organization/source family. No independent validation or holdout is claimed or
opened. The dataset planner's mandatory evolution/validation allocation does not
apply to this non-evolution comparison; its authoring and verifier checks do.
Any feedback-driven improvement requires a separately declared study.

## Verification and publication

Require complete and disjoint source partitions, independent generated-expert
validation, deterministic reconstruction, matched native-helper retrieval parity,
raw-to-knowledge body fidelity (including Unicode),
task replay, valid alternative answers, adversarial verifier checks, and probes
from the actual executor before sealing the organizer study. Run the repository
coverage gate before implementation closure.

Keep generated skills, data, tasks, traces, credentials, and native jobs ignored.
Publish reviewed English aggregate reports by arm, application, question category,
and cost/time/accuracy, linked from the existing report catalog. Preserve e6 and
all prior study artifacts.

The [OpenAI function-calling contract](https://developers.openai.com/api/docs/guides/function-calling)
describes the model/tool request-response boundary. The exact Pi transport and
native Harbor adapter are frozen implementation inputs for this comparison.
