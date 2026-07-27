# Tantivy Runtime Contract

The package pins `tantivy==0.26.0`, the official Python binding for the Rust Tantivy search engine. A compatible binary wheel is preferred. If no wheel exists for the active interpreter and platform, installation requires a Rust compiler and the native build toolchain.

The helper must report package version `0.26.0` before inspecting or searching. Do not silently substitute a pure-Python BM25 implementation, Elasticsearch, Quickwit, another Tantivy binding, or an unpinned release.

Each search creates `tantivy.Index(schema)` without a path, adds only the already filtered passage set, commits it, queries it, and releases it with the process. This is an in-memory index. Do not pass a bundle-relative or persistent path to Tantivy.

The schema uses Tantivy's `default` analyzer for `title` and `body`, the `raw` analyzer for the stored document identity, and frequency-aware text indexing. Tantivy supplies native BM25 scoring. The classical plan's title and body weights become query-parser field boosts. The consultant accepts only the standard classical `k1=1.2` and `b=0.75` plan because those match the Tantivy/Lucene defaults exposed by this binding.
