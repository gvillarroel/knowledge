# Definitive ensemble reviewed expected-ID audit

The reviewed hard-ten expected identifiers and the generated three-arm Skill Arena
assertions are coherent with the exact `20260715-ensemble-final-03` bundle.

The audit passed for all 44 atomic answer groups and all 13 important-negative
groups. Across those groups it checked 113 expected-ID option links, 68 unique
authoritative claims, 71 authoritative evidence objects, 10 config-question checks,
and 40 per-question assertion blocks. It verified claim existence, paper and source
identity, authoritative paths, locators, reviewed text hashes, satisfiable
alternatives, and equality between evaluator assertions and the reviewed ground
truth.

For this definitive benchmark, every `evidence-validity` assertion carries the
same closed universe of all 831 reviewed `Paper Semantic Claim` answer bindings,
and the auditor compares that universe exactly. This includes bindings that are not
local to a particular question, so an omitted, added, or altered non-question
binding also fails the audit. The other 43 semantic records (28 `Analysis Term`
records and 15 `Research Paper` records) remain authoritative core records but are
not eligible answer-claim bindings.

Each `evidence_claim_ids` array is a logical OR set. The audit therefore requires
exact option membership but deliberately ignores option order and duplicate
spellings; the ordered sequence of atomic and negative groups remains exact. This
matches the evaluator, where any declared option may satisfy its group, and prevents
a harmless deterministic sort from being mistaken for benchmark drift. Changed,
missing, or extra option membership still fails closed.

This pass rules out stale or impossible expected identifiers as an explanation for
missed claims. Exact-ID coverage remains stricter than semantic correctness: an
answer supported by another valid record can be semantically correct while missing
the benchmark's reviewed identity set. Important-negative ID coverage proves only
that a declared anchor is present; semantic review must still confirm that the
answer states the required exclusion, contrast, or failure condition.

Reproduce the reviewed audit with:

```powershell
python evaluations/semantic-okf-adaptive-evolution/scripts/audit_expected_ids.py `
  --evaluation-dir evaluations/semantic-okf-ensemble/reviewed-benchmark `
  --bundle evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/workspace-a/knowledge `
  --config evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml `
  --frozen-benchmark evaluations/semantic-okf-ensemble/reviewed-benchmark/frozen-answer-benchmark.json
```

The machine-readable companion, `expected-id-audit-final.json`, binds the exact
auditor, reviewed benchmark, ground truth, generated config, answer bindings,
authoritative ledger, counts, and this Markdown report.
