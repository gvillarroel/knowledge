# EnterpriseRAG campaign closure and retained skill release

Date: 2026-09-18. The user requested final closure and publication of the best
supported skill versions. The campaign is closed. The canonical skills already
contain the accepted generator improvement and tested maintenance changes;
there is no independently accepted EnterpriseRAG candidate waiting to replace
them. This release retains those exact packages and records their identities
in the [release inventory](../evaluations/reports/releases/enterprise-skills-20260918.json).

## What remains in the skills

The [universal knowledge-skill generator](../skills/build-semantic-okf-knowledge-skill/SKILL.md)
retains G2's explicit structured-field selection and source-coverage receipt.
Its [independent construction comparison](../evaluations/reports/evolution/generator-g2/README.md)
improved from **6/8 to 8/8**, with zero task regressions. The four promoted files
remain byte-identical to their published implementation in commit
`d52f3c8b3df0d4829797ce28fcd50b03e1b32bbe`.

Later maintenance in `fe854cbfe3d268444ac5c2a7e17c1701b38c87fb` avoids repeated
provenance-graph copies and packed-document reads while retaining exact evidence
checks and rejecting concurrent mutation. The current complete package therefore
has its own release identity; it is not relabeled with G2's older whole-bundle
digest. The release inventory binds the current Git trees and file content.

All eight matched canonical pairs remain available, and every vendored copy in
the generator matches its canonical package byte-for-byte:

| Family | Builder | Consultant |
| --- | --- | --- |
| Legacy | [Build](../skills/build-semantic-okf/SKILL.md) | [Consult](../skills/consult-semantic-okf/SKILL.md) |
| Embeddings | [Build](../skills/build-semantic-okf-embeddings/SKILL.md) | [Consult](../skills/consult-semantic-okf-embeddings/SKILL.md) |
| Classical | [Build](../skills/build-semantic-okf-classical/SKILL.md) | [Consult](../skills/consult-semantic-okf-classical/SKILL.md) |
| Adaptive | [Build](../skills/build-semantic-okf-adaptive/SKILL.md) | [Consult](../skills/consult-semantic-okf-adaptive/SKILL.md) |
| Entity Graph | [Build](../skills/build-semantic-okf-entity-graph/SKILL.md) | [Consult](../skills/consult-semantic-okf-entity-graph/SKILL.md) |
| Ensemble | [Build](../skills/build-semantic-okf-ensemble/SKILL.md) | [Consult](../skills/consult-semantic-okf-ensemble/SKILL.md) |
| Graphify | [Build](../skills/build-semantic-okf-graphify/SKILL.md) | [Consult](../skills/consult-semantic-okf-graphify/SKILL.md) |
| Turso | [Build](../skills/build-semantic-okf-turso/SKILL.md) | [Consult](../skills/consult-semantic-okf-turso/SKILL.md) |

## Treatment of the experimental versions

The [E15 terminal decision](../evaluations/reports/evolution/e15/terminal-001/README.md)
preserves E14's six retained development results. E15 was rejected before
execution; [E16](../evaluations/reports/evolution/e16/terminal-001/README.md)
closed after two original timeouts without a selection or private release.
Those profiles and runtime candidates remain historical experimental evidence.
Their development gains do not authorize installing them as accepted defaults.
Legacy and Turso's experiment-specific query wrappers also have a distinct
[generated-expert delivery boundary](enterprise-stratified-evolution.md).

The subsequent [public retrieval catalog](../evaluations/reports/datasets/enterprise-primary-route-001/README.md)
contains seven valid strategy observations on 500 questions and 6,000 complete
documents. Entity Graph completed; Ensemble reached its three-hour limit after
264 completed queries. These observations do not complete the earlier private
acceptance gate, establish a new skill promotion, or measure Luna answer quality.
The [application/category](../evaluations/reports/datasets/enterprise-primary-route-001/groups.md),
[CTA](../evaluations/reports/datasets/enterprise-primary-route-001/cta.md) and
[dataset-scope](../evaluations/reports/datasets/enterprise-primary-route-001/datasets.md)
reports retain their original metric contracts.

There is no automatic continuation or pending campaign launch. Closure does not
claim that every possible improvement was exhausted. Unmeasured hypotheses,
including repeated Adaptive/Ensemble query work, stay documented in their
[original scope](../evaluations/reports/datasets/enterprise-primary-route-001/phases.md).
Any future evolution is separate work with fresh eligibility and acceptance.

## Release verification

The inventory records checks performed for this closure, separately from
historical benchmark results. It covers the generator and sixteen canonical
packages, vendored parity, the complete generator test suite, all three dataset
descriptors, package validation, and the required application coverage gate.
All **17** package validations and **16** canonical/vendor comparisons passed.
The generator suite passed **20 tests**; the application gate passed **1,730
tests and 378 subtests**, with **90.5%** coverage against the required **80%**.
Dataset payloads, generated experts, candidates, private evidence and native
jobs remain ignored. Historical reports and sealed study evidence are preserved.

[Decision record](../.specs/adr/0171-close-enterprise-campaign-with-accepted-skills.md)
· [Documentation index](README.md)
