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

The base runtime contains PyYAML, RDFLib, pySHACL, and OWL-RL support for the authoritative core. Record chunking, native semantic chunking, and the hashing provider need no embedding library.

## Optional extras

Install LlamaIndex only when the plan selects `chunking.implementation: "llamaindex"`:

```bash
python -m pip install -r scripts/requirements-llamaindex.txt
```

Install SentenceTransformers only when the plan selects its provider:

```bash
python -m pip install -r scripts/requirements-sentence-transformers.txt
```

These files are separate so the portable baseline never imports or installs model frameworks. Optional imports occur only after the closed plan selects that backend.

## Model snapshot preflight

Prepare model weights outside the builder under a governed cache. Record the Hugging Face `namespace/repository` model ID, immutable revision, file inventory, and license. Run the build with network access disabled. The runtime forces Hugging Face and Transformers offline modes, resolves the exact cached revision with `huggingface_hub`, verifies the snapshot directory revision, and passes only the resolved local path to SentenceTransformers with `local_files_only=True`, `trust_remote_code=False`, and `device="cpu"`.

If the exact snapshot is missing, stop. Do not relax the revision, enable downloads, trust remote code, choose a hosted fallback, or substitute a different model.

## Determinism limits

The hashing provider is byte-deterministic across supported Python environments. SentenceTransformers computation may vary at insignificant floating-point digits across library or hardware builds. The contract fixes CPU execution and serializes vectors at eight decimal places after normalization. Preserve the complete package requirements, model revision, Python version, and platform in evaluation evidence.

## Resource limits

The core builder and retrieval projection retain normalized records and vectors in memory. Exact JSONL output is appropriate for ordinary local research collections. Partition collections upstream when the source, graph, or vector set no longer fits comfortably in memory. Do not silently skip records or publish a partial projection.
