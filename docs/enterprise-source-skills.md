# Enterprise application skills: completed experiment and retained lessons

[Documentation index](README.md) · [Results by application and CTA](../evaluations/reports/enterprise-source-skills/s2/README.md)
· [Original protocol](../.specs/adr/0123-evaluate-agent-selected-enterprise-source-skills.md)
· [Retirement decision](../.specs/adr/0125-retire-enterprise-application-skill-experiment.md)

The application-split treatment is retired. On the forty exposed Enterprise
questions, nine available skills did not improve observed retrieval over one
unified expert. Raw final-evidence nDCG@10 was 82.37 versus 84.26 on a scale of
100, with 2.13 times the tokens and 1.43 times the agent latency. The agent could
choose and combine all nine skills; it opened two to four per question. This
was a real test of selection, with no task-specific routing supplied by the evaluator.

All eighty native trials completed. Semantic review was available for thirty-three
complete question pairs: required-fact coverage was 78.12% for the application
skills and 90.15% for the unified expert. Seven pairs remain unknown after eight
invalid reviewer outputs. Their full-cohort bounds overlap. These conditional
semantic means do not establish a winner over all forty questions.

The experiment used the Embeddings family of `build-semantic-okf-knowledge-skill`,
which supports eight families. Splitting by application is independent of choosing
a retrieval family. No application skill was installed, promoted, or made the
default. This single exposed, reference-enriched corpus does not establish that
application partitioning can never help a different task.

## What remains useful

1. **Preserve source content explicitly.** The original v1 manifest declared
   `body` in its schema but omitted its field mapping. Its 985 normalized records
   therefore contained title-derived text. The retained full-text adapter adds
   `fields: {body: documentText}` and the corresponding ontology property, in a
   separate projection. All 6,291,040 original body characters survived in the
   ten evaluated experts. Original v1 data and historical scores retain their
   [documented title-only scope](../evaluations/reports/enterprise-source-skills/ingestion-scope-20260907.md).
2. **Check content, not just inventories.** The retained verifier compares original
   text with `attributes.body` exactly and requires its complete rendered form in
   retrieval text. It rejects missing, duplicate, or reassigned records and
   title-only projections. Storage fidelity does not eliminate an embedding
   encoder's token limit. The canonical builder skill now states this distinction.
3. **Measure citation fidelity separately from retrieval.** Raw nDCG was much
   higher than citation-gated nDCG in both arms. Each arm had twenty-eight native
   citation-contract failures. Twenty-five cases per arm missed citation marker
   coverage; eleven unified and fourteen split cases contained a quote that was
   not an exact substring. These counts overlap. Preserve original text and
   validate the submitted citation structure; do not interpret a mechanical
   failure as a semantic judgment or relax the historical scorer after seeing results.
4. **Keep reviewer failures visible.** Eight invalid status arrays were preserved
   without retries or repairs. The existing semantic consensus code was applied
   only to complete paired outputs, with explicit denominators and full-cohort
   bounds under [ADR 0124](../.specs/adr/0124-report-unavailable-semantic-review-pairs.md).
   Validate the exact number of required statuses before aggregation.
5. **Account for the cost of routing.** The model made more searches and consumed
   more tokens when choosing among source skills. Source usage describes behavior;
   it is not an individual skill-quality ranking. Keep whole-treatment quality,
   latency, and token comparisons together.

## Retained ingestion commands

These commands prepare source text and check a built ledger. They do not launch
models, run Harbor, select an application, or publish a skill. Run from the
repository root with a fresh ignored destination:

```powershell
python -X utf8 -B evaluations/enterprise-rag-bench/fulltext_projection.py prepare --input evaluations/enterprise-rag-bench/processed/enterprise-rag-bench-40-v1/input --output tmp/enterprise-fulltext
python -X utf8 -B evaluations/enterprise-rag-bench/fulltext_projection.py prepare --input evaluations/enterprise-rag-bench/processed/enterprise-rag-bench-40-v1/input --output tmp/enterprise-fulltext --check
```

Build with the matched canonical builder using
`tmp/enterprise-fulltext/input/manifest.json` and the family's existing plan.
Then verify its ledger, substituting the actual path for `RECORDS.jsonl`:

```powershell
python -X utf8 -B evaluations/enterprise-rag-bench/fulltext_projection.py verify --input tmp/enterprise-fulltext/input --records RECORDS.jsonl
```

For a generated expert the ledger is
`references/knowledge/semantic/records.jsonl`; for a standalone knowledge folder
it is `semantic/records.jsonl`. Preparation copies only declared source documents
and the license, preserves source bytes, and writes a deterministic provenance
receipt. It leaves the original v1 dataset and evaluator files in place.
Verification supports the record-level structured rendering used here; a future
chunked representation needs its own reconstruction-aware fidelity contract.

## Preserved evidence and retired implementation

Reviewed reports remain in Git by application, question category, and CTA, with
the general comparison and historical scope correction linked from the report hub.
The [historical audit utility](../evaluations/enterprise-rag-bench/audit_historical_scope.py)
still reproduces the binding to all 114 e6 native trials.

The experiment-specific agent, source router, model transport, task generator,
review orchestration, report generator, and their tests were removed from active
tracked code. Their exact source, tests, and former execution guide are archived
under ignored `tmp/enterprise-source-skills-s2/reproduction/`, alongside the
unchanged local study, generated experts, native jobs, and semantic review evidence.
That archive preserves original relative-path assumptions; reproduction requires
restoring its source layout in a separate checkout. The completed study is not
an active execution recipe. No further model calls were made during retirement.
