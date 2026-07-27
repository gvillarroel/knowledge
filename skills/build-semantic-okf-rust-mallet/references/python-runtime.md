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

The runtime contains PyYAML, RDFLib, pySHACL, and OWL-RL for the authoritative core, plus `pyrmallet==0.1.1` and its NumPy dependency. The pinned wheel embeds the Rust implementation; no separate Rust compiler is needed after installation.

Do not install RustMallet from an unpinned branch, download a model, or substitute another LDA implementation. A missing `pyrmallet` package is a hard build error.

## Determinism limits

The contract fixes the RustMallet package version, sampler seed, priors, iteration schedule, vocabulary filters, and eight-decimal serialization. Require two byte-identical clean builds on the release platform. Preserve the complete package lock, Python version, and platform in evaluation evidence; do not claim cross-platform byte identity until it has been measured.

## Resource limits

The core builder and retrieval projection retain normalized records, the token corpus, and topic matrices in memory. Exact JSONL output is appropriate for ordinary local research collections. Partition collections upstream when these no longer fit comfortably in memory. Do not silently skip records or publish a partial projection.
