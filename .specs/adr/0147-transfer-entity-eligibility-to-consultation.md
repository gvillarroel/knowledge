# Transfer Entity eligibility checks to consultation with the builder frozen

Status: Accepted as an isolated software candidate; native qualification and
independent package acceptance remain pending.

Date: 2026-09-11

## Context

The Entity builder and consultant independently derive candidate entities
during complete validation. The builder already uses prefix counts to reject
n-gram windows containing disallowed tokens. A source comparison of the frozen
lifetime package found that the consultant differed only in this extraction
function: it still repeated membership and digit checks for overlapping windows.

The previous full EnterpriseRAG attempt timed out after successful intermediate
build and standalone-validation logs. That evidence does not identify the
precise timeout phase or establish a causal performance gain from this transfer.

## Decision

Charge one consultation proposal, `entity-consultant-ngram-eligibility-001`,
under [ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md).
The total becomes 89 of 585, including six of Entity's 80 claims. Preserve all
seven consumed construction measurements and the existing family stopping rules.

Freeze the complete builder and change only the consultant's
`_candidate_statistics` body, transferring the implementation accepted for
isolated builder testing in [ADR 0144](0144-reuse-token-eligibility-in-entity-candidate-extraction.md).
Preserve exclusions, window order, counts, score arithmetic, deterministic ties,
query routes and independent validation. Do not bypass deep rederivation.

Validate the complete candidate with the maintained realizer, exact independent
extraction oracles, artifact/query parity and corruption rejection in both
schemas and both layouts. Keep the software cases separate from benchmark tasks.

For a consultation-only runtime check, reuse the retained processed snapshot
and its existing deep-validation response. Supply only the consultant and that
snapshot as the skill/data inputs. Inspect effective container mounts and mask
any image-baked raw-data directory with an empty read-only mount before subject
execution. Preserve a refused preparation rather than rewriting its result.

## Evidence and consequences

The [software report](../../evaluations/reports/evolution/e11/entity-consultant-ngram-eligibility-001/README.md)
records seven passed checks, 4,080 exact comparisons and 192 integration child
commands. The corrected pinned-runtime check executed one deep consultation on
1,024 synthetic records, preserving its exact response and all 19 snapshot files.
The first preflight refused before starting the consultant; no quality miss or
additional proposal is assigned to that environment failure.

The sealed candidate is
`sha256:cdbcc0e33b9ba6235f0ae6d7505826c0ed71768e1497c468bf63a9b0810ed591`,
from parent
`sha256:810ca4eee999ce0c93f19a3b0302a31de6f28cfd9ba1ee09c39e6014c056ddb5`.
The other 251 package files are unchanged. Reduced predicate counts and one
instrumented runtime observation do not establish native feasibility or ranking
improvement. The exclusive first native measurement remains unassigned.

Native admission, the five remaining searches, joint replay, the final all-500
comparison and one-way independent whole-bundle acceptance remain required.
No canonical skill is promoted by this decision.
