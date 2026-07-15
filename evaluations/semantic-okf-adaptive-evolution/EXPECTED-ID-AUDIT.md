# Frozen Expected-ID Audit

## Conclusion

The expected claim IDs are semantically sensible and structurally valid. The audit found **zero
mismatches** across 44 atomic answer claims, 13 important negatives, 42 unique authoritative claim
records, and the 40 question/config combinations in four Skill Arena configurations.

The frozen benchmark was not edited. This review distinguishes three concepts that should not be
collapsed into one score:

1. **Semantic correctness** asks whether the answer is true and appropriately qualified.
2. **Exact atomic ID coverage** asks whether every selected canonical claim record was carried into
   the response. It is intentionally stricter and may under-credit a correct answer that cites a
   different valid record.
3. **Important-negative ID coverage** asks whether at least one declared evidence anchor for each
   negative is present. It does not by itself prove that the response stated the required exclusion or
   contrast; the blinded semantic review checks that separately.

## What was checked

For every expected claim ID, the audit independently reproduced or verified:

- the reviewed JSONL claim record and its exact line, character offsets, and hash;
- the versioned paper identity and claim source identity;
- every declared `PDF-page-N` locator, page-text offsets, and page-text hash;
- the adaptive answer binding, authoritative interpretation hash, source path, concept path, paper
  identity, locator tokens, and integer citation pages;
- the existence of the concept mirror and its authoritative interpretation;
- complete use of the selected evidence by atomic answers or important negatives; and
- parity between the frozen ground truth and the `allowed`, `requiredPapers`, atomic `expectedSets`,
  and negative `expectedSets` embedded in all four Skill Arena configs.

The independent hard-ground-truth validator also confirmed the exact 30+10 benchmark composition and
question/answer isolation.

## Per-question result

| Question | Atomic claims | Important negatives | Unique claim anchors | Verdict |
| --- | ---: | ---: | ---: | --- |
| `q031-graph-routing-boundary` | 4 | 1 | 4 | Pass |
| `q032-incremental-update-maturity` | 5 | 1 | 5 | Pass |
| `q033-corruption-specific-defenses` | 4 | 1 | 4 | Pass |
| `q034-nonmonotonic-context-budget` | 4 | 1 | 4 | Pass |
| `q035-lossless-enough-evidence-organization` | 4 | 1 | 4 | Pass |
| `q036-evaluation-leakage-and-stage-separation` | 5 | 2 | 5 | Pass |
| `q037-domain-construction-under-constraints` | 5 | 2 | 5 | Pass |
| `q038-failure-aware-query-router` | 4 | 1 | 4 | Pass |
| `q039-baseline-bound-efficiency-claims` | 5 | 1 | 5 | Pass |
| `q040-answer-source-control` | 4 | 2 | 4 | Pass |
| **Total** | **44** | **13** | **42 across the benchmark** | **Pass** |

Forty atomic statements are direct faithful paraphrases of their reviewed claim interpretations.
Four deserve an explicit interpretation note; none requires changing the expected ID:

| Atomic claim | Relationship | Review conclusion |
| --- | --- | --- |
| `q031-a4` | Bounded derivation | The record reports corrections in both directions; “neither route is universally dominant” is the valid contrast drawn from those two reported categories. |
| `q035-a4` | Bounded derivation | The reviewed evaluator analysis identifies examples, quotations, and citations as details graph extraction should retain better; possible loss from a high-level community summary is a cautious synthesis. |
| `q036-a4` | Bounded derivation | The record directly establishes a contamination/reference-quality concern; independently verifying the reference answer is the defensible benchmark-design consequence. |
| `q038-a4` | Page-supported detail | The claim interpretation names DFS traversal, and its cited paper page defines maximum depth five; “bounded path” is therefore supported by the exact locator. |

Important negatives are intentionally derivational. For example, `q039-n1` is not a sentence copied
from one paper: it is the cross-paper conclusion that ratios tied to different baselines, tasks,
models, and cost definitions must not be ranked as if they were comparable. Its three IDs make sense
as evidence anchors, but the ID-only assertion accepts any one of them. Therefore the ID assertion is
an anchor-presence diagnostic, while the separate blinded review remains the authority for whether
the answer actually states the comparison boundary.

## Reproduction

Run the audit from the repository root:

```powershell
python evaluations/semantic-okf-adaptive-evolution/scripts/audit_expected_ids.py `
  --output evaluations/semantic-okf-adaptive-evolution/expected-id-audit.json
```

The checked-in [machine-readable audit](expected-id-audit.json) binds the frozen ground truth, adaptive
index, answer-binding artifact, all four Skill Arena configs, every reviewed interpretation, and the
manual relationship classification above.
