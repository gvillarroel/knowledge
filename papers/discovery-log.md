# Paper Discovery Log

This append-only ledger records the durable decisions from scheduled and
remediation discovery runs. API responses remain operational artifacts; this
file preserves the query boundary, completeness evidence, finalist decisions,
and registration verification needed to audit the curated catalog.

## 2026-08-09 remediation run

- Active key: `papers-self-improvement-km`
- UTC publication boundary: strictly after `2026-07-20T00:00:00Z`
- Query profile SHA-256:
  `53b515266fc021e092199ef50b928e1cc202475a3fbfe6f16c4b7918d2b6efaa`
- Query lanes: 11
- Unique unregistered exact-version candidates: 477
- Truncated lanes at 200 results per lane: 0
- Selected after title screening and abstract review: 52
- Abstract-reviewed finalists rejected: 4
- Remaining title-screened candidates rejected: 421

### Lane coverage

| Lane | Window results | Truncated |
|---|---:|---:|
| Long-horizon agents | 16 | No |
| Harness and agent systems | 132 | No |
| Agent/runtime/execution harness phrases | 40 | No |
| Task-state and context management | 11 | No |
| Self-improvement and recursive improvement | 23 | No |
| Self-evolution and continual learning | 60 | No |
| Long-term, persistent, episodic, and managed memory | 58 | No |
| Knowledge management, knowledge graphs, and knowledge bases | 75 | No |
| Agent skills, skill libraries, and tool use | 153 | No |
| Agent evaluation, benchmarks, and trajectory auditing | 50 | No |
| Context engineering, compression, and retrieval | 19 | No |

Lane counts overlap. The 477-candidate count is deduplicated by exact arXiv
version after combining every lane.

### Selected exact versions

Each exact version below was selected because its abstract provides a
transferable method, evaluation, architecture, or failure analysis. The
catalog entry in `papers/README.md` records the paper-specific rationale.

Harness, runtime, state, and long-horizon control:

- `2607.11388v1`, `2607.18235v1`, `2607.20064v2`, `2607.20972v1`
- `2607.21557v2`, `2607.22798v1`, `2607.25408v1`, `2607.25825v1`
- `2607.26598v1`, `2607.26722v1`, `2607.27652v2`, `2607.27994v1`
- `2607.28272v1`, `2607.28802v1`, `2607.29069v1`, `2607.29241v1`
- `2608.00267v1`, `2608.01918v1`, `2608.01964v1`, `2608.02276v1`
- `2608.04968v1`, `2608.05013v1`, `2608.05144v1`, `2608.05446v1`

Memory, knowledge representation, and retrieval:

- `2607.17598v1`, `2607.24663v1`, `2608.01269v2`, `2608.01711v1`
- `2608.03137v1`, `2608.03699v1`, `2608.05906v1`

Skills and self-evolution:

- `2607.27309v1`, `2608.00155v1`, `2608.03764v1`, `2608.03874v1`
- `2608.04003v1`, `2608.04828v1`, `2608.05204v1`, `2608.05563v1`
- `2608.05604v1`, `2608.05628v1`, `2608.05810v1`

Evaluation, provenance, and governance:

- `2607.20911v1`, `2607.26191v1`, `2607.27677v1`, `2608.00355v1`
- `2608.01684v1`, `2608.05573v1`, `2608.06216v1`, `2608.06301v1`
- `2608.06346v1`, `2608.06362v1`

### Rejected abstract-reviewed finalists

| Exact version | Decision reason |
|---|---|
| `2607.23588v1` | JarvisHub is a useful creative-production platform, but its contribution is primarily canvas-specific rather than a comparative or general knowledge-methodology result. |
| `2607.28147v1` | Agent Harness Distillation focuses on extracting harness intellectual property and its security defense, which is peripheral to the present methodology corpus. |
| `2608.00548v1` | DrawAI studies editable image reconstruction; its harness comparison is secondary to a domain-specific visual artifact workflow. |
| `2608.05141v1` | OctoLong contributes model mid-training data and long-context weights rather than an external memory, retrieval, harness-control, or evaluation method. |

The other 421 candidates were rejected at title screening. Dominant reasons
were incidental uses of the word “harness” or “harnessing,” unrelated applied
agent systems, narrow domain benchmarks without a transferable method, model
or hardware training work outside the external-knowledge boundary, and new
versions that lacked a reviewed reason to supersede an existing exact pin.

### Registration verification

- Registered and synchronized all 52 selected exact versions.
- Canonicalized the supplied alphaXiv target to
  `https://arxiv.org/abs/2608.01964v1`.
- Reran the same batch: 52 existing, 0 created, 0 duplicates.
- Refreshed the 25 historical sources; all 77 sources now have canonical
  versioned URLs, exact `paper_id`, real titles, and `last_synced_at`.
- arXiv API rate limiting affected the final eight sources. The normal adapter
  recovered through official arXiv abstract-page citation metadata and marked
  those syncs as `arxiv-abs-html`; no content was injected manually.
- Exported 77 sources and 77 normalized files to
  `C:\Users\villa\.knowledge\exports\knowledge-export-20260809T233605Z.zip`.
- Verified all 52 selected source IDs and the target `paper.md` are present in
  the archive.
