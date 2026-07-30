---
type: Agent Skill
title: Review Knowledge Methodology
description: Review and challenge this repository's knowledge acquisition, representation,
  retrieval, evaluation, evolution, and publication methodology using the embedded
  version-pinned research-paper corpus. Use for paper-grounded architecture reviews,
  experiment design critiques, dataset governance audits, and prioritized knowledge-method
  improvements.
tags:
- codex
- skill
skill_name: review-knowledge-methodology
source_path: skills/review-knowledge-methodology/SKILL.md
---

# Review Knowledge Methodology

Apply the bundled knowledge using its reviewed domain guidance and exact local
evidence. This skill is a self-contained read-only expert artifact.

## Standalone boundary

- Use only this skill's files and the user's query.
- Treat `references/knowledge/` as immutable and authoritative.
- Do not use the web or unstated prior knowledge when the snapshot is the
  requested authority.
- Do not rebuild, repair, refresh, or modify the embedded knowledge.

## Workflow

1. Read [guidance.md](../../skills/review-knowledge-methodology/references/guidance.md) and translate the request into its
   domain-specific decision and evidence checklist.
2. Verify the artifact binding and discover candidate records:

   ```bash
   python scripts/query_expert_knowledge.py verify
   python scripts/query_expert_knowledge.py search --contains "QUERY TERMS"
   ```

3. Use exact `source_id`, `record_id`, and `concept_path` values from the results.
4. Open only the selected files below `references/knowledge/` and apply the
   guidance's decision rules.
5. Return the requested answer with exact bundled evidence paths. Label any
   inference and stop when the knowledge does not support a conclusion.

## Exact lookup

```bash
python scripts/query_expert_knowledge.py get   --source-id SOURCE_ID --record-id RECORD_ID --show-content
```

The helper verifies [expert-manifest.json](expert-manifest.json) before every
operation. It is local and read-only.


## Completion gate

- The manifest and complete embedded knowledge tree passed verification.
- Every material claim is supported by an exact bundled concept path.
- The guidance's scope, decision rules, important negatives, and limits were
  applied.
- No file in this skill was changed.
