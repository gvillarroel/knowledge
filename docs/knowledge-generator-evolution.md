# Evolving the knowledge-skill generator

The canonical `build-semantic-okf-knowledge-skill` generates one portable expert
for any of the eight registered Semantic OKF families. Generator evolution is a
separate treatment from changing an expert's consultation strategy. The accepted generator addresses
an ingestion failure observed during the completed Enterprise application-skill
experiment: a schema can declare document text while the selected field map
retains only titles.

The candidate described below passed independent acceptance in G2 and is now
the canonical generator. Both development and fresh independent validation
improved from 6/8 to 8/8, with no regressions. G1's private gate had aborted before scoring.
See the [G1 construction report](../evaluations/reports/evolution/generator-g1/README.md)
for that preserved interruption and the
[G2 confirmation report](../evaluations/reports/evolution/generator-g2/README.md)
for the accepted result, source-format comparison and CTA. The
[decision record](../.specs/adr/0126-evolve-generator-explicit-source-selection.md)
defines the treatment and acceptance boundary.

## Deliberate structured source selection

Choose the fields that the expert should retain before generating it. For a
JSON/CSV source with a `body` field, an explicit selection can be:

```json
"fields": {"body": "documentText"}
```

The `documentText` datatype property must also be declared in the source
manifest's ontology using the appropriate domain and range. The schema still
declares the source's full typed shape. A partial field map intentionally omits
the remaining fields. Use an explicit empty map when title-only knowledge is
the intended artifact:

```json
"fields": {}
```

The generator requires this decision when a structured schema contains fields beyond
identity and title. It does not infer a field's importance from its name or
automatically widen a caller's selection. Native Markdown and RDF adapters keep
their existing content semantics. The complete CLI, required guidance headings,
family plans and runtime locks remain in the
[generator skill](../skills/build-semantic-okf-knowledge-skill/SKILL.md).

## Interpreting the generated receipt

`references/source-coverage.json` is part of the expert's existing digest-bound
artifact set. It records per-source selection scope, declared/mapped/omitted
fields, normalized records, non-null and null mapped values, and normalized body
character counts. Those counts include canonical rendering; they are not raw
document character counts.

The receipt explicitly sets `raw_source_fidelity_verified` to false. Inspect it
to detect omitted fields and unexpectedly small knowledge artifacts. For a claim
of complete document retention, also compare raw source values with the
normalized ledger and retrieval text using the adapter's rendering rules. The
retained [Enterprise full-text projection checks](enterprise-source-skills.md)
illustrate that additional check. Even complete storage does not establish that
a bounded embedding encoder processed every token.

## Evaluation and reuse

The evolution compares the exact incoming generator with a complete candidate through native
Harbor CLI execution, using disjoint development and independently authored
validation cohorts. It tests valid and rejected construction, source preservation,
deep artifact integrity and consultant preservation. The receipt is a secondary
metric; primary correctness does not fail an old generator simply because the
new receipt filename is absent.

The deterministic executor makes zero language-model calls. These are construction
results, with no new EnterpriseRAG answer score or retrieval-ranking claim. The
eight-family public regression verifies knowledge and consultant byte equality,
deep validation, deterministic rebuilds, native queries and physical evidence.
A completed private gate can supply technical transfer evidence with an explicit
shared-host role-isolation limitation. It does not establish population-level
statistical confidence. G1's unavailable gate supplies no acceptance evidence;
G2's fresh cohort supplies the accepted one-way comparison. Both versions passed
the five successful-build contracts. The gain comes from detecting two missing
field-selection decisions before publishing an expert.

The reusable [native construction adapter](../evaluations/integrated-semantic-okf-knowledge-skill/evolution/README.md)
documents task materialization, source isolation, deterministic replay and explicit
native artifact copying. Its tests are separate from construction fitness.

For another evolution, follow the [playbook](knowledge-skill-evolution-playbook.md),
freeze a new baseline and disjoint cohorts before scoring, and open validation only
after one finalist is frozen. Do not reuse a consumed private cohort for another
candidate or import its outcomes into mutation notes. Sources, generated experts,
task trees and native jobs remain ignored. Keep only reviewed aggregate results
and useful reusable implementation in the repository.

[Documentation index](README.md)
