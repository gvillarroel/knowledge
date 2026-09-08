# Exact selected family profiles

[Development comparison](comparison.md)

Each configuration below belongs to the named evaluated candidate digest. Construction and consultation treatments retain their separate scopes. These are reproducibility records; publication does not install a default skill.

These are profile overrides. The [frozen profile helper](../../../../enterprise-evolution/profiles.py) applies them to the unchanged construction plan or consultation defaults. Reproduction also requires the campaign's frozen runtime and control plan. The complete bundle digest binds the underlying builders and consultants.

## adaptive

Candidate: `candidate-013`. Treatment: **construction**.

Complete evaluated bundle digest: `sha256:3aabacd66c90f8b131c6b45639c38c655a3f28e4048814bb18bcd5ed08796453`.

```json
{
  "plan": {
    "bm25.b": 1.0,
    "bm25.title_weight": 1.0,
    "reranking.relevance_weight": 1.0,
    "reranking.source_novelty_weight": 0.0,
    "reranking.topic_novelty_weight": 0.0
  },
  "search": {}
}
```

## classical

Candidate: `candidate-014`. Treatment: **construction**.

Complete evaluated bundle digest: `sha256:8d97f28b9ff9c45528e8b03b373a7ba0c32c90ffb46c764f672f73abf04db62d`.

```json
{
  "plan": {
    "bm25.b": 1.0,
    "bm25.title_weight": 1.0,
    "expansion.association_weight": 0.0875,
    "expansion.topic_weight": 0.05,
    "reranking.relevance_weight": 1.0,
    "reranking.source_novelty_weight": 0.0,
    "reranking.topic_novelty_weight": 0.0
  },
  "search": {}
}
```

## embeddings

Candidate: `baseline`. Treatment: **construction**.

Complete evaluated bundle digest: `sha256:0fb227d81f64ba9e930a0b720bc9b4133681ff236b45d622d390f8bb2c948746`.

```json
{
  "plan": {
    "embedding": {
      "dimension": 384,
      "model_id": "sentence-transformers/all-MiniLM-L6-v2",
      "normalize": true,
      "provider": "sentence-transformers",
      "revision": "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
    }
  },
  "search": {}
}
```

## ensemble

Candidate: `candidate-018`. Treatment: **construction**.

Complete evaluated bundle digest: `sha256:5e45b27a162ee9fcb7b74f823cc5a9c400f087970b6bcef94a79f62845a8b5a8`.

```json
{
  "plan": {
    "adaptive.bm25.b": 0.5,
    "adaptive.bm25.title_weight": 4.0,
    "adaptive.reranking.relevance_weight": 1.0,
    "adaptive.reranking.source_novelty_weight": 0.0,
    "adaptive.reranking.topic_novelty_weight": 0.0,
    "embedding.embedding": {
      "dimension": 384,
      "model_id": "sentence-transformers/all-MiniLM-L6-v2",
      "normalize": true,
      "provider": "sentence-transformers",
      "revision": "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
    },
    "policies.quality.weights": [
      1,
      1,
      1,
      8
    ]
  },
  "search": {}
}
```

## entity-graph

Candidate: `candidate-010`. Treatment: **construction**.

Complete evaluated bundle digest: `sha256:81f637cf98dcc0983005b83feef6c26fccfe58a01722930d5abba4cd4d35f199`.

```json
{
  "plan": {
    "bm25.b": 0.0,
    "query.candidate_edge_weight": 0.0,
    "query.max_hops": 1
  },
  "search": {}
}
```

## graphify

Candidate: `candidate-010`. Treatment: **consultation**.

Complete evaluated bundle digest: `sha256:b094fb922cc34f6033de2575f8fdd7b8541afdd5bfeb8a5a819c5b791c31bce6`.

```json
{
  "plan": {},
  "search": {
    "depth": 4,
    "lexical_weight": 4.0
  }
}
```

## legacy

Candidate: `candidate-003`. Treatment: **consultation**.

Complete evaluated bundle digest: `sha256:94bc21841c665d2470ee0f2a4fd8a9b00e874ee6ba65fbce223f379fa675a67e`.

```json
{
  "plan": {},
  "search": {
    "engine": "bm25",
    "k1": 2.0
  }
}
```

## turso

Candidate: `candidate-003`. Treatment: **consultation**.

Complete evaluated bundle digest: `sha256:4dab411aa251397e054691513359ee94b24ac7264922ca42c8cb707ff15dee7b`.

```json
{
  "plan": {},
  "search": {
    "engine": "bm25",
    "k1": 2.0
  }
}
```
