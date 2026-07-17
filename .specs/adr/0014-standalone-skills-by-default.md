---
adr: "0014"
title: "ADR 0014: Package Repository Skills as Standalone Units by Default"
summary: "Make every skill self-contained unless an explicit external tool, service, or user-supplied input is part of its public contract."
status: "Accepted"
date: "2026-07-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Agent Skills"
tags:
  - skills
  - standalone
  - portability
  - testing
---

# ADR 0014: Package Repository Skills as Standalone Units by Default

## Status

Accepted.

This decision generalizes the standalone packaging rules in ADR 0012 and ADR 0013 to every skill shipped by the repository.

## Context

Several skills were useful only while mounted inside this checkout. Their instructions sent an agent to root-level specifications, documentation, cables, source modules, evaluation fixtures, or sibling skills. One otherwise portable skill imported a Python package supplied only by the repository environment. These dependencies made the directory layout and installation order part of the runtime contract, even when the skill itself did not need them.

Some dependencies are intrinsic and should remain explicit. A CLI skill may require its named executable, an integration skill may require a remote service and credentials, and a project-projection skill may accept another repository as input. Those public inputs differ from hidden access to this repository or another skill package.

## Decision

Treat every direct `skills/<name>/` directory containing `SKILL.md` as a standalone package by default.

- Keep every required instruction, reference, runtime script, validator, asset, and dependency declaration inside the skill directory.
- Do not require a sibling skill, a repository-relative helper, root documentation, source modules, fixtures, evaluation artifacts, or a particular checkout layout.
- Declare required external executables, services, credentials, browsers, and user-supplied data as public inputs. Provide an in-scope preflight or diagnostic when one is unavailable.
- Treat files in a target project as user-supplied inputs only when operating on projects is part of the skill's public purpose; do not embed semantics specific to this repository in a generic generator.
- Prefer a small package-local implementation or deliberate duplication over a runtime dependency on another skill. Coordinate duplicated format rules through tests rather than imports.
- Keep optional performance tools and model-assisted workflows optional. The documented baseline must continue to work without them.
- Verify local links and dependency declarations, copy every skill outside the repository, and run each bundled entry point from the copied package. Add deeper copied-package tests for mutation or generation workflows where `--help` is insufficient.
- Keep frozen historical evaluation snapshots immutable. Active generated projections and intentionally pinned active overlays may be refreshed through their own reproducible workflows.

Instruction-only skills satisfy this contract when their complete operational guidance is inside `SKILL.md` and package-local references. They may rely on the explicitly named external tool, but must not tell the agent to recover essential behavior from this repository.

## Consequences

Positive:

- skills can be installed, copied, evaluated, and upgraded independently;
- hidden checkout assumptions fail in tests instead of at user runtime;
- explicit external requirements are distinguishable from accidental coupling;
- trigger and authority boundaries remain understandable without sibling handoffs.

Negative:

- shared validators and format rules may be duplicated;
- every package must maintain its own dependency metadata and portability tests;
- generic generators cannot rely on convenient project-specific defaults;
- coordinated format changes may require edits in more than one independent package.
