# Semantic OKF Storage Version Evaluation

This evaluation compares three complete Semantic OKF build-and-consult packages:

- `file-backed`: canonical Markdown, JSONL, and RDF artifacts;
- `embedding-backed`: the same authoritative core plus a hash-bound retrieval projection; and
- `turso-backed`: the same authoritative core plus a validated local Turso Database projection.

The comparison has two independent layers. `evaluation.yaml` tests whether an isolated agent can apply each version's construction, exact-evidence, discovery, aggregation, and corruption boundaries. `scripts/compare_operational.py` builds and measures the implementations directly on the 31-source, 874-record GraphRAG corpus.

## Current result

The deterministic operational comparison passes every integrity and parity gate. The concise result is in `operational-report.md`, while `operational-report.json` retains raw timings, samples, hashes, package fingerprints, counts, and evidence references.

The final Skill Arena run completed all 16 cells without infrastructure errors. Its raw score was 0/4 for the no-skill control, 4/4 for file-backed, 4/4 for embedding-backed, and 2/4 for Turso-backed. Manual contract review found both Turso rejections to be false negatives: one used the documented `knowledge.db` plus `records --contains` route without spelling the helper filename, and the other correctly grouped accepted rows in `records` rather than `rdf_statements`. The current assertions accept those supported forms. `last_report.md` preserves the raw run, and `initial_report.md` preserves the first evaluator-adjudication incident.

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
```

The command performs two fresh file-backed builds and two fresh Turso-backed builds. It proves deterministic reconstruction using physical hashes for ordinary files and the validated logical digest for `knowledge.db`; verifies byte-identical authoritative cores and record ledgers; compares exact lookup and grouped aggregation results; measures fresh CLI subprocesses; and checks the physical database hash before and after consultation.

The embedding build and retrieval evidence comes from its existing append-only offline model run because that run already produced two verified builds and 30-question retrieval results on the same manifest. The comparator verifies and fingerprints the exact report and run manifest it consumes.

## Interpretation boundaries

- CLI timings include process startup and each version's validation boundary. They are not in-process engine microbenchmarks.
- The legacy lexical timing in the embedding report uses an in-process reused index, while the embedding routes use fresh validated subprocesses. The report retains this mismatch explicitly.
- The embedding-backed packages are current worktree comparison inputs. They are not part of the Turso feature commit, so `operational-report.json` records their exact package tree hashes.
- One request per Skill Arena cell is useful for contract smoke testing but does not estimate statistical model variance. Raw reports and manual adjudications remain separate.
- Retrieval scores do not make chunks authoritative. All three versions retain the same Semantic OKF evidence layers.
