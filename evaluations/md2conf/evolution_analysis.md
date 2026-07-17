# md2conf Skill Evolution Analysis

## Outcome

The evolved skill materially improved offline md2conf planning, diagnosis, recovery, and safety guidance. In the final frozen qualification, the skill-enabled profile passed 44 of 51 samples (86.3%) while the isolated no-skill control passed 12 of 51 (23.5%), an absolute lift of 62.8 percentage points. Skill Arena completed all 102 evaluations with zero runtime errors.

This result qualifies the skill as a stronger planning and review workflow. It does not prove live Confluence publication correctness.

## Qualification design

- Benchmark: `md2conf-varied-evolution-compare`
- Evaluation ID: `eval-F2G-2026-07-13T22:00:40`
- Result directory: `results/md2conf-varied-evolution-compare/2026-07-13T22-00-37-378Z-compare`
- Prompts: 17 across 13 genuine task families
- Profiles: isolated no-skill control and isolated md2conf-only treatment
- Samples: 3 per prompt/profile cell, 102 total
- Runtime: Codex GPT-5.6 Sol, read-only sandbox, approvals disabled, web and network disabled
- Assertions: one semantic rubric per prompt plus a shared non-empty response check
- Completed: 102; runtime errors: 0; duration: 2,344,669 ms

The corpus covers local preview, directory hierarchy, mapped updates, scoped Cloud authentication, storage XML and diagrams, package drift, Markdown contract defects, attachment integrity, partial-run recovery, mentions, metadata reconciliation, explicit mapping boundaries, and native Confluence authority.

## Evolution evidence

| Round | Treatment | Control | Interpretation |
| --- | ---: | ---: | --- |
| Initial semantic baseline | 8/13 | 3/13 | The generated responses and semantic grades were valid, but the aggregate report was invalidated by a malformed shared JavaScript assertion. |
| First clean candidate | 11/13 | 3/13 | Added end-to-end response closure for previews, rich content, trees, mentions, and native authority conflicts. |
| Second clean candidate | 12/13 | 2/13 | Added consistent explicit-mapping and metadata decision guidance. |
| Frozen qualification | 44/51 (86.3%) | 12/51 (23.5%) | Three fresh samples per cell over the expanded 17-prompt corpus. |

The initial malformed assertion used a statement-form `return` where Promptfoo expected an expression. The final config uses a valid expression. The baseline aggregate `evolution_baseline_report.md` is retained only as raw provenance; its displayed zero rate must not be used as performance evidence.

## Skill changes driven by observed gaps

- Require a complete proposed workflow even when the executable or sandbox prevents execution.
- Close local-preview plans with distribution/version/help preflight, disposable staging, an exact local command shape, generated-storage review, and later browser verification.
- Require one well-formed tenant-compatible `csf` node and explicit diagram prerequisites.
- Explain the full live mention chain from `mailto:` lookup to `ri:user` and possible notification.
- Make complete-body regeneration and the native-page/separate-Markdown-page alternatives explicit.
- Apply explicit page mappings against the requested space and root without guessing IDs or creating duplicates automatically.
- Distinguish absent, empty, and populated metadata fields; explain label deletion against the full returned set, property reconciliation, and md2conf's own synchronization property.

## Residual qualification misses

Seven treatment samples failed their all-or-nothing semantic rubrics:

- one scoped-auth sample did not read the non-secret fixture and therefore did not select its concrete cloud ID and space;
- one mention sample omitted the version-specific absence of a user-mention disabling flag;
- one absent-metadata sample omitted the complete-body regeneration warning;
- three tags-only samples made the correct preservation decision but omitted either removal-by-name wording or the synchronization-property nuance;
- one properties-only sample made the correct decision but did not enumerate both global and team label namespaces.

Six of the seven misses reached the correct safe decision and proposed no unsafe live mutation. They are retained as qualification evidence rather than used for another tuning round.

## Limits and next independent gates

- The original 13 prompts became a development regression set because their failures directly informed the skill. The four metadata-matrix prompts expand generalization coverage, but future promotion should use a separately frozen unseen corpus.
- Actor and judge both use the Codex route. A second model or independent judge would test portability.
- The evaluation is deliberately offline and primarily tests plans and diagnostics. It does not execute a pinned `md2conf --local` conversion or a mock-backed publisher.
- A future boundary case should cover same-name labels across global, team, and personal prefixes.
- Promptfoo's rendered overall status labels semantic failures as errors; the authoritative `summary.json` records `errors: 0`.

## Artifact hashes

- `skills/md2conf/SKILL.md`: `04E83FFAF1AA00C6B79CC69B35312A68FED8307A26BFD2A9523452BA47CCC8C7`
- `evaluations/md2conf/evolution.yaml`: `D03F7068DBE843B8B8CF366333760374A176A658A6DEA7EDBEE17FF99C0D2EE5`
- `evaluations/md2conf/evolution-coverage.json`: `E07DA6F0F9D4751325B60D7181477F20FE4EE3CB4D34EAF9E0ACBB388FCAC54D`
