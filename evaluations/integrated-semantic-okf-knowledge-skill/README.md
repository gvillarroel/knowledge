# Integrated Semantic OKF Knowledge Skill Evaluation

The [generator G2 report](../reports/evolution/generator-g2/README.md) records the
separate evolution of explicit structured source selection, following the
[preserved G1 infrastructure interruption](../reports/evolution/generator-g1/README.md). Its deterministic
Harbor construction metric is distinct from the historical parity study below.
See the [operating guide](../../docs/knowledge-generator-evolution.md) for the
field-selection and coverage-receipt contracts, and the
[native adapter](evolution/README.md) for reproducible task construction.

This study verifies the direct multi-family generator against the exact
separate builder and consultant pairs registered in
`evaluations/semantic-okf-datasets/families.json`.

## Scope

The matrix contains all eight canonical families on all three registered
40-question datasets. Each cell uses the same prepared evaluator-free manifest,
optional plan, `source-packed-v1` layout, Python runtime, offline model policy,
and pinned local model cache for both construction paths.

The generated artifacts are intentionally ignored under:

```text
evaluations/semantic-okf-datasets/generated/
  integrated-family-validation-20260813-02/
    astro/
    graphrag/
    qec/
```

Each dataset directory contains `ALIAS-FAMILY-expert` from
`build-semantic-okf-knowledge-skill` and `ALIAS-FAMILY-baseline` from the exact
separate canonical builder. The tracked report contains only normalized,
authentication-free evidence.

## Reproduction boundary

Before construction, run the canonical registry and staging checks described
in `evaluations/semantic-okf-datasets/README.md`. Use each staged
`input-manifest.json` host build command for the baseline, adding
`--concept-layout source-packed-v1`. Run the universal generator with the same
staged `manifest.json`, optional `plan.json`, layout, and dataset guidance. Use
the exact locked runtime for embedding and ensemble cells and force Hugging
Face and Transformers offline.

After all 48 independent outputs exist, run:

```bash
python -B \
  evaluations/integrated-semantic-okf-knowledge-skill/scripts/compare_separate_and_integrated.py \
  --model-python PATH/TO/PINNED-FAMILY-RUNTIME/PYTHON

python -B \
  evaluations/integrated-semantic-okf-knowledge-skill/scripts/compare_separate_and_integrated.py \
  --model-python PATH/TO/PINNED-FAMILY-RUNTIME/PYTHON --check
```

The default `--base-python` is the interpreter launching the comparison and
must carry the baseline, Graphify, and Turso locks. `--model-python` must carry
the prepared embedding and ensemble locks. Neither interpreter path is written
to the report.

## Acceptance gate

For every dataset-family cell, require:

- exact complete knowledge-tree bytes from the independent build paths;
- exact canonical versus generated consultant instructions, references, and
  runtime bytes;
- one exact canonical-versus-packaged native default-route payload;
- a stable façade payload that differs only by additive expert and physical
  citation fields;
- nonempty physically resolvable hit citations; and
- exact ledger-body retrieval through the generated `get` operation.

Complete knowledge and consultant byte equality is the all-question mechanical
equivalence proof. The executed query cells additionally guard command
translation and citation enrichment. This study does not claim a new
model-judged Harbor answer-quality result.
