---
name: consult-semantic-okf-adaptive
description: Consult an existing adaptive Semantic OKF snapshot read-only through BM25, topic, PPMI term-graph, fusion, query-aspect retrieval, or facet-separated claim coverage and finalize contract-ready evidence from authoritative bindings. Use when Codex must discover diverse evidence across arbitrary declared sources, answer multi-source questions, preserve exact IDs and locators, or inspect retrieval integrity without building, repairing, or modifying knowledge.
---

# Consult Semantic OKF Adaptive

Retrieve diverse evidence from an immutable Semantic OKF snapshot, then verify factual statements in the authoritative concept, ledger, or purpose-selected RDF graph. Prefer `adaptive`, which combines the strongest full-query ranking with deterministic aspect rankings and emits exact structured evidence rows.

## Standalone read-only boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the supplied bundle as an explicit external input; never import a sibling skill or repository helper.
- Never write a cache, query, answer, lock, repair, or derived artifact into the bundle.
- Stop on a stale hash, closed-schema violation, symlink, unsafe path, orphan passage, invalid locator, statistic mismatch, or failing report.
- Treat every retrieval score, topic, expansion term, and association edge as discovery-only.

## Required references

- Read [adaptive-format.md](references/adaptive-format.md) when inspecting bundle integrity.
- Read [querying.md](references/querying.md) before choosing a mode, interpreting aspects, or citing results.

## Workflow

1. Inspect the snapshot. Add `--deep-validation` once for a newly received, evaluation-critical, or release-candidate bundle.
2. Use the ledger for exact metadata, RDF for declared joins, and adaptive search for discovery.
3. Turn the question into an explicit coverage checklist of named subjects, comparison axes, conditions, exclusions, requested mechanisms, and important negatives.
4. When the answer contract requests reviewed claims for a multi-part question, run `coverage-pack` first. It retains an ordinary top-30 evidence pack plus separate candidate lists for comma- and conjunction-delimited facets. Use `evidence-pack` for a single narrow issue.
5. Apply source, concept, and concept-type filters before ordinary search ranking.
6. Use `adaptive` for broader discovery and multi-source synthesis; use a component mode only for diagnosis or a deliberately narrower retrieval contract.
7. Inspect every `coverage_facets` row independently. Select evidence for each checklist item; repair a missing row with a focused follow-up query instead of letting one strong facet hide another.
8. After maximizing checklist coverage, minimize the selected evidence set. Prefer one directly entailing reviewed record per atomic statement; use two only for a real join or contrast, and split the statement instead of attaching loosely related support.
9. Use `ranked_bindings`, `claim_evidence`, or `evidence_rows` to discover and verify authoritative records; never reconstruct an identity from a filename or prose.
10. Resolve each ordinary retrieval locator against the matching `semantic/records.jsonl` `record.body`; open `concept_path` as the readable Markdown mirror after its YAML frontmatter, and verify that the authoritative text supports the claim.
11. For the standard structured-answer contract, construct a compact draft containing only `summary` and atomic `claims`, then pipe it to `finalize-answer --draft -` (or use a file outside the bundle when writes are allowed). It validates the word bound, sorts identifiers, and reconstructs papers, citations, and evidence exclusively from verified bindings. Return the successful command's JSON unchanged; do not manually reserialize it.
12. For another response schema, adapt authoritative fields losslessly. Do not copy an internal locator representation into a field with a different required type.
13. Answer with atomic claims, cite authoritative paths and locators, preserve important negatives, and abstain only when the snapshot cannot support a nontrivial answer.

## Inspect and search

```bash
python scripts/runtime_smoke.py
python scripts/query_semantic_okf_adaptive.py BUNDLE inspect --deep-validation
python scripts/query_semantic_okf_adaptive.py BUNDLE coverage-pack --query "compare reviewed mechanisms, exclusions, and failure boundaries" --top-k 30 --per-facet 12
python scripts/query_semantic_okf_adaptive.py BUNDLE evidence-pack --query "compare reviewed mechanisms and failure boundaries" --top-k 30
python scripts/query_semantic_okf_adaptive.py BUNDLE finalize-answer --draft - --question-id QUESTION_ID --summary-min-words 180 --summary-max-words 320
python scripts/query_semantic_okf_adaptive.py BUNDLE search --query "compare mechanisms, conditions, and failure boundaries" --mode adaptive --top-k 10
```

The default mode is `adaptive`. Available diagnostic routes are `bm25`, `topic`, `association`, and `fusion`. Repeat `--source-id`, `--concept-id`, or `--concept-type` to form a union within one filter kind; different filter kinds combine with logical AND.

## Evidence adapter

`evidence_rows` is the retrieval-to-verification contract, not automatically the user's final answer schema. Each row copies the exact source, record, concept, source path, record hash, text hash, locator, and evidence text selected by retrieval, together with the core and adaptive-index hashes. The adapter performs no entity or citation guessing. Use the row as a verification checklist, not as a substitute for opening the authoritative layer or adapting authoritative fields to the declared output types.

`evidence-pack` is the preferred adapter for reviewed-claim response contracts. It ranks every verified claim record independently, so several necessary claims from one paper can survive. Copy `claim_evidence[].locators` as canonical string tokens such as `PDF-page-7`; copy `citations[].pages` as integers such as `7`. `ranked_bindings` retains the reviewed interpretation, claim and concept identities, claim-source path, evidence-source paths, record hashes, and snapshot hashes for verification. The command performs no answer synthesis and never writes to the snapshot.

`coverage-pack` wraps that primary pack and reproducibly derives bounded lexical facets from the question itself. Each facet receives an independent, paper-diversified claim ranking so an enumeration such as systems, mechanisms, conditions, or failure modes cannot be satisfied by repeated evidence for only its strongest member. It uses no question ID, answer key, benchmark label, or ground truth. Inspect candidate authoritative text before selection; facet membership is discovery-only.

`finalize-answer` reads a compact draft from standard input with `--draft -` or from a file outside the snapshot. Standard input is preferred in a read-only sandbox. It accepts only `summary` and `claims`; every claim contains `statement` and `supporting_claim_ids`. It rejects unknown IDs and invalid word bounds, sorts and deduplicates identifiers, then derives `paper_ids`, numeric citation pages, lexically sorted locator strings, exact concept paths, and exact claim-source paths from `adaptive/answer-bindings.jsonl`. It writes nothing and emits the final JSON on standard output. It does not judge whether the prose faithfully follows the selected evidence, so verification remains required.

## Coverage closure

Treat multi-source synthesis as a set-coverage task, not a single search. Before drafting, maintain a small evidence ledger with one row per requested subject, comparison axis, condition, exclusion, mechanism, or negative. Run the complete question first, then compare the returned aspects and authoritative support against that ledger.

For each unsupported row, issue a focused query containing the missing subject and its requested axis. Prefer `adaptive`; use `bm25` for an exact identifier or rare phrase, and a component mode only to diagnose expansion. When the response contract asks for reviewed claims, follow relevant passage hits to exact claim records and retain only claims whose authoritative text supports the intended statement. Stop expanding when each checklist row has verified support or is explicitly marked unsupported. Do not fill a gap with model memory, a merely related paper, or repeated evidence for another row.

Draft only after mapping every atomic answer statement to one or more verified authoritative records and mapping each important negative to explicit supporting or absence-qualified evidence. Then perform a fidelity-reduction pass: remove unused evidence, remove merely topical records, split any statement whose complete predicate is not directly entailed, and delete recommendations or causal explanations that are not stated by the reviewed interpretations. Re-run a focused query when a named subject is absent from the draft.

Do not turn one unresolved facet into a null answer when the snapshot supports the requested comparison in part. State the supported boundary and explicitly qualify the unresolved facet. Return `answer: null` only after the primary pack and each relevant facet fail to support any nontrivial answer. This is a support threshold, not permission to fill gaps from model memory.

## Response-contract adaptation

The user's declared output contract takes precedence over the internal `evidence_rows` shape. Before serializing an answer:

- enumerate every required key, key order, type, sort rule, length bound, and cross-field invariant;
- obtain claim IDs, claim concept paths, claim-source paths, paper IDs, and claim evidence locators from the exact authoritative claim records when the contract asks for reviewed claims;
- copy evidence locators from `claim_evidence[].locators` as canonical `PDF-page-N` strings when the contract requires locator tokens;
- copy citation pages from `citations[].pages` as integers and require each evidence locator's `N` to appear in the matching paper citation;
- never place a `sources/...#PDF-page-N` string, canonical locator token, retrieval character range, record locator, or full source fragment into an integer page array;
- never substitute the paper Markdown path for a field that explicitly requires the reviewed claim's `source_path`, or vice versa;
- treat `concept_path` as a bundle-local file and validate it inside the snapshot; treat a reviewed claim's `source_path` as an authoritative source identity validated through the ledger and pinned source inventory, even when the physical source was not copied into the published bundle; and
- run a final structural pass over types, sorting, uniqueness, claim-to-evidence grounding, evidence-to-citation page agreement, and required-source coverage.

For the standard `question_id` / `answer` / `evidence` response, prefer `finalize-answer` over a manual structural pass. If it fails, revise the external draft and rerun it. Never edit the snapshot to make a draft pass.

This is a lossless projection of authoritative fields, not identity guessing. If the requested representation cannot be derived unambiguously from an authoritative record, abstain or disclose the unsupported field instead of coercing it.

## Completion gate

Before answering, confirm that:

- inspection passed and the bundle tree remained unchanged;
- filters were applied before ranking and requested/effective mode are disclosed;
- adaptive aspects and component expansions are visible;
- every requested subject, comparison axis, condition, exclusion, and important negative is either supported in the evidence ledger or explicitly reported as unresolved;
- every cited identity and locator was copied from an authoritative binding, adapted losslessly to the declared response type, and resolves exactly;
- claim evidence pages, paper citations, and response-field types agree;
- a matching structured-answer contract was emitted unchanged by a successful `finalize-answer` run;
- factual claims were checked against an authoritative layer;
- missing or contradictory support caused qualification or abstention; and
- no retrieval signal, web result, or model memory is presented as corpus ground truth.
