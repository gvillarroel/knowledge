# Retrieval construction-profile study e4

[Evolution evidence](../README.md) · [Historical dataset rankings](../../README.md)
· [Operating guide](../../../../docs/retrieval-profile-evolution.md)

Status: **stopped after the completed native baseline**. All 32 baseline trials
finished with zero execution errors and complete evidence integrity. The owning
controller rejected the declared-versus-observed agent name before running any
candidate or creating an archive. These results are retrospective native
diagnostics excluded from evolution selection and promotion. Validation was
never released.

The JobConfig left the agent name null while correctly specifying the custom
import and local model marker. Harbor recorded the actual name `skill-retrieval`.
The strict owning-controller profile check requires those names to match.
[ADR 0119](../../../../.specs/adr/0119-declare-native-agent-identity-and-qualify-the-owning-controller.md)
requires a fresh identity-declared campaign and an independent smoke of the
complete controller path. Original configs, locks, metrics and failure logs
remain unchanged.

The standalone native reporter confirms **66.49% mean diagnostic nDCG@10** across
all 32 default-route cells. Thirteen cells reach the descriptive 0.8 cutoff and
nineteen do not; all 32 pass the separate integrity requirement. The baseline
took approximately 100 minutes of native wall time and reported zero model
tokens or provider charge. Four candidate profiles were realized but none was
evaluated, selected or promoted in e4.

The [complete diagnostic report](baseline-diagnostic/README.md) includes all
72 route aggregates, per-skill and per-dataset views, a comparative figure and
[cost/time/accuracy measurements](baseline-diagnostic/cta.md). Those publications
retain the owning-controller rejection explicitly.

## Registered comparison

| Development dataset | Queries | Documents | Skill families | Retrieval routes |
|---|---:|---:|---:|---:|
| EnterpriseRAG reduced corpus | 40 | 985 | 8 | 18 |
| Astro | 40 | 416 | 8 | 18 |
| Software architecture books | 40 | 18 | 8 | 18 |
| Data science / AI / ML books | 40 | 38 | 8 | 18 |

Generation zero compares the common baseline with four construction profiles:
pinned MiniLM embeddings, quarter-strength expansion, BM25 length normalization
of 0.25, and a title weight of 4.0. The primary measure is binary nDCG@10,
averaged equally over the 32 dataset-by-family default-route cells. All 18
routes are measured; their additional scores do not replace the declared
selection rule. The corresponding plans and mechanisms are documented in the
[profile guide](../../../../docs/retrieval-profile-evolution.md).

Each of the five profiles receives all 32 native trials. Every trial builds and
validates twice, checks byte-identical knowledge, executes every declared query
and route, and independently verifies returned evidence identities. Candidates
must pass integrity for every cell and have no errors to qualify. Missing or
failed cells remain visible and cannot create a favorable partial ranking.

The optional second generation permits at most four new merges supported by
complementary members of the native Pareto archive, plus the unchanged baseline.
The full study is bounded to two generations, nine unique profiles and at most
352 native trials. It makes no instruction-model calls; local computing still
has a resource cost. Actual native accounting and measured durations accompany
the completed results.

## Independent gate

FiQA and SciFact remain sealed during development. One frozen finalist may
consume the whole portfolio once, after achieving at least one percentage point
of mean development gain. Validation uses 12 queries and 985 reference-enriched
documents per source, with eight families per profile. Acceptance requires at
least one percentage point of mean gain, no cell regression, no execution error
and complete evidence integrity. If development produces no eligible gain,
baseline remains and the gate stays sealed.

No mutation, merge, reselection or semantic replay is permitted after release.
The small transfer gate does not establish statistical significance or official
benchmark performance. These retrieval scores are not comparable with the
[public EnterpriseRAG answer-quality leaderboard](../../../enterprise-rag-bench/reports/public-results-20260906.md).

## Correctness and provenance

All profiles share the independently qualified Graphify empty-heading identity
repair in [ADR 0118](../../../../.specs/adr/0118-normalize-empty-graphify-heading-identities-before-profile-evolution.md).
That repair is a separate correctness treatment. It cannot be credited to one
profile's ranking gains. The two earlier unscored campaigns and their failures
remain preserved in the [infrastructure lineage](../20260906-infrastructure.md).

- Frozen native baseline digest: `sha256:76017c96d858c73103c958d99bdcee9379aa1e1407b8c576d1c3720502a7f205`.
- Independent review SHA-256: `f3111a925f74f8b4b59b6a935d7e5f51e8f3a0280471cb276b4202d9403a95f4`.
- Runtime image digest: `sha256:c900631c51e601e91c6300e6d9fb8740375cd9ec28581c2f360068bafcea4f5f`.
- Offline MiniLM revision: `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- Controller-stop receipt SHA-256: `9fa4ffe5db7ed09bc97dd261eafcc2e3d81c0b77e12c827dac1a65055f6732b8`.

The registered task roots, raw corpora, private questions and references,
candidate copies, model weights, native jobs and trajectories remain ignored.
Only reviewed aggregate reports are published. Git ignore rules control
tracking; physical offline agent/verifier separation provides the execution
boundary under the declared trusted host controller.
