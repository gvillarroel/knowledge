# Canonical Family Contracts

## Contents

- [Selection matrix](#selection-matrix)
- [Stable direct-generation contract](#stable-direct-generation-contract)
- [Family-specific consultation](#family-specific-consultation)
- [Model and runtime boundary](#model-and-runtime-boundary)

## Selection matrix

| Family | Prefer when | Plan | Default generated search |
|---|---|---:|---|
| `legacy` | Ledger, Markdown, RDF, and SPARQL are sufficient | No | `ledger` |
| `embeddings` | Paraphrase and vector discovery matter | Yes | `auto` |
| `classical` | Offline BM25, PPMI, topics, and fusion are required | Yes | `fusion` |
| `adaptive` | Deterministic aspect routing and diversification matter | Yes | `adaptive` |
| `entity-graph` | Entity, relationship, section, or multi-hop discovery matters | Yes | `fusion` |
| `ensemble` | Several independently validated signals justify size and latency | Yes | `default` policy |
| `graphify` | Reciprocal lexical graph traversal is intended | No | `graphify` |
| `turso` | A local Turso-backed indexed projection is required | No | `records` |

Do not select a family by name alone. Freeze the intended questions, runtime,
identity grouping, dependency policy, and hard gates before comparing families.

## Stable direct-generation contract

Every family uses the same outer operation:

1. validate explicit inputs and reject links or overwrites;
2. run the exact package-local family builder directly into the generated
   expert's `references/knowledge/` candidate;
3. run the exact matched family validator;
4. copy only the matched read-only consultant, its references, and declared
   requirements into the generated expert;
5. bind every non-knowledge file, the complete knowledge tree, the source
   manifest, optional plan, family identity, routes, and record count;
6. verify every record-to-physical-evidence mapping;
7. run the generated expert's native verification; and
8. publish the candidate atomically or compare it through `--check`.

The generated skill is read-only even though its generator is write-capable.
It cannot import builder code or reach back into this package.

## Family-specific consultation

The generated `scripts/query_expert_knowledge.py` provides a stable `verify`,
`inspect`, `search`, and `get` façade. `search` translates its common arguments
to the exact native family CLI and then adds physical citation fields without
removing or changing native fields. Advanced family operations remain available
under `scripts/native/` and are documented in `references/consultation.md` and
`references/consultation/`.

The façade verifies all manifest, artifact, and knowledge-tree bindings before
each command and confirms the knowledge tree again after native consultation.
Native results containing authoritative record identities gain:

- `logical_concept_path`;
- `physical_concept_path`;
- `evidence_path`;
- `evidence_anchor` when source-packed; and
- `citation`.

## Model and runtime boundary

Legacy, classical, adaptive, and entity-graph consultation have deterministic
offline baselines. Graphify and Turso require their declared local packages.
Embedding and ensemble plans may select a pinned sentence-transformer and
LlamaIndex construction path. Such plans require the exact optional locks and
the declared model revision/cache; they must never silently fall back during
build or validation. Generated experts carry the matched consultant's baseline
and optional requirement locks.
