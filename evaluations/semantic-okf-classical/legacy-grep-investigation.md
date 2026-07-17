# Legacy `grep` / `rg` Investigation

## Finding

The legacy consultation skill is not implemented as a single `grep` retrieval engine. It contains one optional `rg` (ripgrep) recipe for exact fixed-string discovery in concept Markdown. The retrieval benchmark's route named `legacy_lexical` does not invoke `rg`, POSIX `grep`, or any subprocess at all; it is an in-process deterministic TF-IDF-like ranker over the authoritative ledger.

These are separate layers:

1. **Skill guidance.** `skills/consult-semantic-okf/references/querying.md` recommends `rg -i -n --glob '*.md' --fixed-strings` when a user already has an exact phrase. The same reader workflow prioritizes the ledger for discovery, concept Markdown for context, and RDF only for joins or aggregation. `rg` is therefore one optional exact-phrase tool, not the skill's complete retrieval definition.
2. **Legacy benchmark algorithm.** `LegacyLexicalIndex.from_ledger` in `evaluations/semantic-okf-embeddings/scripts/compare_retrieval.py` tokenizes every authoritative ledger record, computes document-frequency IDF values, and retains term-frequency counters. `LegacyLexicalIndex.search` scores query-token overlap as `(1 + log(tf)) * idf`, sorts deterministically by score and concept path, and returns the requested candidates. There is no `grep`, `rg`, shell, or subprocess call in that route.
3. **Agent behavior in answer runs.** A knowledge-only Skill Arena control may choose `rg` while navigating files because the general Codex environment prefers it for text search. Such a command is an agent navigation choice. It must not be conflated with the frozen `legacy_lexical` evaluator algorithm or used to relabel its metrics.

## Verification performed

- A repository search found the active legacy reader's only `rg` example in `skills/consult-semantic-okf/references/querying.md`.
- The frozen comparator's tokenizer, index construction, and scoring implementation were read directly.
- Searches of the comparator found no `grep` or `rg` execution in `LegacyLexicalIndex`.
- The current classical comparison continues to import and execute that frozen route without modifying it.

## Decision

The legacy baseline remains unchanged. Reports describe it as **in-memory TF-IDF-like ledger ranking**. Documentation may separately say that the reader instructions permit ripgrep for exact phrase discovery. This distinction preserves the user's observation without attributing an interactive navigation recommendation to the benchmark algorithm.
