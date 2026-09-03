# tau3 banking-knowledge evaluation

This evaluation tests the repository's integrated classical and chunked-classical knowledge-skill builders against the public `sierra-research/tau3-bench` banking-knowledge domain. The domain contains 97 Harbor tasks with required-document qrels and a 698-document Rho-Bank corpus.

The recorded outcome is in [REPORT.md](REPORT.md).

The checked-in configuration is reproducible and source-bound. It pins upstream release `v1.0.0` at commit `17e07b1da2bbc0cadfddeea36412686e0604127b`, verifies every downloaded Harbor task against the corresponding upstream task, preserves one evidence identity per knowledge document, physically separates skill input from evaluator qrels, and records path-sensitive digests.

## Evidence boundary

This is a retrospective retrieval diagnostic, not an official tau3 end-to-end score and not sealed validation or promotion evidence. The query is `task.user_scenario.instructions`; qrels are `task.required_documents`. No expected action or expected answer is used as query text. The full scenario is an oracle-context ceiling because a live agent would have to elicit those facts across a conversation.

An official conversational run additionally requires a model-backed tau3 user simulator and, for some tasks, a model-backed verifier. Do not report an official score unless those conversations complete under the original verifier. The public Harbor task Dockerfiles also clone the latest upstream repository; this harness avoids that reproducibility gap by checking a pinned clone.

## Reproduce

From the repository root:

```powershell
harbor download sierra-research/tau3-bench `
  --output-dir evaluations/semantic-okf-datasets/generated/external

git clone https://github.com/sierra-research/tau2-bench.git `
  evaluations/semantic-okf-datasets/generated/external/tau2-v100
git -C evaluations/semantic-okf-datasets/generated/external/tau2-v100 `
  checkout --detach 17e07b1da2bbc0cadfddeea36412686e0604127b

python evaluations/tau3-banking-knowledge/tau3_banking_knowledge_eval.py prepare
python evaluations/tau3-banking-knowledge/tau3_banking_knowledge_eval.py prepare --check
python evaluations/tau3-banking-knowledge/tau3_banking_knowledge_eval.py build
uv run --isolated --no-project --with rank-bm25 python -B `
  evaluations/tau3-banking-knowledge/tau3_banking_knowledge_eval.py evaluate
```

`build` exercises both local skill packages through deterministic generation or `--check`, independent deep validation, packaged runtime smoke tests, and packaged deep verification. `evaluate` runs BM25, association, topic, and fusion retrieval for all 97 tasks, compares both generated experts at every rank, evaluates the chunked context selector, and computes the exact whitespace-tokenized upstream BM25 baseline.

Generated corpora, experts, receipts, and detailed results are written below `evaluations/semantic-okf-datasets/generated/external/tau3-banking-knowledge-evaluation-v5/` and remain ignored evaluation artifacts.
