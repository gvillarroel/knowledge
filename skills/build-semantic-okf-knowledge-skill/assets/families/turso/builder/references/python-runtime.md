# Python Runtime

## Supported environment

CPython 3.12 is the compatibility baseline used to compile `scripts/requirements.txt`. A newer CPython is supported only when the runtime smoke test passes with the exact locked dependencies. The builder uses the standard library for CSV, JSON, hashing, paths, and atomic staging; RDFLib for RDF parsing and graph construction; PyYAML for frontmatter; pySHACL for validation; and the pinned `pyturso` package for the embedded Turso Database engine.

Install and verify the runtime:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate the same environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then keep the environment activated while installing and running the builder:

```bash
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py
```

The smoke command imports every required library and emits one JSON document with the interpreter, dependency versions, Turso engine identity, and SQLite compatibility version. Treat a smoke failure on a newer interpreter as an unsupported runtime rather than bypassing the lock. A platform without a compatible wheel may need Rust and a native compiler to build `pyturso`; do not replace it with `sqlite3` or `libsql` to avoid that preflight.

## Deterministic processing

The builder performs these steps in one process:

1. validate the closed manifest;
2. discover every manifest-relative source path;
3. hash the sorted physical source inventory;
4. parse every source with its strict adapter;
5. normalize and sort records by source ID, record ID, and source path;
6. re-discover and re-hash sources to detect content or membership changes;
7. materialize concepts, RDF, provenance, SHACL, ledgers, and reports into a hidden candidate;
8. create and populate `semantic/knowledge.db` with Turso Database inside that candidate;
9. validate RDF/OKF coherence, database integrity, relational coherence, logical hashes, and database-to-file parity; and
10. publish the complete candidate through one final promotion rename.

Do not depend on filesystem enumeration or parser iteration order. JSON object order has no semantic effect. CSV fields bind by exact physical header name, not schema member order.

## Resource limits

Whole Markdown and RDF files are read in memory. The materializer also retains normalized records and RDF graphs in memory so it can validate cross-artifact coherence and insert a deterministically ordered database before publication. Full database validation scans every logical row. This is appropriate for local research libraries and ordinary document collections, not unbounded data lakes.

Split multi-gigabyte documents upstream. For a collection that no longer fits comfortably in memory, create independently versioned bundles with explicit federation or load validated RDF releases into a persistent indexed store. Do not introduce silent partial materialization.

## Strict failures

Malformed encodings, duplicate or mismatched CSV headers, invalid scalar conversions, malformed JSON, blank RDF nodes, duplicate identities, source changes during processing, SHACL violations, Turso runtime failures, failed integrity checks, schema drift, digest mismatch, and cross-layer drift are blocking errors. The builder removes its staging directory after ordinary failure and never publishes a partial snapshot.
