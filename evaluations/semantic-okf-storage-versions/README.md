# Semantic OKF Storage Version Evaluation

This evaluation compares four complete Semantic OKF build-and-consult packages:

- `file-backed`: canonical Markdown, JSONL, and RDF artifacts;
- `embedding-backed`: the same authoritative core plus a hash-bound retrieval projection; and
- `turso-backed`: the same authoritative core plus a validated local Turso Database projection; and
- `graphify-backed`: the same authoritative core plus a hash-bound Graphify structural projection for linked-heading discovery and bounded neighborhood traversal.

The comparison has two independent layers. `evaluation.yaml` tests whether an isolated agent can apply each version's construction, exact-evidence, discovery, aggregation, and corruption boundaries. `scripts/compare_operational.py` measures the file, embedding, and Turso baselines, while `scripts/compare_graphify.py` freezes those results and builds and evaluates Graphify directly on the same 31-source, 874-record GraphRAG corpus and 30 retrieval questions.

## Current result

Both deterministic operational comparisons pass every integrity and parity gate. The baseline result is in `operational-report.md` and `operational-report.json`. The Graphify extension is in `graphify-operational-report.md` and `graphify-operational-report.json`, including all 30 cases, 300 independently validated hits, timings, hashes, and per-case evidence status.

The expanded Skill Arena run `eval-Tee-2026-07-17T01:41:47` completed all 20 cells without adapter errors. Raw scores were 0/4 for the no-skill control, 3/4 for file-backed, 3/4 for embedding-backed, and 4/4 for both Turso-backed and Graphify-backed. Manual contract review found the two treatment rejections to be assertion false negatives: both answers validated first, stopped on failure, kept the release immutable, used the authoritative RDF route, and explicitly prohibited repair inside a list, rather than using one of three exact phrases. The current assertion accepts those semantically equivalent forms. `last_report.md` preserves the unmodified raw run; the adjudicated treatment contract score is 4/4 for every installed package.

The agent evaluation is evidence about instruction usability, not an engine benchmark. The operational report is the primary evidence for choosing a storage version.

## Reproduce the configuration checks

```powershell
skill-arena val-conf evaluations/semantic-okf-storage-versions/evaluation.yaml
$configAuthor = Join-Path $env:USERPROFILE '.agents\skills\skill-arena-config-author'
node "$configAuthor\scripts\validate-evaluation-design.js" `
  evaluations/semantic-okf-storage-versions/evaluation.yaml `
  --coverage evaluations/semantic-okf-storage-versions/prompt-coverage.json
skill-arena evaluate evaluations/semantic-okf-storage-versions/evaluation.yaml --dry-run
```

Run the live matrix with:

```powershell
skill-arena evaluate evaluations/semantic-okf-storage-versions/evaluation.yaml `
  --markdown-output evaluations/semantic-okf-storage-versions/last_report.md
```

## Reproduce the operational comparison

Choose a work directory that does not exist. The comparator is create-only and refuses to replace prior outputs.

```powershell
python evaluations/semantic-okf-storage-versions/scripts/compare_operational.py `
  --work-root tmp/semantic-okf-storage-version-run-NEW `
  --iterations 5

python evaluations/semantic-okf-storage-versions/scripts/compare_graphify.py `
  --work-root tmp/semantic-okf-storage-graphify-run-NEW `
  --iterations 5
```

The baseline command performs two fresh file-backed builds and two fresh Turso-backed builds. It proves deterministic reconstruction using physical hashes for ordinary files and the validated logical digest for `knowledge.db`; verifies byte-identical authoritative cores and record ledgers; compares exact lookup and grouped aggregation results; measures fresh CLI subprocesses; and checks the physical database hash before and after consultation.

The Graphify comparator requires a new work root, consumes the frozen prior operational report, builds two fresh Graphify-backed releases, verifies deterministic reconstruction and authoritative-core parity, runs five exact and aggregate consultations, evaluates all 30 existing retrieval questions, validates every returned hit against the ledger and exact concept body, and confirms that every consultation leaves the release unchanged.

The embedding build and retrieval evidence comes from its existing append-only offline model run because that run already produced two verified builds and 30-question retrieval results on the same manifest. The comparator verifies and fingerprints the exact report and run manifest it consumes.

## Interpretation boundaries

- CLI timings include process startup and each version's validation boundary. They are not in-process engine microbenchmarks.
- The legacy lexical timing in the embedding report uses an in-process reused index, while the embedding routes use fresh validated subprocesses. The report retains this mismatch explicitly.
- Graphify discovery uses lexical scoring plus breadth-first traversal to depth 2 over a derived Markdown heading/link graph; it does not use semantic LLM extraction or clustering.
- The Graphify graph is a non-authoritative retrieval projection. Returned records are hydrated from unchanged OKF concepts, and exact lookup and aggregation intentionally use `semantic/records.jsonl`.
- Graphify timings include full release validation plus a fresh process. They are not Graphify engine microbenchmarks.
- The Graphify projection pins `graphifyy==0.9.17`; temporary view digests are regenerated from the authoritative ledger during validation.
- The embedding-backed packages are current worktree comparison inputs. They are not part of the Turso feature commit, so `operational-report.json` records their exact package tree hashes.
- One request per Skill Arena cell is useful for contract smoke testing but does not estimate statistical model variance. Raw reports and manual adjudications remain separate.
- Retrieval scores do not make chunks or graph nodes authoritative. All four versions retain the same Semantic OKF evidence layers.
