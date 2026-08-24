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

## 2026-08-17 scheduled run

- Active key: `papers-self-improvement-km`
- UTC publication boundary: strictly after `2026-07-27T13:17:15Z`
- Query profile SHA-256:
  `53b515266fc021e092199ef50b928e1cc202475a3fbfe6f16c4b7918d2b6efaa`
- Query lanes: 11
- Aggregate lane matches: 599
- Unique unregistered exact-version candidates: 532
- Truncated lanes at 200 results per lane: 0
- New or updated exact versions since the prior successful run: 146
- Abstract-reviewed finalists: 77
- Selected after complete title screening and abstract review: 62
- Abstract-reviewed finalists rejected: 15
- Remaining title-screened candidates rejected: 455

### Lane coverage

| Lane | Window results | Truncated |
|---|---:|---:|
| Long-horizon agents | 26 | No |
| Harness and agent systems | 161 | No |
| Agent/runtime/execution harness phrases | 55 | No |
| Task-state and context management | 9 | No |
| Self-improvement and recursive improvement | 33 | No |
| Self-evolution and continual learning | 85 | No |
| Long-term, persistent, episodic, and managed memory | 72 | No |
| Knowledge management, knowledge graphs, and knowledge bases | 90 | No |
| Agent skills, skill libraries, and tool use | 185 | No |
| Agent evaluation, benchmarks, and trajectory auditing | 54 | No |
| Context engineering, compression, and retrieval | 24 | No |

Lane counts overlap. The 532-candidate count is deduplicated by exact arXiv
version. The fourteen-day overlap re-surfaced 386 previously screened exact
versions; their earlier decisions were preserved unless arXiv returned a new
version after the previous successful run.

### Selected exact versions and decisions

| Exact version | Decision reason |
|---|---|
| `2608.14490v1` | Selected: gates actions on complete replay agreement with an executable learned world model. |
| `2608.14441v1` | Selected: evaluates self-evolution under controlled environment mutation and diagnoses memory anchoring and redesign limits. |
| `2608.14380v1` | Selected: aligns agent and environment checkpoints for informed rollback in long-horizon work. |
| `2608.14354v1` | Selected: manages research as recoverable executable states with evidence-aware transitions and budgets. |
| `2608.14270v1` | Selected: provides a live, cutoff-aware benchmark for skill adaptation under recurring evidence releases. |
| `2608.14228v1` | Selected: grounds text-to-SPARQL agents in live schemas and relation paths without curated metadata. |
| `2608.14036v1` | Selected: isolates why skills work, why retrieval collapses at scale, and twelve distinct use modes. |
| `2608.13951v1` | Selected: makes model-harness co-evolution typed, source-traceable, and reusable as verified learning data. |
| `2608.13900v1` | Selected: defines semantic ACID guarantees for persistent, concurrent agent workflows. |
| `2608.13867v1` | Selected: supplies a system-level reliability synthesis with evidence-gated practices and runnable protocols. |
| `2608.13662v1` | Selected: represents project decisions, constraints, rationale, lifecycle, provenance, and supersession in an ontology. |
| `2608.13522v1` | Selected: builds an auditable repository-scale benchmark for joint implementation and proof synthesis. |
| `2608.13417v1` | Selected: evaluates framing, execution, feedback control, experience reuse, and harness stability beyond final scores. |
| `2608.13334v1` | Selected: uses associative graph expansion from hybrid episodic anchors to recover distributed evidence. |
| `2608.13228v1` | Selected: reports a controlled invariance result while preserving a failed discovery gate and sealed confirmation split. |
| `2608.13173v1` | Selected: attributes value to individual skill steps under discrete reward cliffs. |
| `2608.13120v1` | Selected: sustains skill-evolution feedback through multi-turn probing and independent governance repair. |
| `2608.12990v1` | Selected: improves the cost-quality tradeoff through typed semantic segment-level memory consolidation. |
| `2608.12888v1` | Selected: demonstrates strong agent-controlled retrieval over immutable raw chat history without semantic index construction. |
| `2608.12880v1` | Selected: exposes treatment leakage and reconstructs execution-grounded endpoint labels. |
| `2608.12851v1` | Selected: measures skill misevolution across authoring, retrieval, and later fresh-session execution. |
| `2608.12847v1` | Selected: separates candidate retrieval from safe, target-conditioned reuse of experience. |
| `2608.12789v1` | Selected: enforces provenance and semantic authority before tool output may alter perceived state. |
| `2608.12720v1` | Selected: co-evolves memory-retrieval skills and routing with separate expansion and deployment frontiers. |
| `2608.12610v1` | Selected: separates skill content, persistence, and triggering to address prompt-residency limits. |
| `2608.12486v1` | Selected: evolves diverse skill populations and selects complementary procedures to reduce overfitting. |
| `2608.12476v1` | Selected: gives persistent memory source-bound, bitemporal, fail-closed release semantics. |
| `2608.12282v1` | Selected: re-executes API paths and isolates multi-hop, cross-source, and policy-constrained failures. |
| `2608.11977v1` | Selected: injects controlled tool failures requiring retry, switching, or justified abstention. |
| `2608.12428v1` | Selected: combines evolving memory schemas, conflict consolidation, corrective feedback, and skill distillation. |
| `2608.11888v1` | Selected: attributes functional and efficiency regressions to skills through paired differential runs. |
| `2608.11775v1` | Selected: localizes temporal loss in gist compression and validates a narrow preservation repair. |
| `2608.11772v1` | Selected: turns self-correction into a frozen, failure-specific recovery-interface policy. |
| `2608.11727v1` | Selected: controls for unprompted defaults when measuring rules across harness instruction surfaces. |
| `2608.11552v1` | Selected: revalidates common uncertainty measures on full interactive trajectories. |
| `2608.11323v1` | Selected: decomposes variance and shows that aggregate leaderboards rank specialization rather than capability. |
| `2608.11095v1` | Selected: measures catastrophic remembering and uses rationale comments to make instruction deletion safer. |
| `2608.13608v1` | Selected: evaluates learning harnesses without labels using teacher-relative longitudinal lift. |
| `2608.11079v1` | Selected: compresses skills without rollouts while preserving every extracted contract obligation. |
| `2608.10974v1` | Selected: creates a source-grounded scientific problem-solution-rationale knowledge base. |
| `2608.13606v1` | Selected: benchmarks long-term updating and temporal reasoning over year-scale multimodal experiences. |
| `2608.10906v1` | Selected: provides a large identity- and history-aware dataset for empirical research on agent skills. |
| `2608.10795v1` | Selected: persists provenance-linked mutation advice for reuse across evolutionary searches. |
| `2608.10669v1` | Selected: verifies safety violations from sandbox receipts and final state instead of one aggregate score. |
| `2608.11274v1` | Selected: defines preventive and evidential runtime contracts around checkable trajectory evidence. |
| `2608.10538v2` | Selected: generates executor-specific natural-language skills for compact models through language-level reinforcement learning. |
| `2608.10528v2` | Selected: reproduces and stress-tests anchor reranking, narrowing the conditions under which it helps. |
| `2608.10504v1` | Selected: converts validated sessions into typed wisdom and feeds attributed evidence back into optimization. |
| `2608.10502v1` | Selected: repairs propagated memory faults through dependency-guided invalidation and selective replay. |
| `2608.10450v2` | Selected: preserves the versioned software world while finite-lived agents contribute accepted local consequences. |
| `2608.10319v1` | Selected: gives negative evidence that generic procedural skills can outperform sparse personalized preferences. |
| `2608.10299v1` | Selected: organizes agent, environment, and meta co-evolution and their evaluation boundaries. |
| `2608.10216v1` | Selected: demonstrates construct invalidity in cosine similarity gates through matched semantic reversals. |
| `2608.10178v1` | Selected: separates transferable harness cores, ecosystem-specific margins, and model compensation effects. |
| `2608.10157v1` | Selected: jointly optimizes decomposed verifiers and harness policy from self-supervised graded feedback. |
| `2608.10108v1` | Selected: dynamically composes query-specific structural memory views under weak end-to-end supervision. |
| `2608.09885v1` | Selected: attributes safety failures to bounded harness artifacts and validates held-out transfer. |
| `2608.09779v1` | Selected: contributes iterative graph traversal plus text retrieval for explainable conditional GraphRAG. |
| `2608.09732v1` | Selected: exposes and detects harmful behavior that emerges only through cross-skill composition. |
| `2608.09629v1` | Selected: compares open-ended optimizer delegation with prescribed evolution under fixed constraints and budgets. |
| `2608.09096v2` | Selected: isolates intrinsic harness-evolution capability with sensitivity-aware splits and transfer tests. |
| `2608.08311v2` | Selected: documents reviewed self-modification while separating frozen evaluation snapshots from a live lineage. |

### Abstract-reviewed rejections

| Exact version | Decision reason |
|---|---|
| `2608.13560v1` | Rejected: the meta-harness contribution is evaluated only through a paper-to-poster design application. |
| `2608.13179v1` | Rejected: the main contribution is parameter-training credit assignment rather than an external harness, memory, or evaluation method. |
| `2608.11967v1` | Rejected: the reflection mechanism is primarily a policy-training method and is sufficiently covered by selected runtime-memory work. |
| `2608.12743v1` | Rejected: the transferable-memory idea is evaluated as a spatial VLM adaptation system and adds limited general evidence. |
| `2608.11350v1` | Rejected: the skill-harness evolution result remains specific to embodied fixed-interface control. |
| `2608.10963v1` | Rejected: constructs a closed-book parametric knowledge base without source-grounded acquisition or provenance. |
| `2608.10725v1` | Rejected: applies selective ontology grounding to a narrow medical multiple-choice setting. |
| `2608.10176v1` | Rejected: the retrieval contribution is primarily a public-service recommendation application. |
| `2608.09857v1` | Rejected: uses a domain-specific judge ensemble for robot permissibility without a stronger general verification result. |
| `2608.07440v2` | Rejected: version-only update; the selected `2608.07440v1` already covers the material contribution. |
| `2608.06216v2` | Rejected: version-only update; the selected `2608.06216v1` already covers the survey contribution. |
| `2608.03699v2` | Rejected: version-only update; the selected `2608.03699v1` already pins the transaction-aware memory method. |
| `2607.27652v3` | Rejected: version-only update; the selected `2607.27652v2` already pins Harness-G. |
| `2607.26722v2` | Rejected: version-only update; the selected `2607.26722v1` already pins DREvo. |
| `2607.26598v2` | Rejected: version-only update; the selected `2607.26598v1` already pins Living-Harness. |

The other 455 candidates were rejected at title screening in aggregate:

| Title-screen rejection category | Count |
|---|---:|
| Prior overlap decision preserved with no new version evidence | 386 |
| Fresh incidental `harness`/`harnessing` or other keyword collision | 12 |
| Fresh unrelated or narrow domain-specific agent application | 24 |
| Fresh model training, serving, hardware, or internal-cache work outside scope | 18 |
| Fresh domain benchmark or workflow without a transferable method | 8 |
| Fresh peripheral, redundant, or insufficiently evidenced contribution | 7 |

### Registration status

- Registered and synchronized all 62 selected exact versions through the
  normal arXiv adapter. Every initial registration reported `created: true`,
  used `metadata_source: arxiv-api` and `content_source: arxiv-pdf`, and
  produced PDF-derived normalized Markdown; no fallback or manual content
  injection was used.
- Reran the exact 62-version batch with `--if-missing --sync`: all 62 were
  existing and 0 were created, confirming zero duplicates.
- The key now contains 164 registered sources. All 62 selected sources passed
  canonical exact-version URL, matching `paper_id`, real title,
  `last_synced_at`, normalized `paper.md`, non-empty `type` and `resource`, and
  minimum-content checks.
- Exported the complete key to
  `C:\Users\villa\.knowledge\exports\knowledge-export-20260817T132224Z.zip`.
  The archive contains 426 entries and 212 normalized paper documents,
  including exact-version `paper.md` and `source-metadata.yaml` entries for all
  62 selections. Their archived `paper_id`, `type`, and `resource` fields all
  passed inspection.
- Failures: none.

## 2026-08-24 scheduled discovery

The strict discovery window started at `2026-08-03T13:26:17Z`, fourteen days
before the most recent successful run. The eleven authoritative query lanes
returned 525 aggregate matches and 430 unique unregistered exact versions.
No lane was truncated at the 200-result cap.

### Lane coverage

| Lane | Window results | Truncated |
|---|---:|---:|
| Long-horizon agents | 36 | No |
| Harness and agent systems | 138 | No |
| Agent/runtime/execution harness phrases | 41 | No |
| Task-state and context management | 10 | No |
| Self-improvement and recursive improvement | 26 | No |
| Self-evolution and continual learning | 81 | No |
| Long-term, persistent, episodic, and managed memory | 58 | No |
| Knowledge management, knowledge graphs, and knowledge bases | 80 | No |
| Agent skills, skill libraries, and tool use | 161 | No |
| Agent evaluation, benchmarks, and trajectory auditing | 52 | No |
| Context engineering, compression, and retrieval | 20 | No |

Lane counts overlap. The title screen preserved 309 prior overlap decisions
and reviewed all 121 new or revised exact versions. Abstracts were inspected
for 64 plausible finalists; 57 were selected.

### Selected exact versions and decisions

| Exact version | Decision reason |
|---|---|
| `2608.21230v1` | Selected: quantifies durable false-memory poisoning and the limits of content and additive provenance defenses. |
| `2608.21208v1` | Selected: measures cross-agent specification portability and retrieval-based mitigation. |
| `2608.21159v1` | Selected: binds authorization to provider effects across commit, retry, and recovery. |
| `2608.21156v1` | Selected: synthesizes graph engineering for tasks, agents, and evolving system state. |
| `2608.21126v1` | Selected: joins user intent, admitted evidence, realized effects, and completion checks in one contract. |
| `2608.21101v1` | Selected: evaluates progressive skill, intent, effect, and consequence monitoring across agent harnesses. |
| `2608.21027v1` | Selected: uses weak comparison-only advisors for constructive runtime intervention. |
| `2608.20797v1` | Selected: grounds trajectory evaluation in step consequences before trajectory aggregation. |
| `2608.20729v1` | Selected: calibrates persistent criterion revision with trace-anchored interventions and concealed transfer. |
| `2608.20634v1` | Selected: synthesizes persistent executable worlds and learns their construction from traces. |
| `2608.20631v1` | Selected: manages active long-horizon memory through hierarchical retention and decay. |
| `2608.20614v1` | Selected: evaluates skills through paired live trials and execution-derived skill lift. |
| `2608.20485v1` | Selected: unifies terminal-agent architecture, runtime, learning, and process-level evaluation. |
| `2608.20318v1` | Selected: isolates algorithm-design capability as a benchmark for recursive self-improvement. |
| `2608.20169v1` | Selected: reduces harness-search evaluation cost with probability-corrected adaptive task selection. |
| `2608.19901v1` | Selected: exposes source-disjoint generalization failure in malicious-skill detection. |
| `2608.19880v1` | Selected: co-evolves reusable environment harnesses while retaining original verifiers. |
| `2608.19803v1` | Selected: derives long-horizon credit from locally evidenced milestones and traps. |
| `2608.19741v1` | Selected: evaluates reliable stateful workflows through exact persistent-state effects rather than one success. |
| `2608.19626v1` | Selected: separates genuine feedback gains from oracle artifacts and placebo scaffolding. |
| `2608.19564v1` | Selected: benchmarks persist, verify, clarify, and tool-call decisions for agent memory. |
| `2608.19197v1` | Selected: makes executable environment design an adaptive self-play component. |
| `2608.19047v1` | Selected: compiles long-horizon obligations into task-conditioned agent topologies with acceptance semantics. |
| `2608.19013v1` | Selected: formalizes continual learning over prompts, memory, tools, skills, and routing. |
| `2608.18988v1` | Selected: structures evidence synthesis as revisable claim-and-support blocks. |
| `2608.18933v1` | Selected: distills entity-grounded project skills from repository-generated practice tasks. |
| `2608.18852v1` | Selected: isolates and repairs selector credit starvation in long skill libraries. |
| `2608.18704v1` | Selected: fuses fragmented multi-source memories while preserving source provenance. |
| `2608.18580v1` | Selected: grounds terminal-task instructions, environments, solutions, and verifiers in one executable state. |
| `2608.18398v1` | Selected: builds claim-to-evidence trace graphs for agent audit and artifact lineage. |
| `2608.18351v1` | Selected: trains task-conditioned least privilege with executable effect checks. |
| `2608.18307v1` | Selected: diagnoses computer-use failures at the component level under matched harnesses. |
| `2608.18066v1` | Selected: demonstrates variance, task-order sensitivity, and underspecification in self-improving agents. |
| `2608.18050v1` | Selected: binds parsed views, native files, diffs, and submissions to versioned workspace state. |
| `2608.18027v1` | Selected: evaluates continual inference-time improvement from accumulated feedback traces. |
| `2608.17756v2` | Selected: gates memory changes with paired evidence, protected slices, and replayable diagnostics. |
| `2608.17718v1` | Selected: monitors role, goal, and evidence drift over trajectory prefixes. |
| `2608.17713v1` | Selected: shows correspondence transforms can invalidate evaluation and learning credit. |
| `2608.17684v1` | Selected: audits capability, security drift, state effects, and executor compatibility after evolution. |
| `2608.17597v1` | Selected: benchmarks safety across the full agent-harness lifecycle. |
| `2608.17588v1` | Selected: combines static evidence and shadow execution to generate safer effective skills. |
| `2608.17587v1` | Selected: trains skill optimizers from matched successful and failed execution traces. |
| `2608.17528v1` | Selected: provides a reproducible harness-native agentic-RL architecture and diagnostics. |
| `2608.17499v1` | Selected: treats the next user turn as local credit for multi-turn tool-agent learning. |
| `2608.17393v1` | Selected: aligns native coding harness execution with policy-gradient training and monitoring. |
| `2608.18177v1` | Selected: introduces reversible forgetting with active, dormant, retired, and shadow-reactivation states. |
| `2608.17007v1` | Selected: checks memory-bounded tool lowerings before granting execution authority. |
| `2608.16813v1` | Selected: provides gated, bitemporal, authority-scoped knowledge-graph storage for agent writers. |
| `2608.16798v1` | Selected: optimizes opaque heterogeneous harnesses through captured black-box rollout trees. |
| `2608.16630v1` | Selected: defines coherence debt and causally tests fact availability across coding harnesses. |
| `2608.16002v2` | Selected: propagates uncertainty through trajectory dependencies for earlier failure detection. |
| `2608.15242v3` | Selected: separates responsible-role and earliest-root-step diagnosis in long trajectories. |
| `2608.14905v2` | Selected: contributes an artifact-level failure taxonomy for end-to-end autonomous research. |
| `2608.12627v3` | Selected: combines context-rich indexing with time-aware evidence retrieval for long-horizon memory. |
| `2608.09044v2` | Selected: organizes self-evolving experience as outcome-calibrated hierarchical reasoning trees. |
| `2608.07994v2` | Selected: integrates directory, vector, graph, and reflective retrieval over hierarchical enterprise knowledge. |
| `2608.03392v2` | Selected: supplies a taxonomy and reliability agenda for self-evolving coding agents. |

### Abstract-reviewed rejections

| Exact version | Decision reason |
|---|---|
| `2608.20622v1` | Rejected: proposes an enterprise harness architecture but provides no comparative empirical validation. |
| `2608.20438v1` | Rejected: studies synthetic social-feed convergence rather than reusable agent memory, harness, or evaluation methods. |
| `2608.20432v1` | Rejected: the judge contribution remains specific to Mathlib proof-style preferences. |
| `2608.19263v1` | Rejected: ECP is explicitly work in progress and leaves adoption-level empirical validation to future work. |
| `2608.17275v1` | Rejected: the attack-surface synthesis is specialized to irreversible Web3 effects. |
| `2608.16859v1` | Rejected: the agentified evaluation pipeline is confined to visual world-model outputs. |
| `2608.10725v2` | Rejected: selective ontology grounding remains a narrow medical multiple-choice method. |

The other 366 candidates were rejected at title screening in aggregate:

| Title-screen rejection category | Count |
|---|---:|
| Prior overlap decision preserved with no new version evidence | 309 |
| Fresh incidental harness/tool/memory keyword collision | 10 |
| Fresh unrelated or narrow domain-specific agent application | 21 |
| Fresh model training, serving, hardware, or internal-cache work outside scope | 11 |
| Fresh domain benchmark or workflow without a transferable method | 9 |
| Fresh peripheral, redundant, or insufficiently validated contribution | 6 |

### Registration status

- Registered all 57 exact versions and confirmed the idempotent rerun reported
  57 existing and 0 created.
- Fifty-six selections passed canonical URL, exact `paper_id`, real title,
  `last_synced_at`, PDF-derived normalized `paper.md`, `type`, and `resource`
  checks. `2608.09044v2` remained registered but incomplete because normal PDF
  synchronization failed on an unencodable surrogate pair; no adapter patch or
  manual abstract injection was used.
- A terminal-session defect accidentally left two registration processes alive.
  The duplicate was stopped, the damaged registry was rebuilt from the prior
  successful export through normal `know add arxiv` registration, and the
  current reviewed batch was then run serially. The recovered key contains 269
  registered sources; 26 historical sources were fully re-synchronized before
  arXiv stopped the historical recovery pass, while their prior source folders
  remain on disk.
- Exported the key to
  `C:\Users\villa\.knowledge\exports\knowledge-export-20260824T134352Z.zip`.
  The archive contains 538 entries and 269 `paper.md` paths. All 57 selected
  exact paths are present; 56 contain fully verified current metadata, while
  `2608.09044v2` contains only the incomplete registration projection described
  above.
- Updated the 259-paper scored catalog and added a categorized GitHub Pages
  index with text and minimum-score filters. Browser validation parsed all 259
  catalog rows, rendered every category, filtered `GraphRAG` from seven to
  three results at the 10/10 threshold, and reported no console errors.
- The repository completion gate passed with 907 tests and 89.9% total
  application coverage.
