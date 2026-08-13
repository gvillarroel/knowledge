# ADR 0099: Package Strategy-Specific Knowledge Visualizers as External Read-Only Skills

## Status

Accepted on 2026-08-09.

The Classical visual language is an approval candidate. The architectural
boundary and staged strategy-by-strategy delivery are accepted.

## Context

Semantic OKF packages preserve an authoritative semantic core and may add a
strategy-specific derived projection. Users need to see what a packaged
knowledge skill contains without adding viewer assets, caches, databases, or
application state to the knowledge directory itself.

A generic graph viewer would underuse the distinct metadata produced by each
strategy. In particular, the Classical strategy persists exact passages,
BM25 corpus statistics, deterministic topic communities, PPMI term
associations, source selection, retrieval parameters, build reports, and
artifact hashes. Treating all strategies as one generic node-and-edge schema
would hide important distinctions and could incorrectly present statistical
signals as semantic facts.

## Decision

- Ship one standalone `visualize-semantic-okf-<strategy>` skill for each
  supported knowledge strategy.
- Develop and approve one strategy at a time. Begin with Classical and do not
  establish the visual language of another strategy until the Classical view
  has been reviewed.
- Treat the knowledge directory as immutable input. Require an absent,
  disjoint output directory and never install viewer files into the knowledge
  package.
- Generate a self-contained offline atlas consisting of `index.html`,
  `projection.json`, and `receipt.json`. Do not require a CDN, application
  server, model, database, or sibling skill at viewing time.
- Process every row in large strategy artifacts when computing aggregates,
  but embed bounded inspection projections instead of duplicating entire
  retrieval indexes in the browser payload. Preserve all compact identities,
  plans, reports, source declarations, validation metadata, and artifact
  bindings.
- Bind the external atlas to the source tree and generated files with SHA-256.
  Provide an independent validator and a no-write `--check` mode that require
  byte-identical deterministic regeneration.
- Give each visualizer a strategy-native primary view. For Classical, use
  topic communities as navigation, persisted PPMI edges as the association
  map, and representative exact passages as the route back to evidence.
- Keep authoritative semantic records and ontology declarations visually and
  verbally distinct from non-authoritative topics, BM25 values, and PPMI
  associations. Never synthesize unpersisted topic-to-topic edges.
- Expose source provenance, record types, publication years, attribute
  coverage, ontology declarations, validation state, algorithms, parameters,
  artifact sizes, and hashes in dedicated Sources and Integrity views.
- Reserve a Contradictions view for explicit source-declared contradiction
  relations and separately labeled strict review candidates. Apply the
  precision-first proposition-alignment and filtering contract in ADR 0100;
  broad claim-role or polarity matches are audit diagnostics, not queue rows.
  Never promote a heuristic pair to a confirmed contradiction. Preserve both
  record identities and evidence locators, and warn that scope, conditions,
  baselines, time, or definitions may reconcile the pair.
- Keep each visualizer package standalone under `skills/`, including its
  scripts, validator, reference contract, browser asset, and interface
  metadata.

## Consequences

- Users can inspect packaged knowledge with a portable external artifact while
  the knowledge itself remains clean and immutable.
- Each strategy can emphasize the metadata that actually explains its
  retrieval behavior instead of conforming to a misleading universal graph.
- Visual review becomes a deliberate gate before the next strategy is built.
- Large indexes are fully accounted for in aggregates without forcing every
  raw token or passage body into the browser.
- Users gain a focused inconsistency-review queue while source-declared
  relations, strict review candidates, and rejected lexical tensions remain
  distinguishable.
- Each strategy maintains some duplicated viewer infrastructure and needs its
  own portability, determinism, interaction, and visual-regression checks.
- The atlas explains stored knowledge and discovery metadata; it does not
  promote a retrieval signal into evidence or establish factual correctness.
