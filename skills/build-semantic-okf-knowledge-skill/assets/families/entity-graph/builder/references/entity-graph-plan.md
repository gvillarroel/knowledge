# Entity-Graph Plan

The plan is a closed JSON object. Unknown or missing members fail. Schema `2.0` is the source-generic default; schema `1.0` remains accepted without semantic or output changes for frozen paper-corpus reproduction.

## Source-generic schema 2.0

Declare sorted, unique, nonempty `selection.source_ids`. A selected source may be Markdown, CSV, JSON, or RDF and may produce any positive number of records. Claims, vocabularies, `paper_id`, arXiv identifiers, and one-record-per-source layouts are not required.

Use this exact sectioning object:

```json
{
  "strategy": "markdown-headings-or-bounded-record-v1",
  "maximum_characters": 4000
}
```

The sectioner recognizes ATX Markdown headings outside fenced code. It preserves heading paths, uses non-overlapping exact Unicode character ranges, and splits an oversized heading block at deterministic paragraph, line, or hard character boundaries. A record without headings uses the same bounded full-record fallback. Every locator explicitly targets `semantic/records.jsonl` `record.body`; it is not a byte offset into an original CSV, JSON, RDF, or frontmatter-bearing Markdown file.

Every selected record receives the structured identity `{kind: "source-record", source_id, record_id}` and a deterministic `document_id`. This default never guesses identity from a title, filename, URL, or identifier-like string.

The remaining objects retain the version 1 parameter families:

- `tokenization`: `ascii-alphanumeric-v1`, `english-v1`, and minimum token length;
- `extraction`: n-gram range, section-frequency floor, maximum section fraction, global candidate cap, and per-section cap;
- `bm25`: `k1` and `b`;
- `graph`: per-section co-mention cap, frequency floor, neighbor cap, and evidence-section cap; and
- `query`: resolved entities, traversal bounds and weights, mention weight, candidate pool, `max_per_document`, and reciprocal-rank-fusion constant.

Candidate edge weight should remain below reviewed structural-edge weight. Parameter changes create a new non-authoritative projection; they never change the authoritative core.

## Legacy schema 1.0

Schema `1.0` declares sorted `paper_source_ids`, `claim_source_ids`, and one `vocabulary_source_id`. Each paper source produces exactly one record, claims are reviewed, vocabulary terms use the established method/dimension kinds, and `sectioning.strategy` is `pdf-page-headings-v1`. Each literal `## PDF page N` heading begins an exact page section. `max_per_paper` controls diversity.

Use schema `1.0` only when reproducing a bundle that relies on its reviewed-claim and PDF-page contracts. Do not convert an arbitrary corpus into fake papers or synthesize page headings to satisfy it.
