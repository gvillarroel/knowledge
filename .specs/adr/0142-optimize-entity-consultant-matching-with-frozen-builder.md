# Optimize Entity consultant matching with the builder frozen

Status: Accepted for isolated candidate preparation and software validation;
complete EnterpriseRAG qualification and promotion remain pending.

Date: 2026-09-10

## Context

The [builder token automaton](0141-use-token-automaton-for-exact-entity-mentions.md)
preserves exact mention matching on the declared public software fixtures.
Its [original native measurement](../../evaluations/reports/evolution/e11/entity-token-automaton-native-001/README.md)
nevertheless reached the unchanged 3,600-second agent limit without a submitted
response or retrieval score. That attempt remains consumed.

An independent source review confirms that the exact frozen workload loads
the separate Entity consultant model, then performs deep snapshot validation
before returning its four query routes. That validation rederives the complete
projection, including mentions. The consultant still enumerates alias-length
tuple windows. The builder and consultant model files are identical outside
`derive_mentions`; the builder optimization does not change the function that
the consultant imports.

Deep snapshot setup occurs once before the route/query loop. The source review
does not establish which phase timed out or its share of execution time.
It also distinguishes the computational workload bridge from the separate
custody authenticator. Neither source inspection nor the small software fixture
establishes a whole-workload speed or memory improvement.

## Decision

Reserve `entity-consultant-token-automaton-001` as one additional, nonrefundable
Entity proposal under [ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md).
Cumulative claims become **86 of 585**, including **3 of Entity Graph's 80**.
Preserve all four consumed construction first measurements, both historical
pending first measurements, closed and unavailable entries, five catalog
rounds, and the three-consecutive-evaluable-miss rule. Unused closed-family
capacity remains nontransferable.

Use the complete builder-automaton package as the frozen parent. Change only
`assets/families/entity-graph/consultant/scripts/_entity_graph_model.py`, and
only its `derive_mentions` body. Transfer the already implemented sparse token
automaton with failure links and linked suffix outputs into that function.
Keep all builder files and the other 251 package files byte-identical.
This is a separate consultation runtime treatment with construction frozen.

Preserve tokenization, aliases, duplicate bindings, overlapping occurrences,
counts, stable identifiers, output ordering, all four retrieval routes and
ranking parameters. Preserve independent complete rederivation and every
integrity, corruption and error check. Do not replace deep validation with a
cache, remove a build, enlarge resources, truncate documents, or change other
families.

Declare seven software checks before realization: complete single-function
scope, skill format, ordered matching with independent count oracles, and four
complete schema/layout integration cells. The latter compare complete builds,
rebuilds, independent validation, exact artifacts and query payloads. Both the
builder and consultant must reject the declared corruptions.

The new first-measurement identity is exclusive and unassigned. Any later task
version must bind the changed consultant digest in both `skill_files` and
`imported_candidate_modules`, preserving all other task values, deep validation
and the original resource and attempt limits. Existing studies and controllers
must not be edited or restarted.

## Evidence and consequences

The frozen parent is
`sha256:6414475543ea62006f6cc2ea7bb330577279b90bf775154fe0596854143119f4`.
The independent source-review receipt is
`23fdfd3a548276b418219dd766794d638e880938c9e1007bf1d9f39258d42f92`.
The nonrefundable reservation is
`3ed4d817ba824f3d4e776373da4cb6793771fd130a5551572e1c7a5a3ffdfcfe`;
the declared realization configuration is
`a7d0f7fcbd855cfc8cdd4515727aea75259e65b23e85f4f121e710a5b3681a77`.

Keep the candidate isolated until the declared qualification and acceptance
gates pass. Exact software equivalence can support a new measurement, but it
cannot supply a missing EnterpriseRAG score or select a production winner.
Five family searches, composed-reference qualification, paired all-500
measurement and independent whole-bundle acceptance remain unfinished.

The [realized candidate report](../../evaluations/reports/evolution/e11/entity-consultant-token-automaton-001/README.md)
records seven passed checks, 1,120 ordered comparisons, 16 complete builds,
16 independent validations, 32 nonempty paired queries, eight deep consultant
inspections and 40 corruption rejections at each of the builder and consultant
layers. Sealing and subsequent verification completed without rerunning those
validation commands. The candidate is
`sha256:15d7fd9ffc0e83a1585a901bf6a2ee8133d2c58407130e3c0918cb7acdf39cbc`.
The pinned native-runtime fixture and full-workload measurement remain pending.
