# md2conf Skill Evolution v2 Analysis

## Outcome

The second evolution pass is accepted as a development improvement and a held-out non-regression, with explicit limits.

The candidate adds exact stable-0.6.1 guidance for recursive global-property merging, the recorded-version condition behind `--no-overwrite`, document-level space routing, comment/frontmatter mapping precedence, same-name label collisions across prefixes, attachment reconciliation when a body is current, and same-directory `.mdignore` behavior.

The evidence does not establish a held-out lift over the frozen previous skill or cross-adapter portability. The valid held-out Codex route reached parity with the frozen skill, and the Antigravity route was invalidated by timeouts and quota exhaustion.

## Evaluation design

The pass keeps three evidence sets separate:

1. a seven-prompt development corpus across seven distinct task families;
2. a four-prompt held-out qualification corpus across four different task families;
3. a one-prompt targeted regression gate for the last pre-qualification property-safety close.

Every compare profile used `inheritSystem: false`. The frozen previous skill is a byte-identical snapshot at `evaluations/md2conf/fixtures/skills/md2conf-v1`. The candidate profile installs only `skills/md2conf`. Prompts, fixtures, assertions, offline policy, and request counts are identical within each comparison.

The first attempted development run used the Copilot CLI judge and is excluded. Its multiline prompt quoting failed and its temporary configuration directory caused cleanup errors. All accepted semantic evidence uses `skill-arena:judge:codex`; raw Promptfoo statistics, rather than the normalized report's display label, determine whether runtime errors occurred.

## Development evidence

The valid frozen baseline was evaluation `eval-9DI-2026-07-13T23:16:28`.

| Profile | Overall | Core safety | Mechanics | Raw runtime errors |
| --- | ---: | ---: | ---: | ---: |
| No skill | 1/7 | 3/7 | 3/7 | 0 |
| Frozen v1 | 5/7 | 7/7 | 5/7 | 0 |

The frozen skill's two exact misses were:

- it incorrectly described document/global properties as a shallow key-level override instead of a recursive nullish merge;
- it omitted the recorded-page-version comparison required for `--no-overwrite` to detect a conflict.

The first candidate sample closed those two cases but omitted complete response closure on source-space and current-body attachment cases, scoring 5/7. After general attachment and mapping closure was added, the next full sample, evaluation `eval-IAW-2026-07-13T23:47:58`, scored 6/7 with zero raw runtime errors. Its only miss derived the property merge and deletion correctly but did not explicitly require either leaving properties unmanaged or reviewing a complete desired set.

That close was added before qualification and was not changed afterward. The targeted post-development regression, evaluation `eval-3dP-2026-07-14T00:41:25`, produced:

| Profile | Recursive-property regression |
| --- | ---: |
| No skill | 0/1 |
| Frozen v1 | 0/1 |
| Candidate | 1/1 |

The regression run had zero raw runtime errors. The candidate derived the complete merged object, identified deletion of the extension-owned property, and closed with both safe alternatives.

## Held-out qualification

Qualification evaluation `eval-Eze-2026-07-14T00:04:17` requested 24 cells: four unseen prompts, three profiles, and two variants.

### Infrastructure validity

| Variant | Profile | Requested | Evaluable artifacts | Infrastructure errors |
| --- | --- | ---: | ---: | ---: |
| Codex | No skill | 4 | 4 | 0 |
| Codex | Frozen v1 | 4 | 4 | 0 |
| Codex | Candidate | 4 | 4 | 0 |
| Antigravity | No skill | 4 | 0 | 4 |
| Antigravity | Frozen v1 | 4 | 1 | 3 |
| Antigravity | Candidate | 4 | 1 | 3 |

Antigravity produced nine timeouts and one quota-exhaustion error. Its other two artifacts contained truncated progress text rather than final answers. The Antigravity route is therefore inconclusive and is excluded from semantic acceptance claims.

### Codex results

| Profile | Raw overall | Core safety | Mechanics |
| --- | ---: | ---: | ---: |
| No skill | 0/4 | 2/4 | 0/4 |
| Frozen v1 | 2/4 | 3/4 | 3/4 |
| Candidate | 2/4 | 3/4 | 3/4 |

The single-file-link mechanics rubric produced a false negative for both skill profiles. Both responses used a disposable directory copy and a mapped `synchronized: false` prerequisite. That is the documented stable workflow for retaining a Confluence-authored page in navigation and link resolution without synchronizing its body. The rubric instead allowed directory mode only when both documents were synchronized, contradicting both the skill contract and the task's instruction not to publish or change the prerequisite.

Manual adjudication gives both frozen and candidate profiles a mechanics pass for that case:

| Profile | Corrected overall | Corrected core safety | Corrected mechanics |
| --- | ---: | ---: | ---: |
| Frozen v1 | 3/4 | 3/4 | 4/4 |
| Candidate | 3/4 | 3/4 | 4/4 |

The remaining valid holdout miss is Data Center checklist completeness. Both skill profiles selected the correct API v1, domain, base path, space, page, root, Bearer PAT environment shape, local preview, and later browser verification. Neither explicitly required least-privilege account, space, page, and app permission checks; the candidate also did not label operational validity of fixture-derived target values as unverified. This is retained as qualification evidence and was not used for another tuning round.

## Deterministic tool evidence

The separate pinned local validation in `evolution-v2-local-validation.md` confirmed:

- local `--keep-hierarchy` created missing root and nested `index.md` files plus `.csf` files only in a disposable copy;
- the repository source remained byte-stable;
- a nested `.mdignore` rule failed with the expected unsupported-matching error;
- inline mapping comments overrode conflicting frontmatter values;
- recursive property coalescing produced the exact expected nested object.

This closes several limitations of the first evolution, which evaluated planning but did not execute pinned local conversion.

## Acceptance decision

Accept the candidate because:

- the development baseline identified two specific mechanics defects and the targeted regression shows the frozen candidate closes the remaining property case;
- the skill retains all core safety boundaries and adds source-verified, general rules rather than prompt-specific answers;
- deterministic stable-0.6.1 execution corroborates the highest-risk local behaviors;
- the valid held-out route shows no regression against frozen v1 after correcting a contradictory rubric.

Do not claim:

- a held-out improvement over frozen v1;
- successful cross-model qualification;
- live Confluence publication correctness;
- verified tenant permissions, Marketplace rendering, or remote label/attachment behavior.

## Artifact hashes

- `skills/md2conf/SKILL.md`: `B95F6E8AF33F4CE852DA7EC0700E9746F3583C447469AC12620F37EA0F867FB0`
- `skills/md2conf/references/markdown-contract.md`: `F9F2A03432251E7F6867ED5433E525CB3A7A8A1CDFA9F73B38F91EA969D72BD4`
- `skills/md2conf/references/publishing-safety.md`: `7971B5DB40315057121AC9E288F0128FFD36088DBB976C6CF61CFD09427F61B4`
- `evaluations/md2conf/evolution-v2-development.yaml`: `A654E284DF2DFDC8D67A3809CD84B27F05DD5CE95C8009CBC198EC9BB4C8A405`
- `evaluations/md2conf/evolution-v2-qualification.yaml`: `C694C53996F964F434B6ABA94DCE6A7E6DCB3CB65A2AB1146BE9C932B81D7A3C`
- `evaluations/md2conf/evolution-v2-property-regression.yaml`: `CBF84AC2C0FE6692A1D026ED95B2EE2015B3D8D56FE7C3A9FC82A4AF53692674`
