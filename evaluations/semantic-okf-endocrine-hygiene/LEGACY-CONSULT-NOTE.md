# Legacy Semantic OKF Consultation: `rg`, `grep`, and the Evaluator

## Verified conclusion

The legacy Semantic OKF evaluation does not use `grep` or `rg` as its retrieval
algorithm.

The legacy consultation guidance recommends one optional fixed-string `rg` command
for a person or agent doing lexical discovery in generated concept Markdown. The
actual legacy query program exposes only validated ledger filtering and local
read-only SPARQL. The `legacy_lexical` row in this evaluation is a separate,
explicitly labeled in-memory TF-IDF-like evaluator baseline. Neither its ranking code
nor the evaluator invocation executes `grep` or `rg`.

## What was inspected

The verification covered:

- `skills/consult-semantic-okf/SKILL.md`;
- `skills/consult-semantic-okf/references/querying.md`;
- `skills/consult-semantic-okf/scripts/query_semantic_okf.py`;
- `evaluations/semantic-okf-endocrine-hygiene/scripts/_retrieval_eval.py`; and
- `evaluations/semantic-okf-endocrine-hygiene/scripts/evaluate_retrieval.py`.

A repository search finds one operational recommendation in the legacy package:

```text
rg -i -n --glob '*.md' --fixed-strings -- 'retention policy' BUNDLE/concepts
```

It appears under “Search and read Markdown” in `references/querying.md`. The skill
also describes concept Markdown as a fixed-string lexical-discovery surface. This is
workflow guidance, not a packaged ranker. No `grep` command appears in the legacy
build or consultation package.

## What the legacy consult CLI actually implements

`query_semantic_okf.py` has two subcommands:

- `ledger` streams `semantic/records.jsonl` through exact identity, type, attribute,
  and fixed-substring filters; and
- `sparql` runs bounded, local, read-only `SELECT` or `ASK` queries over explicitly
  selected RDF graphs.

The CLI can validate the complete read surface before either operation. It does not
offer a ranked natural-language `search` subcommand. The endocrine-hygiene evaluator
therefore runs this command only as a real legacy read-surface validation:

```powershell
python skills/consult-semantic-okf/scripts/query_semantic_okf.py BUNDLE ledger --all --validate --format json
```

That command validates and reads the ledger. It does not produce the ranked
`legacy_lexical` benchmark results.

## What produces the `legacy_lexical` ranking

`LegacyLexicalIndex` in `_retrieval_eval.py` loads selected authoritative ledger
records in memory, tokenizes English text, computes document frequency, and scores
each record with this TF-IDF-like contribution for every distinct query token:

```text
(1 + log(term frequency)) * inverse document frequency
```

It then sorts deterministically, returns a raw pool of 100, maps lower-case source
IDs to real PMCIDs for evaluator-side paper scoring, deduplicates papers by first
occurrence, and validates every retained hit against the authoritative ledger.
There is no shell search process in this path.

`evaluate_retrieval.py` invokes a subprocess for the validated legacy ledger read.
The per-question ranking calls the in-process `LegacyLexicalIndex.search` method.
Static inspection of `_retrieval_eval.py` finds no `subprocess`, `Popen`,
`os.system`, `grep`, or `rg` invocation.

## Why the distinction matters

The accepted legacy metrics describe the evaluator-side baseline:

| Metric | Value |
| --- | ---: |
| Recall@10 overall | 98.9% |
| Recall@10 hard | 97.1% |
| MRR@10 | 0.967 |
| nDCG@10 | 0.947 |
| Evidence validity | 100.0% |
| Mean measured ranking time | 0.6 ms |
| p95 measured ranking time | 0.8 ms |

The 0.6 ms mean is the in-memory ranker's measured time after the ledger has been
loaded. It is not the latency of `rg`, `grep`, the legacy query CLI, full bundle
validation, file reading by an agent, or answer synthesis.

The row is retained because it supplies a deterministic lexical baseline over the
same authoritative records. It must be called an evaluator-side baseline, not a
legacy consult CLI search. Changing the frozen legacy skill merely to remove an
optional `rg` example would not change this evaluator and would invalidate the
purpose of comparing unchanged alternatives.

## Reproduce the implementation check

From the repository root:

```powershell
rg -n -i "\b(grep|rg)\b" skills/build-semantic-okf skills/consult-semantic-okf evaluations/semantic-okf-endocrine-hygiene/scripts
rg -n "add_parser|ledger|sparql" skills/consult-semantic-okf/scripts/query_semantic_okf.py
rg -n "class LegacyLexicalIndex|def search|subprocess|Popen|os\.system|grep|rg" evaluations/semantic-okf-endocrine-hygiene/scripts/_retrieval_eval.py
```

Expected interpretation:

- the legacy documentation contains the single fixed-string `rg` example;
- the evaluator documentation says the ranker invokes neither `grep` nor `rg`;
- the legacy CLI parser exposes `ledger` and `sparql`; and
- the in-memory ranker contains the scoring implementation and no shell-process
  invocation.

No MCP is required for any of these paths. The accepted direct ranker and CLI checks
are local and offline. The separate accepted remote Skill Arena run,
`eval-v8v-2026-07-15T23:49:40`, compares a knowledge-only control with the
**classical** consultation skill; it does not test the legacy ranker or legacy CLI.
All `10/10` cells completed with `0` runtime errors, but both profiles had 0/5 compound
passes and the classical treatment's mean score was `0.543` versus `0.657` for
control. With one request per cell, that result is descriptive and provides no
evidence of treatment improvement. See the
[compact accepted diagnostic](reports/skill-arena-hard5-diagnostic.md).
