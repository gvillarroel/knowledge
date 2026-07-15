# Entity-Graph Format

The `entity-graph/` directory is a closed, hash-bound, discovery-only projection. `entities.jsonl` stores reviewed core identities and extracted candidate phrases; `sections.jsonl` stores exact page slices; `mentions.jsonl` stores candidate phrase matches; `edges.jsonl` stores reviewed claim paths and candidate mention/co-mention paths; `lexicon.json` stores BM25 statistics.

Reviewed graph paths mirror authoritative claim records but do not replace them. Candidate phrases, mentions, co-mentions, edge weights, and rankings are not domain facts. Use `concept_path` and `record_id` from reviewed claim nodes, then verify the claim concept and exact section locator.

Ordinary inspection verifies closed files, hashes, references, record identities, exact character ranges, index, and report. Deep inspection additionally rebuilds every node, section, mention, edge, and lexical statistic in memory. Neither inspection nor search writes to the bundle.
