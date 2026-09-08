# Skill evolution readiness inventory

Date: 2026-09-06. Research complete; evolution execution has not started.

Read the [evolution roadmap](../../../docs/knowledge-skill-evolution-roadmap.md) for
the proposed priorities, dataset eligibility review, evidence requirements,
and one-way acceptance process. The [JSON inventory](20260906-readiness.json)
contains complete target fingerprints and supporting source commitments.

## Readiness outcome

- The existing direct retrieval ranking executes runtime functions; changing
  `SKILL.md` alone does not change those results.
- The embedding family already supports a pinned learned model; comparing
  it with hashing is the proposed first builder treatment.
- Candidate execution must first attest the actual staged runtime and
  reproduce the canonical baseline.
- An eligible native development failure pack and independently sealed
  validation were not established by this audit. The current aggregate
  report hub is not a substitute for either.
- No candidate, formal planner campaign, evolution job, new score, or
  promotion was created by this research.

## Inspected target versions

The inventory covers 16 canonical build/consult packages and four expert
or integrated generators. It does not claim to inventory every experimental
or historical skill in the repository. Fingerprints use the expertise
planner's canonical `digest_command`, including all current files and
directories. Cache files, where present, are counted without filtering.
A formal study must materialize clean packages and create new candidate
seals. These local-tree fingerprints are audit identities only.

| Skill | Role | Files | Cache files included | Tree SHA-256 prefix |
| --- | --- | ---: | ---: | --- |
| [build-semantic-okf](../../../skills/build-semantic-okf/SKILL.md) | build | 21 | 6 | `f41907dc49567250` |
| [consult-semantic-okf](../../../skills/consult-semantic-okf/SKILL.md) | consult | 17 | 4 | `67490d5b4fe4341f` |
| [build-semantic-okf-embeddings](../../../skills/build-semantic-okf-embeddings/SKILL.md) | build | 27 | 7 | `2496ddab5239759c` |
| [consult-semantic-okf-embeddings](../../../skills/consult-semantic-okf-embeddings/SKILL.md) | consult | 14 | 3 | `7c8322466161c476` |
| [build-semantic-okf-classical](../../../skills/build-semantic-okf-classical/SKILL.md) | build | 22 | 7 | `d427e1629308332e` |
| [consult-semantic-okf-classical](../../../skills/consult-semantic-okf-classical/SKILL.md) | consult | 10 | 2 | `9d44a4d8932007eb` |
| [build-semantic-okf-adaptive](../../../skills/build-semantic-okf-adaptive/SKILL.md) | build | 24 | 7 | `81035d881331850d` |
| [consult-semantic-okf-adaptive](../../../skills/consult-semantic-okf-adaptive/SKILL.md) | consult | 12 | 3 | `06e0d43fa94c21ce` |
| [build-semantic-okf-entity-graph](../../../skills/build-semantic-okf-entity-graph/SKILL.md) | build | 27 | 9 | `30121a0905cf781b` |
| [consult-semantic-okf-entity-graph](../../../skills/consult-semantic-okf-entity-graph/SKILL.md) | consult | 16 | 6 | `1aad8a6046140742` |
| [build-semantic-okf-ensemble](../../../skills/build-semantic-okf-ensemble/SKILL.md) | build | 45 | 15 | `bf8f9cd213b4c706` |
| [consult-semantic-okf-ensemble](../../../skills/consult-semantic-okf-ensemble/SKILL.md) | consult | 33 | 15 | `cc570dabbbc0028b` |
| [build-semantic-okf-graphify](../../../skills/build-semantic-okf-graphify/SKILL.md) | build | 24 | 11 | `d6a832b87e54c526` |
| [consult-semantic-okf-graphify](../../../skills/consult-semantic-okf-graphify/SKILL.md) | consult | 12 | 3 | `ca5b55de2d4d43a0` |
| [build-semantic-okf-turso](../../../skills/build-semantic-okf-turso/SKILL.md) | build | 25 | 6 | `7b9b97d0bebe53c6` |
| [consult-semantic-okf-turso](../../../skills/consult-semantic-okf-turso/SKILL.md) | consult | 12 | 2 | `2ae2576ee664395f` |
| [build-specialized-skill](../../../skills/build-specialized-skill/SKILL.md) | generator | 20 | 9 | `34ff67473f0a53db` |
| [build-semantic-okf-knowledge-skill](../../../skills/build-semantic-okf-knowledge-skill/SKILL.md) | generator | 248 | 0 | `1621f4155b244e08` |
| [build-classical-knowledge-skill](../../../skills/build-classical-knowledge-skill/SKILL.md) | generator | 25 | 5 | `106c59625fa5ed20` |
| [build-classical-chunked-knowledge-skill](../../../skills/build-classical-chunked-knowledge-skill/SKILL.md) | generator | 34 | 11 | `b788ae0039a1c009` |

Full digests and 17 source-artifact SHA-256 commitments are retained in the
JSON. Source commitments cover evaluator code, public aggregate metadata,
policy documents, and ADRs. No questions, answers, qrels, private case
identifiers, or dataset payloads are reproduced here.

## Executed repository checks

| Check | Observed result |
| --- | --- |
| Application test suite under the coverage gate | 1185 passed in 137.90 seconds |
| Total application coverage | 90.7%; minimum 80%; passed |
| Canonical dataset registry | Three descriptors, all eight registered strategy pairs; passed |
| Aggregate report regeneration | Nine datasets and 37 files; unchanged and valid |
| EnterpriseRAG published comparison | All 18 alternatives; unchanged and valid |
| Git evaluation data boundary | Zero tracked files matching evaluation ignore rules |
| Project OKF bundle | Current projection and validation passed |
| Version bindings | All 20 target trees and 17 source artifacts recomputed and matched |
| Markdown navigation | 138 local links across six documents; no broken links |
| Diff whitespace | Working-tree and staged checks passed |

These checks verify repository integrity. They do not evaluate any proposed
candidate or establish new quality, cost, or latency gains.

The coverage command was:

```powershell
python scripts/check_coverage.py --threshold 80 --tests-args --basetemp=tmp/evolution-roadmap-pytest-20260906
```

Target identities can be recomputed with the installed expertise planner's
`digest` command for each `targets[].path`. Its exact implementation hash
is recorded in the JSON; it computes a full local tree, not only tracked
files. Recompute identities after tests or packaging that change caches.

[Roadmap](../../../docs/knowledge-skill-evolution-roadmap.md) ·
[Report catalog](../../COMPARISON-REPORTS.md) · [Report hub](../README.md)
