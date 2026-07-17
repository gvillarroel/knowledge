# q031 consultation comparison after MCP retirement

## Scope

**Question:** A production router must choose among question-only or standalone-model answering, basic RAG, and GraphRAG before generation. Derive an evidence-based decision boundary for simple facts, interconnected synthesis, and noisy graph evidence, and explain why an always-use-the-graph policy is unsupported.

The five gates below are reproduced from the retained q031 Skill Arena contract. Cross-family results are descriptive, not causal: the archived treatment rows came from separate runs and bundles. The current definitive row is a direct, deterministic CLI finalizer run over a reviewed draft and complete bounded coverage; it is not a fresh Skill Arena or model generation.

## Mechanical comparison

| Alternative | Format | Contract | Evidence | Atomic answer | Negative | Score |
|---|---:|---:|---:|---:|---:|---:|
| Legacy lexical | pass | fail | fail | fail | pass | 0.4 |
| Embeddings | pass | pass | fail | fail | pass | 0.6 |
| Classical text processing | pass | fail | fail | fail | pass | 0.4 |
| Entity graph | pass | pass | fail | fail | fail | 0.4 |
| Adaptive hybrid | pass | fail | fail | fail | pass | 0.4 |
| Definitive ensemble (current CLI-only) | pass | pass | pass | pass | pass | 1.0 |

A score is the unweighted mean of the five binary gates. The current CLI-only definitive answer is the only current main alternative that passes all five. Embeddings is the strongest retained non-ensemble row at 0.6. A failed mechanical gate does not prove every sentence is wrong; it means the exact benchmark contract was not fully satisfied.

## Exact answer summaries

The full response objects, evidence bindings, result IDs, artifact hashes, response hashes, and named gates are preserved in `cli-q031-comparison.json`.

### Legacy lexical

Provenance: `archived-skill-arena-treatment`; result ID: `0f1c8221-5945-41be-92c1-6baf3eca219a`; canonical response SHA-256: `918b46b2219f4e81fd7efce8e027c467d3045645319f29e374819f66b40dc0ef`.

Use the least powerful retrieval mode that matches the question’s evidence structure. For a simple, isolated fact, prefer question-only or standalone-model answering when the fact is already reliable in the model; otherwise basic RAG is the strong default because it directly retrieves discrete information, and the snapshot reports that basic RAG is comparable to or better than GraphRAG for simple fact retrieval. For interconnected questions—multi-hop reasoning, cross-document dependency, or contextual synthesis—route to GraphRAG, since its advantage is explicitly tied to traversing connections rather than ranking isolated chunks. The boundary is therefore structural: graph retrieval is justified when answer completeness depends on linked entities, relations, or evidence paths, not merely because a graph exists. Treat noisy graph evidence as a rejection or downgrade condition. Adding an entire noisy graph can underperform answering from the question alone, and increasing retrieved-path counts eventually reduces performance as irrelevant paths accumulate. The router should therefore inspect evidence quality and confidence before generation: retain GraphRAG only when retrieved context supports the query, filter or bound the graph context when it does not, and fall back to basic RAG or standalone answering. This conditional policy is supported by the reported complementarity of intrinsic reasoning and retrieval, and by evidence that GraphRAG can both correct standalone errors and corrupt answers that were initially correct. An always-use-the-graph policy is consequently unsupported: graph structure helps selectively, while unnecessary expansion adds noise and can reduce accuracy.

### Embeddings

Provenance: `archived-skill-arena-treatment`; result ID: `03080c33-0b9c-4ee6-abd6-4f5a8fe394c0`; canonical response SHA-256: `4a6a6cbb9a023fbed2b06423fd67a2687b0aa96a319cd173bfc622da02f6d2a8`.

Use the least elaborate answering path that matches the question’s evidence structure. For an isolated, simple fact, prefer standalone answering when its confidence is high and use basic RAG when external grounding is required; graph expansion is unnecessary and can introduce irrelevant neighbors. For interconnected, multi-hop reasoning or broad synthesis that must combine evidence across documents, route to GraphRAG, because its advantage is connecting distant segments and relational chains. The boundary is therefore structural rather than a fixed hop count: choose GraphRAG when the answer depends on relationships among dispersed facts, not merely on retrieving several independent facts. If the graph is noisy, incomplete, or produced by unreliable extraction or decomposition, do not automatically route to GraphRAG. Prefer standalone answering or focused basic RAG, or require graph/path filtering and confidence checks before using graph evidence. This is a conditional policy, not a claim that one method always wins. Basic RAG is reported as comparable to or better than GraphRAG for simple fact retrieval, while graph expansion may add noise. Moreover, GraphRAG can correct standalone errors but can also turn correct standalone answers into incorrect ones, and extraction, decomposition, verifier, and retrieval errors can propagate into generation. Thus, an always-use-the-graph policy is unsupported: graph benefits are concentrated in relational synthesis, whereas its overhead and failure modes are material outside that regime.

### Classical text processing

Provenance: `archived-skill-arena-treatment`; result ID: `d93aedfb-6991-4b38-be7c-7f2df24ec88f`; canonical response SHA-256: `768127e9bf0af794c401cf73024a6e71f72d5b1babea4068c38a6b7d9df86b9e`.

Use task structure and graph quality as the routing boundary, not a universal GraphRAG default. For a localized simple fact, prefer question-only answering when no retrieval is needed; if grounding in the corpus is required, use basic vector RAG. The snapshot identifies localized fact questions as a comparative strength of conventional vector RAG rather than GraphRAG’s global-search target. For interconnected synthesis—questions requiring themes, connections, or corpus-wide coverage—select GraphRAG or another graph-based retriever, because global approaches outperform vector search on comprehensiveness and diversity across the reported datasets. The graph route should nevertheless be conditional on evidence quality and retrieval economy. Noisy or redundant graph neighborhoods are a stop or fallback condition: adding an entire noisy textual graph can perform worse than answering from the question alone, and redundant graph information can be a more important failure source than insufficient information. Extraction, decomposition, and retrieval errors can also propagate into generation. Thus the production boundary is a quality-aware cascade: standalone for sufficiently local questions, basic RAG for localized corpus facts, graph retrieval for genuinely connected or global synthesis, and fallback or pruning when graph evidence is noisy, redundant, incomplete, or costly. An always-use-the-graph policy is unsupported because GraphRAG has asymmetric effects: it corrects some standalone errors but can also corrupt answers that standalone answering got right; the reported preliminary comparison found both substantial corrections and a meaningful standalone-superiority category.

### Entity graph

Provenance: `archived-skill-arena-treatment`; result ID: `e241c82b-bd52-484f-bc5a-6d190f64ca9c`; canonical response SHA-256: `4411617a9549894099a3d1d44f34854fc9c0f4538437425f8f0a0ea4aff8d6d9`.

The snapshot supports a conditional router, not a universal GraphRAG default. For a simple, single-fact question, use question-only or a standalone model when its answer is sufficiently trusted; otherwise use basic RAG. The evidence specifically reports that basic RAG is comparable to or better than GraphRAG for simple fact retrieval because graph expansion can add noise. For questions requiring relationships across multiple passages, cross-document traversal, or global synthesis across database segments, route to GraphRAG: these are precisely the settings in which relational structure and multi-hop retrieval address the limitations of flat retrieval. However, graph evidence must pass a quality or confidence gate. Redundant graph context and too many initial nodes can introduce irrelevant material, with the latter especially harmful for single-hop questions; filtering, pruning, or falling back to basic RAG or standalone answering is therefore justified. An always-use-the-graph policy is unsupported for two independent reasons: simple facts do not consistently benefit from graph expansion, and GraphRAG can change an originally correct standalone answer into an incorrect one. The reported comparison also includes cases where the standalone model outperformed GraphRAG. Thus the boundary is task structure plus evidence quality: standalone/question-only for trusted atomic facts, basic RAG for clean isolated external facts, GraphRAG for genuinely interconnected or global synthesis, and fallback when graph noise or confidence failure dominates.

### Adaptive hybrid

Provenance: `archived-skill-arena-treatment`; result ID: `7119644d-9130-4635-91c6-3e64370f465b`; canonical response SHA-256: `67e287097b6c52c03ca10579e6c28a377a24b6eeb50bffe4ff5d5499523145fd`.

The snapshot supports a conditional router rather than universal GraphRAG. For a simple, directly answerable fact, use question-only answering when trusted graph evidence is absent or noisy; otherwise basic RAG is the appropriate retrieval option because it directly accesses discrete information and is reported as comparable to or better than GraphRAG on simple fact retrieval. Graph expansion can add irrelevant context without improving the answer. For interconnected synthesis—especially questions involving indirect dependencies, multi-hop relations, or contextual analysis—route to GraphRAG, whose intended advantage is connecting evidence and exposing relational structure that a single semantic match or ordinary retrieval may miss. The graph should be treated as a qualified evidence source, however: moderate retrieval can help, while additional paths eventually introduce noise, and an entire noisy textual graph can perform worse than answering from the question alone. Therefore the production boundary should include evidence-quality and graph-complexity checks, with filtering, fallback, or answer integration when graph confidence is weak. An always-use-the-graph policy is unsupported because the reviewed evidence explicitly says retrieval and parametric reasoning are complementary, GraphRAG can correct standalone errors but can also corrupt initially correct standalone answers, and simpler methods can win on direct facts. The result is a routing rule based on relational necessity and evidence reliability, not graph presence alone.

### Definitive ensemble (current CLI-only)

Provenance: `current-cli-finalizer`; result ID: `not applicable`; canonical response SHA-256: `817f51c5954eddd04668b3b31b919d0e205a99d83e4e9e59fabdb45124c6075e`.

Route by evidence structure and expected noise, not by a blanket preference for graphs. For a simple fact, begin with basic RAG when compact textual retrieval can directly answer the question; the corpus reports that this route can match or outperform GraphRAG because graph expansion may introduce distracting material. Keep the standalone model as a competing answer source when retrieval is weak, because reported cases show that GraphRAG corrects some standalone errors but also reverses some initially correct answers. For interconnected synthesis, GraphRAG has its clearest reported advantages on complex reasoning, contextual summarization, and creative generation, so relational or multi-part questions are the strongest candidates for graph-assisted retrieval before generation. If graph evidence is noisy, prefer pruning or fall back to question-only or basic retrieval: supplying a whole noisy textual graph has been observed to underperform the question alone. The production boundary is therefore conditional: direct factual evidence favors basic RAG; complex, interconnected synthesis can justify GraphRAG; uncertain or noisy graph evidence requires filtering, comparison with non-graph candidates, or abstention. An always-use-the-graph policy is unsupported because graph expansion can add noise and graph retrieval and standalone reasoning have complementary, rather than uniformly ordered, error profiles. The router should preserve the underlying authoritative text bindings and make the selected route answerable to evidence rather than assuming that added structure is automatically useful.

## Historical MCP reference (not current runtime)

The retired MCP treatment scored **1.0** (five of five gates). It remains useful as a historical reference, but must not be described as the active definitive consultation path.

Result ID: `3f118e39-ac2e-4b43-8b8c-f16319c06b93`; canonical response SHA-256: `38685ce0dd67c356ebcf3ba3bbfb5ab9cd89a7f64e5bb6bc1df28115ecb1db57`.

The snapshot supports routing by evidence structure, not by a blanket preference for graphs. For a simple, localized fact, use question-only or the standalone model when the model is reliable and no external grounding is required; if the fact is discrete but needs authoritative support, basic RAG is the default. This boundary is supported by results that basic RAG is comparable to or better than GraphRAG for simple fact retrieval, and by the characterization of vanilla RAG as suited to direct access to discrete information. For interconnected synthesis—multi-hop, cross-document, global, or summary-like questions—route to GraphRAG or a graph-mediated hybrid: its explicit relations, ordered paths, subgraphs, and community summaries expose dependencies that isolated chunk retrieval can miss. Before generation, filter, rank, prune, or verify the graph evidence; pre-generation checking and path reliability ordering are supported safeguards. If the graph is noisy, incomplete, redundant, or costly, do not force GraphRAG: whole noisy graphs can underperform question-only answering, extraction and decomposition errors propagate, and graph expansion adds noise, latency, tokens, and preprocessing cost. Use basic RAG, standalone answering, a hybrid fallback, or abstention according to confidence. Thus the production boundary is conditional on question breadth/depth, evidence quality, expected grounding value, and budget. The literature supports adaptive selection and complementary evidence sources, not an always-use-the-graph policy; reported advantages are also conditional on corpora, models, prompts, and metrics.

## Reproduce

```powershell
python evaluations/semantic-okf-ensemble/scripts/generate_cli_q031_comparison.py --check
```

When the ignored append-only Promptfoo results are present, the generator cross-checks the retained rows by result ID. When they are absent, it validates their checked compact response objects and hashes internally. No MCP service is needed.
