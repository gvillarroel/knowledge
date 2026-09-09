# ADR 0133: Version exact builder bindings in feasibility tasks

Date: 2026-09-09

Status: Accepted for prospective preparation; native execution still requires
terminal predecessors, independent review and a sealed fixed design.

## Context

[ADR 0132](0132-qualify-graphify-builder-before-consultation.md) proposes a fixed
Graphify builder feasibility trial over the existing EnterpriseRAG development
workload. Before dispatch, inspection of the actual public development verifier
identified a package-binding incompatibility: its only mutable skill path is
`assets/retrieval-profile.json`. Every builder file is bound to its original
SHA-256 value. The sealed Graphify candidate changes one builder function in
`assets/families/graphify/builder/scripts/_graphify_projection.py`.

The unchanged verifier would reject that exact candidate as frozen-file drift,
regardless of whether its construction and retrieval behavior were correct.
No feasibility trial has been dispatched. The first native proposal remains
unregistered and must be preserved as superseded preparation.

## Decision

Version the feasibility task prospectively. Change only the expected SHA-256
value of the one changed builder file in `tests/contract.json`. Bind it to the
complete, exact sealed candidate before design sealing. Preserve the task's
other files byte for byte and every other parsed contract value exactly.

Keep the original questions, relevance references, source identities, images,
runtime bridge, verifier/scoring code, routes, attempts, resource limits and
network restrictions. Do not add the builder path to `mutable_skill_paths`,
relax the verifier, or allow arbitrary replacement content. The new task has
its own checksum; the original task and failed original job remain immutable.

This supersedes only ADR 0132's requirement that the task bytes themselves be
unchanged. The workload and all outcome checks remain unchanged. The new
contract binds the intended fixed construction treatment explicitly.

Before admission, independently verify the exact original-versus-versioned
contract delta and complete task trees, source/staged/Harbor-locked package
identity, runtime/import bindings, the public artifact-parity and negative
fixtures, and current executor isolation. Any other drift rejects preparation.
The single native feasibility-trial cap is shared across superseded proposals;
creating a proposal version adds no trial or retry allowance.

If feasibility qualifies, the later consultation study must apply the same
explicit package-binding versioning wherever the complete aggregate reference
contains the revised Graphify asset, including other families' contracts.
Independent private-task custody remains with the curator. Never read or amend
private task content from the evolution workspace. Preserve original exposure,
attempts, unavailable profiles and counters, and require the owning native
qualification/replay gates for the new actual package identities.

All-eight joint replay, one frozen bundle, paired all-500 recalculation and
the whole-bundle one-way private acceptance gate remain required. A versioned
package binding supplies no retrieval score, speed ratio, independent acceptance,
promotion or installation.

## Evidence and consequences

The public development verifier's existing `evaluate` function rejects a
submitted nonmutable file whose digest differs from its expected value. The
prepared package comparison identifies exactly the one changed Graphify file.
An append-only preparation receipt records the original and new task-file
commitments and verifies that the sole semantic contract change is that digest.
These checks are preparation evidence, not a native evaluation result.

This correction prevents a predictable binding rejection without weakening
source integrity or presenting a changed task as its original version.
