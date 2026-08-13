---
name: visualize-semantic-okf-classical
description: Generate and validate a standalone, read-only interactive atlas from a Classical Semantic OKF knowledge bundle. Use when Codex needs to visualize or inspect classical knowledge metadata, including authoritative records, source provenance, ontology and validation summaries, exact passages, BM25 corpus statistics, topic communities, PPMI term associations, precision-filtered contradiction review, retrieval parameters, artifact hashes, and build integrity without modifying the knowledge package.
---

# Visualize Classical Semantic OKF

Generate one deterministic external atlas that explains both the authoritative
knowledge and its non-authoritative classical discovery projection.

## Authority boundary

- Treat the supplied knowledge directory as immutable input.
- Write only to a separate absent output directory.
- Never copy generated visualization files into the knowledge bundle.
- Present topics, BM25 values, and PPMI associations as discovery metadata,
  never as ontology facts or evidence.
- Preserve exact concept paths, source identities, record identities, and
  passage locators so users can return to authoritative evidence.

## Workflow

1. Confirm the input contains `index.md`, `concepts/`, `semantic/`, and the six
   closed `classical/` artifacts.
2. Run the package-local runtime smoke check.
3. Generate the atlas into a separate absent directory.
4. Run the independent atlas validator.
5. Repeat generation with `--check`; require byte-identical output and an
   unchanged source-tree receipt.
6. Open `index.html` through a local HTTP server and inspect Atlas, Sources,
   Contradictions, and Integrity views in a real browser.
7. Verify topic selection, term selection, contradiction search and filters,
   source navigation, responsive layout, and a clean browser console before
   delivery.

## Generate

Run from this skill directory, or prefix scripts with the copied skill root:

```bash
python -B scripts/runtime_smoke.py
python -B scripts/build_classical_atlas.py KNOWLEDGE OUTPUT --output-format json
python -B scripts/validate_classical_atlas.py KNOWLEDGE OUTPUT --output-format json
python -B scripts/build_classical_atlas.py KNOWLEDGE OUTPUT --check --output-format json
```

The output is self-contained and offline:

```text
OUTPUT/
  index.html
  projection.json
  receipt.json
```

`index.html` embeds the exact `projection.json` payload and requires no CDN,
database, server application, model, or network request. `receipt.json` binds
the source tree and generated artifacts by SHA-256.

## Presentation contract

- Lead with bundle identity, validation state, and counts for records,
  passages, vocabulary, topics, and association terms.
- Make topic communities the primary navigation because they are the classical
  strategy's corpus-level organizing signal.
- Draw only persisted PPMI relationships in the association map; do not infer
  topic-to-topic edges.
- Show representative exact passages ranked by persisted topic weight and link
  them to concept and locator metadata.
- Expose sources, concept types, publication years, ontology declarations,
  SHACL status, algorithms, parameters, artifact sizes, and hashes in dedicated
  views.
- Label explicit source-metadata contradiction relations as source-declared,
  not independently confirmed.
- Fail closed on heuristic contradiction detection. Require proposition
  alignment under the precision contract in
  [metadata-contract.md](references/metadata-contract.md); keep broad lexical
  tensions only as aggregate rejected-signal counts.
- Keep every strict candidate review-required, preserve both evidence
  locators, and state that omitted scope or conditions may still reconcile it.
- Provide local filters for row text, declaration status, evidence scope, and
  strict conflict type. Filters must not change or write source knowledge.
- Label every statistical layer as derived and keep authoritative evidence
  visually distinct.

Read [metadata-contract.md](references/metadata-contract.md) only when adapting
the renderer to a new Classical schema version or diagnosing a missing field.

## Completion gate

Before delivery, require:

- source and output paths are disjoint;
- source build reports pass and artifact hashes match;
- every classical metadata layer contributes to the projection;
- every contradiction row preserves two record identities, concept paths, and
  evidence locators, while strict heuristic rows remain labeled
  `strict-review-required`;
- every lexical candidate shares a structured subject and analysis dimension,
  passes the declared proposition-similarity floor, and contains an approved
  unambiguous conflict signal;
- the embedded browser payload equals `projection.json`;
- the output contains exactly three regular files and no symlinks;
- `--check` passes without writing;
- the source-tree digest remains unchanged after generation; and
- browser interaction and console checks pass.
