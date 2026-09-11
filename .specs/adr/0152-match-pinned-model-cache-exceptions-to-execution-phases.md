# Match pinned model-cache exceptions to execution phases

Date: 2026-09-11.

Status: Accepted for isolated prospective source correction. The tested policy
copy is inert; it does not restart E13 or provide current execution admission.

## Context

The [E13 native report](../../evaluations/reports/evolution/e13/turso-baseline-and-controller-stop-001/README.md)
preserves one completed Turso reference followed by a shared controller stop.
The captured current-agent ownership check passed, but the pinned read-only
model cache remained flagged through its historical directory ancestor.
Its exception named `preparation` and `execution`, while the classifier used
`development`. No recorded private release or reserved-private mount explained
the denial.

## Decision

Change only the specific pinned model-cache phase declaration from
`["preparation", "execution"]` to
`["preparation", "development", "recalculation", "validation"]`.
Retain its exact canonical source and target, read-only requirement, current
native ownership, resources, private-input checks and shared stop. Do not clear
historical or private conflicts generally when another ownership check passes.

Use captured observations and invented negative cases with the actual pure
classifier and unchanged container/mount decision blocks to test this boundary.
Reusing captured ownership evidence in that test does not establish fresh
runtime admission. Preparation must still reject an active native container,
and unsupported phases must receive no cache exception.

Preserve frozen E13 sources and the original failed invocation. E13 is stopped
at ledger sequence 16. Its one completed Turso generation-zero baseline retains
its original job, task, skill, profile and once-consumed allocation identity.
A future continuation must explicitly declare and independently review any
use of that exact historical starting-role evidence through the native owner.
Do not repeat it, treat it as changed-identity fitness, erase its cost or infer
complete Turso qualification from one role. This ADR does not implement that
continuation procedure.

All opportunity counts and the final endpoint from
[ADR 0150](0150-continue-enterprise-searches-by-family-readiness.md) remain:
91 cumulative claims, five open family searches, 373 maximum additional
family-bound claims, unchanged pending and Entity first-measurement identities,
all eight families, joint replay, all-500 comparison and independent acceptance.

## Evidence and consequences

The isolated correction changes one parsed field; exact reverse byte parity
confirms that every other byte remains unchanged. All **13 offline tests**
passed, including the captured old-denied/new-allowed development case and
denials for writable, broader, wrong-target, descendant, unowned, reserved-private
and traversal cases. No observer, full guard, fresh native ownership/resource
verification or benchmark workload ran in this suite.

Safe receipt SHA-256:
`1d64f08596dcf58d0b8526e3680d272d08ffc5e107e3fc0aff2c712150be0032`.
Software result:
`ffac6482bf31600f3094768d918bdec6ff359368f885cb784444b13c3e01a082`.
Corrected policy source:
`54b4c1e3cc63f3e1addcbf3c8f3358b85ed574266e17cc6c4641fe6023ef35a8`.
The [public correction summary](../../evaluations/reports/evolution/e13/turso-baseline-and-controller-stop-001/cache-phase-correction.json)
binds these checks without publishing the private policy or captured raw data.

The isolated policy still has its original routing. Operational integration
requires versioned truthful routing, the existing design/custody and actual
registered-lock checks, and current admission. Passing these software tests
establishes the specific declaration behavior; it adds no retrieval gain,
new champion or live feasibility result.
