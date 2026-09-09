# Harbor Final Evaluation Report

Generated: 2026-09-09T17:19:05.765991+00:00
Reward gate: `reward` >= 0.8

## Outcome

| Job | Skills | Trials | Passed | Verifier failed | Errors | Pass rate | Reward avg | Tokens avg | Agent time avg | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| enterprise-e10-legacy-g000-development-baseline | build-semantic-okf-knowledge-skill@sha256:2554e639 | 1/1 | 0 | 1 | 0 | 0.0% | 0.611 | 0.0 | 72,198.7 ms | $0.0000 |
| enterprise-e10-legacy-g000-development-retained-start | build-semantic-okf-knowledge-skill@sha256:8d1a50d4 | 1/1 | 0 | 1 | 0 | 0.0% | 0.724 | 0.0 | 78,348.1 ms | $0.0000 |
| enterprise-e10-embeddings-g000-development-baseline | build-semantic-okf-knowledge-skill@sha256:2554e639 | 1/1 | 0 | 1 | 0 | 0.0% | 0.635 | 0.0 | 986,248.2 ms | $0.0000 |

## Task and agent breakdown

| Job | Task | Agent | Model | Passed | Errors | Reward avg | Tokens avg | Agent time avg |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| enterprise-e10-legacy-g000-development-baseline | retrieval-e30a639975c480763fb8 | enterprise-stratified-retrieval | local/deterministic-retrieval-v3 | 0/1 | 0 | 0.611 | 0.0 | 72,198.7 ms |
| enterprise-e10-legacy-g000-development-retained-start | retrieval-e30a639975c480763fb8 | enterprise-stratified-retrieval | local/deterministic-retrieval-v3 | 0/1 | 0 | 0.724 | 0.0 | 78,348.1 ms |
| enterprise-e10-embeddings-g000-development-baseline | retrieval-9ac398e7cc362bae31fc | enterprise-stratified-retrieval | local/deterministic-retrieval-v3 | 0/1 | 0 | 0.635 | 0.0 | 986,248.2 ms |

## Failures and errors

- `enterprise-e10-legacy-g000-development-baseline/retrieval-e30a639975c480763fb8__UvahGGT`: reward=0.611052744442418
- `enterprise-e10-legacy-g000-development-retained-start/retrieval-e30a639975c480763fb8__ErWHG72`: reward=0.7237626950008386
- `enterprise-e10-embeddings-g000-development-baseline/retrieval-9ac398e7cc362bae31fc__WjrcR4i`: reward=0.6350525198647472

## Harbor artifacts

- `enterprise-e10-legacy-g000-development-baseline`: `/mnt/c/Users/villa/dev/knowledge/tmp/e10/search/legacy/development/generation-000/harbor-jobs/enterprise-e10-legacy-g000-development-baseline`
- `enterprise-e10-legacy-g000-development-retained-start`: `/mnt/c/Users/villa/dev/knowledge/tmp/e10/search/legacy/development/generation-000/harbor-jobs/enterprise-e10-legacy-g000-development-retained-start`
- `enterprise-e10-embeddings-g000-development-baseline`: `/mnt/c/Users/villa/dev/knowledge/tmp/e10/search/embeddings/development/generation-000/harbor-jobs/enterprise-e10-embeddings-g000-development-baseline`
