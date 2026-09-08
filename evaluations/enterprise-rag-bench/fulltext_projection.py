"""Prepare and verify complete Enterprise source text without changing v1 data."""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile

BODY_PROPERTY = {"name": "documentText", "kind": "datatype",
                 "domain": "EnterpriseDocument", "range": "xsd:string"}


def write_json(path: Path, value: dict) -> None:
    """Write portable deterministic JSON."""
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def linked(path: Path) -> bool:
    """Recognize links on supported Python versions, including Windows junctions."""
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def tree_hashes(root: Path) -> dict[str, str]:
    """Bind regular files without following linked input."""
    paths = sorted(root.rglob("*"))
    if linked(root) or any(linked(path) for path in paths):
        raise ValueError("Linked paths are not supported")
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def fulltext_manifest(manifest: dict) -> dict:
    """Add the missing structured field mapping; preserve other declarations."""
    result = copy.deepcopy(manifest)
    properties = result["ontology"]["properties"]
    existing = [p for p in properties if p.get("name") == "documentText"]
    if existing and existing != [BODY_PROPERTY]:
        raise ValueError("Conflicting documentText property")
    if not existing:
        properties.append(copy.deepcopy(BODY_PROPERTY))
    sources = result["sources"]
    if not sources or len({s["id"] for s in sources}) != len(sources):
        raise ValueError("Source identities must be nonempty and unique")
    for source in sources:
        if (source.get("kind") != "json" or source.get("id_field") != "id"
                or source.get("ontology_class") != "EnterpriseDocument"
                or source.get("schema", {}).get("body") != "string"):
            raise ValueError("Expected the Enterprise JSON body schema")
        fields = source.setdefault("fields", {})
        if fields.get("body", "documentText") != "documentText":
            raise ValueError("Conflicting body field mapping")
        fields["body"] = "documentText"
    return result


def source_documents(root: Path, manifest: dict) -> tuple[dict, list[Path]]:
    """Read only declared document files and require unique original identities."""
    original, paths = {}, []
    resolved = root.resolve()
    for source in manifest["sources"]:
        relative = PurePosixPath(source["path"])
        if (relative.is_absolute() or len(relative.parts) != 2
                or relative.parts[0] != "documents" or relative.suffix != ".jsonl"
                or any(part in {".", ".."} for part in relative.parts)
                or "\\" in source["path"] or ":" in source["path"]):
            raise ValueError("Expected a source path under documents/")
        incoming = root / relative
        if (any(linked(p) for p in (root, incoming, incoming.parent))
                or not incoming.resolve().is_relative_to(resolved)):
            raise ValueError("Linked or escaped source path")
        if incoming in paths:
            raise ValueError("Duplicate source path")
        paths.append(incoming)
        for line in incoming.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            identity, body = row["id"], row["body"]
            if not isinstance(identity, str) or not identity or identity in original:
                raise ValueError("Duplicate or empty document identity")
            if not isinstance(body, str) or not body.strip():
                raise ValueError("Empty or invalid original body")
            original[identity] = {"source_id": source["id"], "body": body}
    if not original:
        raise ValueError("No original documents")
    return original, paths


def prepare(source: Path, output: Path, check: bool = False) -> dict:
    """Publish a separate projection once, or check all bytes by regeneration."""
    source, output = source.absolute(), output.absolute()
    if source.resolve().is_relative_to(output.resolve()) or output.resolve().is_relative_to(source.resolve()):
        raise ValueError("Source and output trees must be disjoint")
    if output.exists() and not check:
        raise FileExistsError("Projection exists; use --check or a fresh output")
    if check and not output.is_dir():
        raise ValueError("Projection is missing")
    manifest_path = source / "manifest.json"
    if manifest_path.is_symlink() or (source / "LICENSE").is_symlink():
        raise ValueError("Linked input metadata")
    manifest = fulltext_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
    original, paths = source_documents(source, manifest)
    inputs = paths + [manifest_path]
    if (source / "LICENSE").is_file():
        inputs.append(source / "LICENSE")
    summary = {"schema_version": "enterprise-fulltext-projection/1.0",
               "document_count": len(original), "source_count": len(manifest["sources"]),
               "original_body_characters": sum(len(row["body"]) for row in original.values()),
               "source_files": {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(inputs)}}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".fulltext-", dir=output.parent) as directory:
        pending = Path(directory) / "projection"
        destination = pending / "input"
        destination.mkdir(parents=True)
        for incoming in inputs:
            target = destination / incoming.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(incoming, target)
        write_json(destination / "manifest.json", manifest)
        summary["projected_files"] = tree_hashes(destination)
        write_json(pending / "projection.json", summary)
        if check:
            if tree_hashes(pending) != tree_hashes(output):
                raise ValueError("Full-text projection drift detected")
        else:
            pending.rename(output)
    return summary


def verify(source: Path, records: Path) -> dict:
    """Require exact original bodies in the ledger and complete retrieval text."""
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    original, _ = source_documents(source, manifest)
    ledger = [json.loads(line) for line in records.read_text(encoding="utf-8").splitlines()]
    if len(ledger) != len(original) or {r["record_id"] for r in ledger} != set(original):
        raise ValueError("Knowledge inventory differs from original documents")
    for record in ledger:
        expected = original[record["record_id"]]
        if record["source_id"] != expected["source_id"]:
            raise ValueError("Knowledge source identity differs")
        if record.get("attributes", {}).get("body") != expected["body"]:
            raise ValueError("Original document body was lost or changed")
        rendered = html.escape(expected["body"], quote=False).replace("\n", " ↵ ").strip()
        if rendered not in record["body"]:
            raise ValueError("Retrieval text omitted original document content")
    return {"records": len(ledger),
            "original_body_characters": sum(len(r["body"]) for r in original.values()),
            "preserved_body_characters": sum(len(r["attributes"]["body"]) for r in ledger),
            "all_source_bodies_exact": True, "all_retrieval_bodies_complete": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--input", type=Path, required=True)
        if name == "prepare":
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--check", action="store_true")
        else:
            command.add_argument("--records", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (prepare(args.input, args.output, args.check) if args.command == "prepare"
                  else verify(args.input, args.records))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
