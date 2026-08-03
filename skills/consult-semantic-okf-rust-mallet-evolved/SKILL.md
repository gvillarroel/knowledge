---
name: consult-semantic-okf-rust-mallet-evolved
description: Consult an immutable reference-dictionary RustMallet Semantic OKF snapshot through compact multi-focus retrieval and reference-ID evidence. Use for multi-paper synthesis, probabilistic-topic discovery, and evidence JSON whose identities must remain byte-exact. This standalone skill is read-only and never builds, repairs, refreshes, or modifies knowledge.
---

# Consult Semantic OKF RustMallet Evolved

Retrieve compact claim references, read only selected evidence, and return the
snapshot-owned IDs without copying long identity fields through model text.

## Standalone read-only boundary

- Use only this skill and the supplied external bundle.
- Never write a cache, query, draft, answer, lock, or derived file inside the bundle.
- Treat retrieval scores as discovery signals, never as factual support.
- Stop on any snapshot validation, dictionary, digest, locator, or path error.
- Never reconstruct or copy `source_id`, paths, locators, or hashes manually.

## Exact answer protocol

When the request requires evidence JSON, follow only this bounded protocol:

1. Do not inspect or list the bundle, read helper source or reference documents,
   run deep validation, install packages, open concept pages, or invoke the legacy
   query helper. The compact helper validates the published snapshot on every call.
2. Run one compact `search` with the complete question. Do not select a mode.
   The helper always uses BM25 and deterministically adds operational expansions
   for mechanisms named by the question: seed/spreading signals for diffusion,
   resource/reliability for paths, prizes/cost for connected subgraphs,
   decomposition/reflection for adaptive traversal, and filtering/integration
   controls for external-versus-parametric knowledge. Optional focus queries are
   only for a named question dimension not covered by those expansions.
3. Use the helper's `recommended` array unchanged. It assigns one source per
   operational mechanism when possible, then adds a two-source breadth buffer
   for incomplete relevance judgments and related evidence. The recommendation
   therefore contains the required count plus at most two independent papers.
   Do not substitute alternatives or run a second search when `recommended`
   covers every named part.
4. Run one `show` call containing every recommended ID. Do not search again
   after `show`.
5. Draft outside the bundle with exactly `question_id`, `summary`, and `claims`.
   Each claim contains exactly `statement` and `reference_ids`. Ground every claim
   in shown text, use every selected reference, and introduce no unshown fact.
6. Run `finalize` once with the task's minimum source count and without
   `--output`. Its stdout is one canonical JSON line whose evidence rows contain
   exactly `reference_id`. Use that exact line as the terminal response: do not
   expand IDs, open a file, pretty-print, retype, normalize, or reconstruct any
   character. The task verifier resolves the IDs from the mounted snapshot before
   applying the legacy exact-evidence checks. If finalization rejects the draft,
   correct only the draft; do not resume discovery.

Use the installed skill path and keep temporary files outside the snapshot:

```bash
SKILL_DIR="$HOME/.agents/skills/consult-semantic-okf-rust-mallet-evolved"
python -B "$SKILL_DIR/scripts/reference_consult.py" search BUNDLE \
  --query "FULL QUESTION" --minimum-sources 5
python -B "$SKILL_DIR/scripts/reference_consult.py" show BUNDLE \
  --reference-id ref-0123456789abcdef01234567 \
  --reference-id ref-89abcdef0123456789abcdef
python -B "$SKILL_DIR/scripts/reference_consult.py" finalize BUNDLE \
  /tmp/reference-draft.json --minimum-sources 5
```

The search output contains compact IDs and interpretations, not long identity
fields. `show` returns authoritative text. `finalize` validates every ID against
the current `classical/references.json`, enforces independent-source breadth and
first-use order, and emits only those IDs. The verifier, not the model, resolves
the seven exact evidence fields from the same dictionary.

## Other consultation

Use the same compact `search` and `show` commands for ordinary read-only discovery.
Use `scripts/query_semantic_okf_rust_mallet.py` only when the user explicitly asks
for index diagnostics, topic activations, associations, or an integrity audit.
Deep validation is restricted to an explicitly requested integrity audit.

## Completion gate

Before returning evidence JSON, confirm that:

- no more than two compact searches and one show call were used;
- selected interpretations directly cover every named question part;
- the recommended minimum-through-minimum-plus-two independent papers are present;
- every claim is supported by shown authoritative text;
- `finalize` succeeded against the current dictionary; and
- the one-line finalized stdout is the unchanged terminal response.
