# Legacy `grep` / `rg` Investigation

## Conclusion

The observation is partly correct at the instruction level, but it does not describe
the legacy row in the Astro direct-retrieval benchmark.

- The legacy consultation documentation recommends one optional `rg` fixed-string
  command for manually discovering words in generated concept Markdown.
- Neither the legacy builder nor its consultation CLI launches `grep`, `rg`, or any
  other external text-search process.
- The Astro evaluator's `legacy_tfidf` route builds and searches a deterministic
  in-memory TF-IDF index over the authoritative record ledger. Its reported retrieval
  metrics therefore measure that evaluator-side TF-IDF baseline, not the documented
  manual `rg` procedure.

This distinction matters: the direct retrieval table and an agent-level Skill Arena
treatment answer different questions. The direct table measures the explicitly coded
retrieval route. A treatment agent given the legacy skill could choose the documented
`rg` discovery command, so such a treatment must not be presented as if it measured
the evaluator's TF-IDF implementation.

This investigation is observational. It does not change either legacy package or
retrofit a different retrieval implementation into the frozen baseline.

## Evidence by layer

| Layer | Actual behavior | Code evidence |
|---|---|---|
| Legacy build skill | Reads declared local files through deterministic Python adapters, normalizes records, and atomically materializes a bundle. It does not perform question retrieval. Python `glob.glob` expands declared source paths; `glob` is file-pattern expansion, not `grep`. | `skills/build-semantic-okf/scripts/build_semantic_okf.py:180-196`, `:512-532`, `:560-618` |
| Legacy consultation instructions | Recommend fixed-string discovery over `concepts/**/*.md` with `rg`. This is procedural advice to an agent or human reader. | `skills/consult-semantic-okf/SKILL.md:48-57`; `skills/consult-semantic-okf/references/querying.md:49-57` |
| Legacy consultation executable | Exposes ledger filtering and local read-only SPARQL. `--contains` is implemented as a Python Unicode-case-folded substring test while streaming JSONL; it does not shell out. There is no ranked natural-language-search subcommand. | `skills/consult-semantic-okf/scripts/query_semantic_okf.py:87-115`, `:146-166`, `:353-400` |
| Astro legacy direct-retrieval route | Tokenizes title plus body, calculates smoothed inverse document frequency, applies sublinear term frequency, sums scores over unique query terms, and uses deterministic score/path ordering. | `evaluations/semantic-okf-astro/scripts/evaluate_retrieval.py:430-480` (`tokenize`, `LegacyIndex`) |
| Astro legacy validation/setup | Invokes the legacy CLI only to validate and read the complete authoritative ledger, then constructs `LegacyIndex` once and executes its in-process search for all 40 questions. | `evaluations/semantic-okf-astro/scripts/evaluate_retrieval.py:530-542`, `:1150-1188` |

For document (d) and unique query terms (q), the evaluator implements this
unnormalized TF-IDF score:

```text
score(d, q) = sum((1 + ln(tf(d, term))) * (1 + ln((N + 1) / (df(term) + 1))))
              for term in unique(q) present in d
```

It uses a fixed evaluator-owned regular expression to tokenize text, excludes
configured stop words, ignores nonpositive matches, and breaks equal scores by
authoritative concept path. No user-supplied regular expression, line-oriented shell
scan, or external search executable participates in that score.

## Reproduce the finding

Run these commands from the repository root in PowerShell.

Show every whole-word `grep` or `rg` mention in the two legacy packages:

```powershell
rg -n -i '\b(grep|rg)\b' skills/build-semantic-okf skills/consult-semantic-okf
```

Expected result: the only command occurrence is the documented example in
`skills/consult-semantic-okf/references/querying.md`; there is no `grep` occurrence.

Locate the evaluator's actual legacy ranking path:

```powershell
rg -n 'class LegacyIndex|def tokenize|math\.log\(|legacy_inspect_command|index = LegacyIndex|index\.search' `
  evaluations/semantic-okf-astro/scripts/evaluate_retrieval.py
```

Verify that the active legacy Python implementations do not refer to a `grep` or
`rg` executable:

```powershell
rg -n -i '\b(grep|rg)\b' `
  skills/build-semantic-okf/scripts skills/consult-semantic-okf/scripts
if ($LASTEXITCODE -eq 1) { 'NO_EXTERNAL_SEARCH_REFERENCES' }
```

Re-run the frozen direct-retrieval comparison after the append-only build exists:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.venv\Scripts\python.exe evaluations/semantic-okf-astro/scripts/evaluate_retrieval.py `
  --run-dir evaluations/semantic-okf-astro/results/runs/20260716-astro-generic-01 `
  --python .venv\Scripts\python.exe
```

The compact output is
`evaluations/semantic-okf-astro/reports/retrieval-comparison.json`; its legacy route
must be `legacy_tfidf`, and its method note must identify an evaluator-side warm
in-process TF-IDF index.

## MCP boundary

The active definitive consultant is CLI-only. Its skill requires the packaged local
CLI and explicitly states that no MCP server is required
(`skills/consult-semantic-okf-ensemble/SKILL.md:12-16`, `:71-82`). The architectural
decision is recorded in `.specs/adr/0027-retire-mcp-for-cli-only-definitive-consultation.md:25-29`
and `:72-95`: MCP discovery, transport, and publication wrappers are not active
dependencies or fallbacks.

The repository intentionally retains old MCP ADRs, reports, hashes, and metrics as
historical experiment evidence. They do not characterize the current CLI runtime and
must not be rewritten as current measurements. The frozen Astro source corpus also
contains an authoritative Astro page that discusses Astro's own Docs MCP service at
`evaluations/semantic-okf-astro/corpus/sources/mdx/guides/build-with-ai.mdx:20-35`;
that page is benchmark content, not an enabled connector. Removing either kind of
evidence would rewrite history or mutate the pinned corpus.

The following audit checks the active definitive build/consult packages and Astro
evaluation configuration for MCP runtime or server markers:

```powershell
rg -n -i '^\s*(from|import)\s+\S*mcp\b|mcp__|mcp_servers|modelcontextprotocol|mcp-remote|fastmcp' `
  skills/consult-semantic-okf-ensemble skills/build-semantic-okf-ensemble `
  evaluations/semantic-okf-astro/scripts evaluations/semantic-okf-astro/skill-arena
if ($LASTEXITCODE -eq 1) { 'NO_ACTIVE_MCP_RUNTIME_OR_CONFIG_MATCHES' }
```

This audit does not search the authoritative corpus or historical decision records,
because their textual references are retained evidence rather than active runtime
configuration.
