# ADR 0097: Canonicalize source and evaluation artifacts

## Status

Accepted on 2026-08-03.

## Context

The repository had both `evaluation/` and `evaluations/`, a root fixture tree,
tracked temporary workspaces, root-level Harbor junctions, and a checked-in
`okf/skills/` projection that duplicated every authoritative skill package.
Raw candidate bundles and trial outputs were visible beside source files while
the durable summaries that explained their outcomes were scattered across
individual studies.

ADR 0003 intentionally checked in the generated project OKF projection. That
made interoperability explicit, but it also created a second, mechanically
generated representation of every `skills/*/SKILL.md`. ADR 0063 later
established that raw and generated evaluation artifacts should remain local
while compact reviewed summaries stay visible to Git.

## Decision

- Use `evaluations/` as the only repository-level evaluation workspace.
- Keep evaluation fixtures below the study that consumes them instead of a
  root `fixtures/` directory.
- Keep authoritative skill packages only below `skills/`.
- Generate the strict project-and-skill OKF projection on demand under the
  ignored `build/okf/` directory. The projector must support arbitrary output
  locations with correct relative provenance links and must be tested by
  building and validating a fresh bundle.
- Ignore and untrack root-local trial workspaces, including `tmp/`,
  `baseline-skill/`, `generation-*`, `.tantivy-*`, and their local logs. Their
  append-only source artifacts remain below ignored evaluation artifact trees.
- Preserve compact, reviewed experiment summaries and decision records in Git.
  Use `evaluations/SKILL-EXPLORATION-AND-EVOLUTION.md` as the human entry point
  for skill comparison and evolution history.

This supersedes ADR 0003 only for the checked-in location and drift-checking of
the generated project bundle. ADR 0003's native-frontmatter boundary and strict
OKF projection semantics remain accepted. It applies ADR 0063's local-artifact
policy to the previously tracked root workspaces.

## Consequences

- There is one evaluation root and one authoritative skill tree.
- Repository status no longer expands thousands of local Harbor trial files or
  generated skill copies.
- A project OKF bundle is still deterministic and validated, but consumers
  build it when needed instead of treating generated Markdown as source.
- Exact raw trials remain local and append-only; Git history carries the
  reviewed conclusions, metrics, limitations, and decision provenance needed
  to understand what was attempted.
- Consumers that require a committed OKF artifact must publish a separately
  generated release artifact rather than reintroducing a second source tree.
