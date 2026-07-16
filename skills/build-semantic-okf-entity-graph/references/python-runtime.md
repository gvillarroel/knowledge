# Python Runtime

## Base environment

CPython 3.12 is the compatibility baseline for the package-local lock. Create and activate an isolated environment, then install and verify the base runtime:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py
```

On Windows PowerShell, create the environment with `py -3.12 -m venv .venv` when several Python versions are installed, then activate it with `.\.venv\Scripts\Activate.ps1`.

Set `PYTHONDONTWRITEBYTECODE=1` or invoke the entry points with `python -B` when the copied skill root itself must remain byte-for-byte read-only. Build outputs are unaffected; this only suppresses ordinary Python `__pycache__` files beside imported package scripts.

The base runtime contains PyYAML, RDFLib, pySHACL, and OWL-RL support for the authoritative core. Entity extraction, Markdown sectioning, lexical statistics, mention matching, co-mention edges, traversal, and fusion are implemented in this package with no model or optional runtime.

## Determinism limits

The graph projection is byte-deterministic across supported Python environments. Preserve the package requirements, Python version, and platform in evaluation evidence, and verify determinism with two clean builds rather than assuming it from a successful first build.

## Resource limits

The core builder and graph projection retain normalized records, sections, entities, mentions, and edges in memory. Exact JSONL output is appropriate for ordinary local research collections. Partition collections upstream when the source or derived graph no longer fits comfortably in memory. Do not silently skip records or publish a partial projection.
