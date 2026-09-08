# ADR 0120: Preflight native profile and complete merge lineage

Status: Accepted. Date: 2026-09-06.

## Context

ADR 0117 allows one optional generation of compatible, evidence-backed profile
merges from the preceding native Pareto archive. The four-child limit makes the
owner's merge-plan order material. A generation seal alone does not establish
that the entire suggested plan is intact: the installed owner's seal payload
includes archived candidates, their vectors and the evaluation profile, but
excludes `mergePlans`.

An independent synthetic forward test demonstrated that omitted or reordered
merge plans can retain a valid native seal while changing the first four
children. It also demonstrated that a package-and-seal check without a selected
candidate does not establish unchanged promotion rules. These are gaps in
campaign preparation checks, not reasons to alter native results or relax the
frozen evaluation protocol.

The installed owner's doctor checks the runtime and ordinary configuration.
Its complete previous-generation profile check happens when it builds the next
archive, after executing candidate jobs. Detecting profile drift at that point
would waste a full generation of work.

## Decision

Before realizing a supported merge, verify every current parent package against
its native development digest, then use the installed owner's profile builder
to compare the exact current evaluation and promotion profile with the sealed
preceding archive. Require the profile payload and digest to agree. Repeat the
native profile and previous-generation ancestry checks on the prepared next
configuration before starting any native job.

Check the full ordered list of suggested pairs against the sealed archive's
ordered members and their existing complementary vectors. Both parents must
win at least one recorded development cell, and the supplied strength lists
must match those vectors. Reject added, omitted, duplicated or reordered pairs.
Apply the existing four-child budget only after that consistency check; skip
baseline-plus-candidate pairs because they add no mechanism and would rerun a
prior candidate.

Realize only exact non-conflicting unions of the frozen operation declarations.
Bind both parent identities and native digests, the physical parent realizer
digest, source archive SHA-256, native generation seal and exact mutation
contract. Keep every previous artifact intact and use fresh output paths.

Qualify preparation changes with an independent isolated forward test. It may
call read-only installed-owner APIs and use explicitly synthetic fixtures, but
must not manufacture a live study archive, run new evaluations, open private
validation or modify a frozen orchestration file.

## Consequences

The native owner continues to score, archive and validate candidate generations.
Campaign preparation verifies the completeness of its input suggestions and
calls existing owner checks earlier; it does not introduce another optimizer,
new candidate mechanisms or a different selection rule. The running generation,
its task contracts and all sealed validation commitments remain unchanged.

These checks extend the workflow qualification in
[ADR 0119](0119-declare-native-agent-identity-and-qualify-the-owning-controller.md).
See the [operating guide](../../docs/retrieval-profile-evolution.md) and
[construction-profile decision](0117-evolve-retrieval-construction-profiles-with-native-harbor.md).

## Source preservation, 2026-09-07

Retain exact copies of the e5 normalization, merge-preparation and generation-
registration helpers in the [campaign source archive](../../evaluations/skill-evolution/campaign-tools/README.md),
with a SHA-256 manifest. Their runtime placement remains the registered ignored
workspace. Archiving their code does not change the running study or permit
replaying completed stages.

Use directory-local Git attributes to preserve LF line endings for these source
files and their metadata. Check that staged and checkout-filtered code bytes
match the source manifest; review evidence must not silently refer to a different
line-ending representation on another platform.

## Descriptive cross-generation publication, 2026-09-07

Compose the two complete, registered e5 development reports before private
validation. The [campaign reporter](../../evaluations/skill-evolution/aggregate_campaign.py)
preserves generation identities, source commitments, native means, qualification,
failed denominators and per-cell timings. It does not average repeated baselines,
pool query percentiles, create a combined native archive, or choose a finalist.
Only the final generation's qualified native archive remains eligible for the
frozen selection rule. This cross-generation development projection is completed
and registered before the private release; its output remains immutable. Terminal
validation publication follows its separate allowed-aggregate contract.

The combined catalog provides one dataset/skill/run/CTA entry point while retaining
both original generation reports. Field allowlists and fixed dataset/family labels
prevent unreviewed payload columns or paths from propagating into this catalog.
Focused synthetic checks cover mixed profiles, incomplete trials, duplicate rows,
wrong scales, path labels, failed profiles, omitted payloads and terminal boundaries.
