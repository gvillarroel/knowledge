---
name: consult-semantic-okf-rust-mallet-evolved
description: Consult an immutable reference-dictionary RustMallet Semantic OKF snapshot through one bounded preparation and reference-ID evidence. Use for multi-paper synthesis, probabilistic-topic discovery, and evidence JSON whose identities must remain byte-exact. This standalone skill is read-only and never builds, repairs, refreshes, or modifies knowledge.
---

# Consult Semantic OKF RustMallet Evolved

Prepare one bounded evidence set, synthesize only from its retrieval
interpretations and authoritative text, and return snapshot-owned IDs without
copying long identity fields through model text.

## Read-only contract

- Use only this skill and the supplied external bundle.
- Never write a cache, query, draft, answer, lock, or derived file inside the bundle.
- Treat retrieval scores and interpretations as discovery signals, never as factual support.
- Stop on any snapshot validation, dictionary, digest, locator, or path error.
- Never reconstruct or copy `source_id`, paths, locators, or hashes manually.

## Exact answer protocol

When the request requires evidence JSON, follow only this bounded protocol:

1. Copy `MINIMUM` exactly from the request's required independent-paper count.
2. Do not list the skill or bundle, invoke help, read helper source or reference
   documents, run deep validation, install packages, open concept pages, or
   invoke the legacy query helper. The command below is complete.
3. Run exactly one preparation call with the complete question and `MINIMUM`.
   It preserves the compact search's `recommended` rows and interpretations,
   then adds the authoritative full text for those same IDs under `selected`.
4. Use the recommended set unchanged. It contains `MINIMUM` through
   `MINIMUM + 2` independent papers so incomplete relevance judgments retain a
   bounded breadth buffer. Use interpretations to plan coverage and selected
   text to support claims. Do not search again.
5. Draft outside the bundle with exactly `question_id`, `summary`, and `claims`.
   Each claim contains exactly `statement` and `reference_ids`. Ground every
   claim in selected text, use every selected reference, and introduce no
   unshown fact.
6. Run `finalize` once with the same `MINIMUM` and without `--output`. Its stdout
   is one canonical JSON line whose evidence rows contain exactly
   `reference_id`. Use that exact line as the terminal response. If finalization
   rejects the draft, correct only the draft; do not resume discovery.

Use the installed skill path and keep temporary files outside the snapshot:

```bash
SKILL_DIR="$HOME/.agents/skills/consult-semantic-okf-rust-mallet-evolved"
MINIMUM="<integer copied from the request>"
python -B "$SKILL_DIR/scripts/prepare_reference_consult.py" BUNDLE \
  --query "FULL QUESTION" --minimum-sources "$MINIMUM"
python -B "$SKILL_DIR/scripts/reference_consult.py" finalize BUNDLE \
  /tmp/reference-draft.json --minimum-sources "$MINIMUM"
```

The preparation output retains compact IDs, source identities, matched query
focuses, and interpretations alongside selected authoritative text.
`finalize` validates every ID against the current
`classical/references.json`, enforces independent-source breadth and first-use
order, and emits only those IDs. The verifier, not the model, resolves the seven
exact evidence fields from the same dictionary.

## Other consultation

Use the existing `reference_consult.py search` and `show` commands for ordinary
read-only discovery. Use `query_semantic_okf_rust_mallet.py` only when the user
explicitly asks for index diagnostics, topic activations, associations, or an
integrity audit. Deep validation is restricted to an explicitly requested
integrity audit.

## Completion gate

Before returning evidence JSON, confirm that:

- exactly one preparation call was used and no inspection or help call was used;
- the minimum count passed to both commands exactly matches the request;
- the selected IDs exactly match the recommended IDs and preserve their order;
- every selected reference appears in at least one claim grounded in selected text;
- `finalize` succeeded against the current dictionary; and
- the one-line finalized stdout is the unchanged terminal response.
