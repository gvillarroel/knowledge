# Attempt 00: Invalid Hybrid Runtime Accounting

## Status

Invalid and superseded before acceptance.

## Observation

The first execution completed all 80 questions and 21 treatments, but the
reported `rrf-hybrid` latency included only reciprocal-rank fusion. It omitted
the BM25 and character-TF-IDF scoring time required to produce the two input
rankings.

## Consequence

Quality metrics and ranking digests were unaffected, but the quality-latency
Pareto frontier was not comparable. No finding from this attempt is accepted.

## Correction

The runner now reports hybrid latency as BM25 scoring plus character-TF-IDF
scoring plus fusion. Runtime-dependent analysis is kept outside the
deterministic replay projection. The accepted report was regenerated only after
this correction.
