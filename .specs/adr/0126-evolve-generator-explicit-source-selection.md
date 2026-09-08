# ADR 0126: Evolve the generator's explicit source selection

## Status

Accepted for a bounded technical evolution study on 2026-09-07. Canonical
promotion requires the frozen independent acceptance gate described below.
G1 subsequently stopped with an unavailable private gate. G2 confirms the exact
same precommitted candidate using a fresh independently authored cohort and the
supported native explicit-artifact-copy route. G2 accepted the candidate at 8/8
versus 6/8 on fresh validation, with no task regressions, and the exact four-file
delta was promoted. G1 evidence remains unchanged. See the
[accepted report](../../evaluations/reports/evolution/generator-g2/README.md).

## Context

ADR 0125 retained the useful ingestion lesson from the application-skill
experiment: declaring a structured field in `schema` does not include it in
knowledge. The canonical adapters intentionally retain the fields selected by
`fields`. The universal generator's instructions already explain this boundary,
but its executable can still publish a title-only expert when a caller forgets
to make that selection. Record-count and artifact-integrity checks can pass in
that situation. The user asked to evolve the skill that generates skills.

## Decision

Evolve `build-semantic-okf-knowledge-skill` through a builder-only treatment.
Require an explicit `fields` object for JSON/CSV declarations whose schemas
contain fields beyond identity and title. Keep partial selections authoritative;
an explicit empty object remains a valid request for title-only knowledge.
Reject an absent selection before constructing or publishing an expert, with an
actionable diagnostic. Leave the eight canonical builder/consultant packages,
family routes, and generated consultation templates byte-identical.

Add a deterministic, digest-bound `references/source-coverage.json` to successful
builds. Report declared, identity, mapped and omitted fields per source, explicit
selection status, record count, non-null and null mapped value counts, and
normalized body character counts. Distinguish native nonstructured sources and
derived source identities. State that raw source fidelity is not verified.
This receipt makes selection inspectable; it does not certify raw-to-ledger text
equality or complete encoder context coverage. Keep those independent checks.

## Evidence boundary

Study `generator-evolution-g1` uses `harbor-population-search` with the incoming
complete generator as baseline. Register eight development cases in two exposed
source/schema families and eight independently authored private cases in three
families. Lock both cohorts, the protocol, baseline, and independent curator review
before any candidate generation or comparison. Preserve separate native verifier
containers, read-only source mounts, offline execution, exact native skill locks,
one attempt per task, and zero built-in retries. Shared-host curator confidentiality
is a role boundary rather than an OS security boundary.

The deterministic executor calls the generator CLI directly. It makes no model
calls and does not measure autonomous skill selection or instruction adherence.
Primary reward checks the construction contract; the new receipt's existence is
only a secondary metric. Require unchanged source bytes on every task. Allow at
most three content-changing development generations with the original baseline,
then freeze one fully passing improvement before a single private gate. Require
private mean gain at least 0.01 and no task regressions. Private feedback cannot
drive another generation in the same study. A failed gate retains the baseline.

The population is a small technical pilot. Report descriptive paired results,
independent family counts, and limitations. No result from this study is a new
EnterpriseRAG answer-quality score, a retrieval-ranking gain, or statistical proof
of generalization. Keep tasks, sources, candidates and raw evidence ignored; retain
reviewed English aggregate reports and the useful reusable generator changes.

G1's private native jobs aborted with a host EIO during artifact collection before
verification. No private scores were observed; this does not count as a semantic
failure or justify rerunning consumed tasks. A dummy native experiment verified
that explicitly mapping `/logs/artifacts` to `published-artifacts` bypasses the
failing mounted-inspection branch and preserves exact files in a separate verifier
container. The filesystem root cause remains unproven. G2 must seal fresh validation
and the corrected transport before its one fixed development comparison, preserve
both G1 bundle digests, and forbid further candidate mutation. It permits 16
development plus 16 validation trials and a separate two-task public preflight.

## Consequences

Some previously accepted generator inputs will need an explicit field selection.
The migration is to review the intended content and add the corresponding map,
or use an explicit empty map for title-only knowledge. Existing frozen experts
and historical evidence remain unchanged. Knowledge and consultation parity,
portable generation, deterministic rebuilding, meaningful regression tests and
the repository coverage gate remain mandatory before implementation closure.

See the [knowledge skill evolution playbook](../../docs/knowledge-skill-evolution-playbook.md)
and [direct generator contract](../../skills/build-semantic-okf-knowledge-skill/references/expert-contract.md).
