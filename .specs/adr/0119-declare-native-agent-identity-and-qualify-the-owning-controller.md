# ADR 0119: Declare native agent identity and qualify the owning controller

Status: Accepted. Date: 2026-09-06.

## Context

Study e4 completed all 32 native baseline trials with zero execution errors and
complete evidence integrity. The native reporter retained 32 diagnostic rewards.
The reflective Pareto owner then rejected the declared-versus-observed agent
profile before launching a candidate or creating an archive. The JobConfig used
the correct custom import and model marker but left `agent.name` null; Harbor
recorded the custom agent's truthful name, `skill-retrieval`.

Native Harbor execution and the standalone reporter permit that import-based
configuration. The owning evolver requires an explicit declared name matching
the observation. A successful task smoke therefore did not qualify the complete
development workflow. This is a configuration/provenance failure, not a missing
retrieval score or a semantic retry opportunity.

## Decision

Declare `name: skill-retrieval` alongside the unchanged
`import_path: native_agent:SkillRetrievalAgent` and
`model_name: local/deterministic-retrieval-v1` in every new development and
validation JobConfig. Keep the actual agent implementation, version, runtime,
model, scoring, candidate operations and acceptance rules unchanged.

Before another internal study begins, an independent source-generic native
smoke must exercise the installed owning controller with baseline and a real
candidate. Require successful baseline consolidation, candidate dispatch and a
valid native archive, including declared/observed identity parity. A doctor
check, standalone Harbor job or standalone result report is insufficient for
that qualification. Preserve the full smoke evidence and bind it in the new
study's design review.

Preserve e4's original configs, locks, trial results, diagnostic scores and
failed controller log. Stop its downstream stages without releasing validation.
Publish its baseline only as a retrospective native diagnostic excluded from
evolution selection and promotion. Never rewrite those native artifacts or
manufacture an accepted archive or effective job.

The next campaign has a fresh identity and sealed protocol. Reuse the unchanged
historical development portfolio and predeclared hypotheses; do not infer new
mutations from this configuration failure. The private validation portfolio is
still unconsumed and unavailable to diagnosis. Report all prior attempts and
the extra qualification work separately from the new campaign's trial budget.

## Consequences

Identity parity becomes an explicit preflight contract at the orchestration
boundary. The native controller continues to own admissibility and comparison;
the adapter does not weaken that check. Baseline diagnostics remain useful
descriptions of completed retrieval work while carrying their exclusion from
candidate ranking and promotion.

See [ADR 0117](0117-evolve-retrieval-construction-profiles-with-native-harbor.md),
[the operating guide](../../docs/retrieval-profile-evolution.md), and
[the e4 diagnostic record](../../evaluations/reports/evolution/e4/README.md).
