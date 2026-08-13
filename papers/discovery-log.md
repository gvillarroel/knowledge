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

## 2026-08-10 scheduled run

- Active key: `papers-self-improvement-km`
- UTC publication boundary: strictly after `2026-07-26T00:00:00Z`
- Query profile SHA-256:
  `53b515266fc021e092199ef50b928e1cc202475a3fbfe6f16c4b7918d2b6efaa`
- Query lanes: 11
- Unique unregistered exact-version candidates: 407
- Truncated lanes at 200 results per lane: 0
- Abstract-reviewed finalists: 154
- Selected after complete title screening and abstract review: 25
- Abstract-reviewed finalists rejected: 129
- Remaining title-screened candidates rejected: 253

### Lane coverage

| Lane | Window results | Truncated |
|---|---:|---:|
| Long-horizon agents | 16 | No |
| Harness and agent systems | 103 | No |
| Agent/runtime/execution harness phrases | 37 | No |
| Task-state and context management | 7 | No |
| Self-improvement and recursive improvement | 19 | No |
| Self-evolution and continual learning | 50 | No |
| Long-term, persistent, episodic, and managed memory | 57 | No |
| Knowledge management, knowledge graphs, and knowledge bases | 59 | No |
| Agent skills, skill libraries, and tool use | 126 | No |
| Agent evaluation, benchmarks, and trajectory auditing | 43 | No |
| Context engineering, compression, and retrieval | 17 | No |

Lane counts overlap. The candidate count is deduplicated by exact arXiv
version. The run retained the full fourteen-day overlap, but registration
focused on newly indexed material that advanced the existing 115-paper corpus.

### Selected exact versions and decisions

| Exact version | Decision reason |
|---|---|
| `2608.07449v1` | Selected: closes the diagnosis-outcome loop and applies validation-gated utility audits to skill consolidation. |
| `2608.07440v1` | Selected: adds predictive, byte-reversible context eviction for coding agents. |
| `2608.07429v1` | Selected: makes memory revocation an explicit, auditable lifecycle operation under world-state drift. |
| `2608.07346v1` | Selected: standardizes task integration, trace capture, and multidimensional harness auditing. |
| `2608.07169v1` | Selected: transfers hierarchical teacher experience through proactive and error-triggered memory. |
| `2608.07068v1` | Selected: identifies and repairs state misalignment in on-policy distillation across memory rewrites. |
| `2608.07023v1` | Selected: combines stable entity grounding with iterative construction of novel multilingual skill concepts. |
| `2608.06992v1` | Selected: exposes disambiguation and fact provenance in a large, queryable LLM-derived knowledge base. |
| `2608.06984v1` | Selected: evaluates delayed risk propagation across seven persistent-carrier families. |
| `2608.06909v1` | Selected: provides component and chain-level causal attribution for long agent trajectories. |
| `2608.06891v1` | Selected: decomposes skill-document quality into inspectable and revision-directed signals. |
| `2608.06880v1` | Selected: treats retrieved skills as task- and interface-adaptable drafts rather than immutable instructions. |
| `2608.06811v1` | Selected: couples planning, phase-conditioned episodic retrieval, stuck detection, and grounded verification. |
| `2608.06745v1` | Selected: constructs task-conditioned relational views over persistent memory. |
| `2608.06714v1` | Selected: unifies reasoning-driven optimization over prompts, programs, and workflow structures. |
| `2608.06663v1` | Selected: supplies a cross-layer synthesis of the long-horizon planning, memory, execution, training, and evaluation gap. |
| `2608.06503v1` | Selected: evaluates compaction boundaries with paired closed-loop continuations from identical environment state. |
| `2608.06474v1` | Selected: evolves executable grader skills with disjoint validation and freezes them before policy optimization. |
| `2608.06370v1` | Selected: provides broad causal evidence for programmatic rather than rigid JSON tool invocation. |
| `2608.06329v1` | Selected: evaluates benchmark consistency, complexity, and policy coverage with actionable diagnostics. |
| `2608.06270v1` | Selected: causally separates useful tool evidence from action-induced shortcuts. |
| `2608.06197v1` | Selected: replaces costly training environments with jointly optimized, grounded world rehearsal. |
| `2608.06196v1` | Selected: gives negative mechanistic evidence about graph augmentation and query leakage in skill retrieval. |
| `2608.06144v1` | Selected: uses interleaved streams and paired controls to measure experience-derived self-evolution. |
| `2608.06057v1` | Selected: isolates stale-history tool failures and transfers policies from authoritative state views. |

### Abstract-reviewed rejections

The remaining plausible finalists were rejected after abstract review. Every
decision is recorded below by exact version and its governing reason group.

- **Already covered or version-only update (3):** `2608.05563v2`,
  `2608.05204v2`, `2607.27773v2`. The registered exact versions already cover
  the material contribution, and the abstracts did not justify a second pin.
- **Narrow domain application without a sufficiently general method (33):**
  `2608.05784v1`, `2608.05263v1`, `2608.05245v1`, `2608.04761v2`,
  `2608.04746v1`, `2608.04530v1`, `2608.04066v1`, `2608.03499v1`,
  `2608.03451v1`, `2608.03392v1`, `2608.03327v2`, `2608.03130v1`,
  `2608.02508v2`, `2608.02444v1`, `2608.02143v1`, `2608.01913v1`,
  `2608.01904v1`, `2608.01867v2`, `2608.01822v1`, `2608.01742v2`,
  `2608.01507v1`, `2608.00962v1`, `2608.00303v1`, `2607.29468v1`,
  `2607.28692v1`, `2607.27733v1`, `2607.27690v2`, `2607.26160v1`,
  `2607.25765v1`, `2607.25415v1`, `2607.24720v1`, `2607.24368v1`,
  `2607.23838v1`.
- **Training or model-internal adaptation outside the external knowledge and
  harness boundary (23):** `2608.05778v1`, `2608.04719v1`, `2608.03403v1`,
  `2608.03071v1`, `2608.02553v1`, `2608.02287v1`, `2608.01851v1`,
  `2608.01678v1`, `2608.01234v1`, `2608.00181v1`, `2607.29190v1`,
  `2607.28777v1`, `2607.28048v2`, `2607.28691v1`, `2607.27557v1`,
  `2607.27497v1`, `2607.27415v1`, `2607.27360v1`, `2607.26922v1`,
  `2607.26643v1`, `2607.26017v1`, `2607.25066v1`, `2607.23802v2`.
- **Security or governance result peripheral to the present methodology
  corpus (25):** `2608.05223v1`, `2608.04192v1`, `2608.03609v1`,
  `2608.03509v2`, `2608.03485v1`, `2608.01637v1`, `2608.01759v1`,
  `2608.01710v1`, `2608.01679v2`, `2608.00981v1`, `2607.28871v1`,
  `2607.28225v1`, `2607.28147v1`, `2607.27083v1`, `2607.27080v1`,
  `2607.27294v1`, `2607.26953v1`, `2607.25890v1`, `2607.25560v2`,
  `2607.25364v2`, `2607.25297v1`, `2607.25255v2`, `2607.24054v1`,
  `2607.23999v2`, `2607.23444v1`.
- **Incremental, weakly validated, or redundant method/benchmark (45):**
  `2608.04562v1`, `2608.04482v1`, `2608.04289v1`, `2608.04278v1`,
  `2608.03836v2`, `2608.03468v1`, `2608.03463v1`, `2608.02358v1`,
  `2608.02356v2`, `2608.02113v1`, `2608.02097v1`, `2608.01285v1`,
  `2608.01149v1`, `2608.01056v1`, `2608.01050v1`, `2608.00824v1`,
  `2608.00808v1`, `2608.00805v1`, `2608.00794v3`, `2608.02680v1`,
  `2608.02636v1`, `2607.29405v1`, `2607.28591v1`, `2607.28430v1`,
  `2607.28156v1`, `2607.28082v1`, `2607.27518v1`,
  `2607.26604v1`, `2607.26520v1`, `2607.25992v1`, `2607.25959v2`,
  `2607.25891v1`, `2607.25398v3`, `2607.25032v1`, `2607.24551v1`,
  `2607.24882v1`, `2607.24097v1`, `2607.23942v1`, `2607.23809v1`,
  `2607.23722v1`, `2607.23693v1`, `2607.23524v1`, `2608.06931v1`,
  `2608.07202v1`, `2608.07079v1`.

The other 253 title-screened candidates were rejected in aggregate as follows:

| Title-screen rejection category | Count |
|---|---:|
| Incidental `harness`/`harnessing` or other keyword collision | 17 |
| Unrelated or narrow domain-specific agent application | 52 |
| Model training, serving, hardware, or internal-cache work outside scope | 57 |
| Domain-specific benchmark or workflow without a transferable method | 23 |
| Other peripheral, redundant, or insufficiently evidenced contribution | 104 |

The overlap re-surfaced previously rejected papers; those decisions were
preserved unless new abstract evidence materially changed the assessment.

### Registration status before final verification

- Registered and synchronized all 25 selected exact versions through the
  normal arXiv adapter; every initial registration reported `created: true`.
- All 25 initial syncs used `metadata_source: arxiv-api` and produced one
  normalized document each.

### Final verification

- Reran the exact batch with `--if-missing --sync`: all 25 registrations
  reported `created: false`, so the rerun created zero duplicates.
- The key now contains 102 sources. All 25 selected records have a canonical
  exact-version URL, matching `paper_id`, real title, `last_synced_at`, and a
  normalized `paper.md` with non-empty `type` and `resource` fields.
- Exported 102 sources with no legacy Markdown files to
  `C:\Users\villa\.knowledge\exports\knowledge-export-20260810T131549Z.zip`.
- Opened the archive and verified all 25 exact-version directories and all 25
  normalized `paper.md` files, including exact `paper_id`, title, and type.
- Failures: none. Every selected sync used the arXiv API; no fallback or manual
  content injection was required.
