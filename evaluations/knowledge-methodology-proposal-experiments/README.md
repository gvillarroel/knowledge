# Knowledge Methodology Proposal Experiments

This directory contains retrospective empirical tests derived from the
paper-grounded methodology audit.

Offline ablation 01 asks whether chunking, baseline choice, domain, and
finite-query uncertainty materially change paper retrieval conclusions. It is
fully retrospective and cannot qualify a production treatment.

## Frozen inputs

The GraphRAG questions, cohort descriptor, and 15 page-grounded paper Markdown
files reuse the repository's canonical tracked corpus. The QEC treatment
versions only the 40 exposed retrieval questions, cohort descriptor, and 15
page-grounded Markdown papers required by this ablation. QEC PDFs, answer
rubrics, generation artifacts, and prebuilt knowledge are intentionally outside
the retrieval input and are not required to reproduce the result.

Run:

```powershell
python evaluations/knowledge-methodology-proposal-experiments/scripts/run_offline_ablation.py --check
python evaluations/knowledge-methodology-proposal-experiments/scripts/validate_experiment.py
```

Accepted results are written to `reports/offline-ablation-01.json` and
`reports/offline-ablation-01.md`.

[`NEXT-STAGES.md`](NEXT-STAGES.md) defines the evidence required to test the
eight proposals that cannot be answered by exposed document-level qrels.

The concise go/keep/reject interpretation is in
[`reports/offline-ablation-01-decision-table.md`](reports/offline-ablation-01-decision-table.md),
with exact machine-readable values in
[`reports/offline-ablation-01-decisions.json`](reports/offline-ablation-01-decisions.json).

## Regeneration boundary

Normal reproduction is read-only. Running the ablation without an option is
also a deterministic check. `--write-report` is reserved for creating a
reviewed replacement report because machine-specific timing changes the full
report digest used by the decision record. A replacement is not accepted until
its decision JSON and table are independently recalculated, rebound to the new
report digest, and the complete validator passes.
