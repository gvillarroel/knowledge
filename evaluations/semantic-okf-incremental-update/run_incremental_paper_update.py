#!/usr/bin/env python3
"""Run a real-paper incremental Semantic OKF refresh and query acceptance check."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER = REPO_ROOT / "skills" / "build-semantic-okf" / "scripts"
CONSULT = REPO_ROOT / "skills" / "consult-semantic-okf" / "scripts"
PAPERS = (
    {
        "arxiv_id": "2005.11401",
        "version": "v4",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
    },
    {
        "arxiv_id": "2603.18012",
        "version": "v1",
        "title": "DynaRAG: Bridging Static and Dynamic Knowledge in Retrieval-Augmented Generation",
    },
)


def sha256_file(path: Path) -> str:
    """Hash one run artifact as raw bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_json(command: list[str]) -> dict[str, Any]:
    """Run one repository command and parse its JSON stdout."""

    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode not in {0, 3}:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not emit JSON: {completed.stdout}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("command JSON must be an object")
    return payload


def download_pdf(paper: dict[str, str], destination: Path) -> dict[str, Any]:
    """Download one exact arXiv PDF and return its pinned acquisition metadata."""

    identity = f"{paper['arxiv_id']}{paper['version']}"
    url = f"https://arxiv.org/pdf/{identity}"
    response = requests.get(
        url,
        timeout=120,
        headers={"User-Agent": "knowledge-incremental-evaluation/1.0"},
    )
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError(f"arXiv response is not a PDF: {url}")
    destination.write_bytes(response.content)
    return {
        "identity": identity,
        "url": url,
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
    }


def extract_markdown(
    paper: dict[str, str],
    pdf_path: Path,
    markdown_path: Path,
) -> dict[str, Any]:
    """Extract page-delimited PDF text into one traceable Markdown input."""

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").replace("\r\n", "\n").replace("\r", "\n")
        pages.append(f"## PDF page {number}\n\n{text.strip()}\n")
    identity = f"{paper['arxiv_id']}{paper['version']}"
    metadata = {
        "title": paper["title"],
        "arxiv_id": paper["arxiv_id"],
        "version": paper["version"],
        "paper_url": f"https://arxiv.org/abs/{identity}",
    }
    markdown_path.write_text(
        "---\n"
        + json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n---\n\n"
        + f"# {paper['title']}\n\n"
        + "\n".join(pages),
        encoding="utf-8",
        newline="\n",
    )
    return {
        "identity": identity,
        "pages": len(reader.pages),
        "bytes": markdown_path.stat().st_size,
        "sha256": sha256_file(markdown_path),
    }


def manifest_payload() -> dict[str, Any]:
    """Return the closed Semantic OKF plan used by this acceptance run."""

    return {
        "schema_version": "1.0",
        "bundle": {
            "title": "Incrementally updated RAG paper knowledge",
            "description": "Version-pinned papers used to verify incremental knowledge refresh.",
            "base_iri": "https://example.org/incremental-rag/",
            "ontology_iri": "https://example.org/ontology/incremental-rag",
            "version_iri": "https://example.org/ontology/incremental-rag/1.0.0",
            "prefix": "irag",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "ResearchPaper", "label": "research paper"}],
            "properties": [
                {
                    "name": "arxivId",
                    "kind": "datatype",
                    "domain": "ResearchPaper",
                    "range": "xsd:string",
                },
                {
                    "name": "version",
                    "kind": "datatype",
                    "domain": "ResearchPaper",
                    "range": "xsd:string",
                },
                {
                    "name": "paperUrl",
                    "kind": "datatype",
                    "domain": "ResearchPaper",
                    "range": "xsd:string",
                },
            ],
        },
        "rules": [
            {
                "name": "ArxivIdentityRule",
                "target_class": "ResearchPaper",
                "path": "arxivId",
                "min_count": 1,
                "max_count": 1,
                "datatype": "xsd:string",
                "message": "Every accepted paper requires one version-independent arXiv ID.",
                "basis": {
                    "kind": "operational-policy",
                    "references": ["INCREMENTAL-PAPER-1"],
                },
            }
        ],
        "sources": [
            {
                "id": "papers",
                "kind": "markdown",
                "path": "raw/*.md",
                "concept_type": "Research Paper",
                "ontology_class": "ResearchPaper",
                "fields": {
                    "arxiv_id": "arxivId",
                    "version": "version",
                    "paper_url": "paperUrl",
                },
            }
        ],
    }


def query(bundle: Path, needle: str) -> dict[str, Any]:
    """Run the generic read-only ledger query against one published snapshot."""

    return run_json(
        [
            sys.executable,
            str(CONSULT / "query_semantic_okf.py"),
            str(bundle),
            "ledger",
            "--contains",
            needle,
            "--all",
            "--show-content",
            "--validate",
            "--format",
            "json",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the acceptance-run CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute the append-only paper acquisition, refresh, and query run."""

    args = build_parser().parse_args(argv)
    if args.run_dir:
        run_dir = args.run_dir.expanduser().resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = Path(__file__).resolve().parent / "results" / stamp
    if run_dir.exists():
        raise RuntimeError(f"run directory already exists: {run_dir}")
    raw = run_dir / "raw"
    downloads = run_dir / "downloads"
    raw.mkdir(parents=True)
    downloads.mkdir()
    cache = run_dir / "cache"
    bundle = run_dir / "bundle"
    manifest = run_dir / "manifest.json"
    manifest.write_text(
        json.dumps(manifest_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    acquisitions: list[dict[str, Any]] = []
    baseline = PAPERS[0]
    baseline_identity = f"{baseline['arxiv_id']}{baseline['version']}"
    baseline_pdf = downloads / f"{baseline_identity}.pdf"
    baseline_markdown = raw / f"{baseline_identity}.md"
    acquisitions.append(
        {
            "download": download_pdf(baseline, baseline_pdf),
            "extraction": extract_markdown(baseline, baseline_pdf, baseline_markdown),
        }
    )
    build = run_json(
        [
            sys.executable,
            str(BUILDER / "build_semantic_okf.py"),
            str(manifest),
            str(bundle),
            "--cache-dir",
            str(cache),
            "--output-format",
            "json",
        ]
    )
    before = query(bundle, "DynaRAG")
    if before["returned"] != 0:
        raise RuntimeError("baseline unexpectedly contains the delta paper")

    delta = PAPERS[1]
    delta_identity = f"{delta['arxiv_id']}{delta['version']}"
    delta_pdf = downloads / f"{delta_identity}.pdf"
    delta_markdown = raw / f"{delta_identity}.md"
    acquisitions.append(
        {
            "download": download_pdf(delta, delta_pdf),
            "extraction": extract_markdown(delta, delta_pdf, delta_markdown),
        }
    )
    refresh = run_json(
        [
            sys.executable,
            str(BUILDER / "refresh_semantic_okf.py"),
            "update",
            str(manifest),
            str(bundle),
            "--cache-dir",
            str(cache),
            "--output-format",
            "json",
        ]
    )
    after = query(bundle, "DynaRAG")
    retained = query(bundle, "non-parametric memory")
    files = refresh["build"]["incremental"]["files"]
    if (
        refresh["status"] != "updated"
        or files["processed"] != 1
        or files["reused"] != 1
        or after["returned"] != 1
        or retained["returned"] < 1
    ):
        raise RuntimeError("incremental acceptance conditions were not met")
    delta_record = after["records"][0]
    content = str(delta_record.get("content", ""))
    if "selectively invokes external APIs" not in content:
        raise RuntimeError("updated answer evidence does not contain the expected DynaRAG behavior")

    receipt = {
        "schema_version": "semantic-okf-incremental-paper-run/1.0",
        "status": "pass",
        "run_dir": str(run_dir),
        "manifest_sha256": sha256_file(manifest),
        "acquisitions": acquisitions,
        "baseline": {
            "build": build["incremental"],
            "dynarag_query_returned": before["returned"],
        },
        "refresh": {
            "status": refresh["status"],
            "changes": refresh["changes"],
            "incremental": refresh["build"]["incremental"],
        },
        "updated_queries": {
            "dynarag": {
                "returned": after["returned"],
                "title": delta_record["title"],
                "concept_path": delta_record["concept_path"],
                "evidence_phrase": "selectively invokes external APIs",
            },
            "retained_baseline": {
                "needle": "non-parametric memory",
                "returned": retained["returned"],
            },
        },
    }
    receipt_path = run_dir / "receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": "pass", "receipt": str(receipt_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
