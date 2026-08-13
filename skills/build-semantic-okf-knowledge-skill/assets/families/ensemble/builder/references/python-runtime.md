# Python Runtime

Use CPython 3.12 with an isolated environment. Install the package-local base lock, then run the smoke test:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py
```

On Windows PowerShell, use `py -3.12 -m venv .venv` and activate with `.\.venv\Scripts\Activate.ps1`. Set `PYTHONDONTWRITEBYTECODE=1` or invoke scripts with `python -B` when the copied skill directory must remain byte-for-byte unchanged.

The base lock contains PyYAML, RDFLib, pySHACL, and OWL-RL support. Adaptive lexical retrieval, entity-graph derivation, and the hashing embedding provider need no additional packages.

Install `requirements-sentence-transformers.txt` only for a plan that pins a SentenceTransformers model and immutable revision already present in the verified local cache. Install `requirements-llamaindex.txt` only when the plan declares LlamaIndex semantic splitting. Never permit network downloads, floating revisions, provider substitution, or an implicit fallback during a build.

For deterministic release evidence, record the Python version, platform, base lock hash, optional lock hashes, model identity and revision, and plan hash. Build twice into fresh directories and compare every relative file digest.
