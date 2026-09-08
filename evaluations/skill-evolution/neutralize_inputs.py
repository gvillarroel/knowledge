"""Normalize incidental agent-visible metadata before oracle construction and sealing."""
from __future__ import annotations

import hashlib
import json

from prepare_experiment import WORK, sha, tree, write_json


def main():
    receipts = []
    for split, names in [("development", ("enterprise", "astro", "architecture", "data-science")), ("validation", ("fiqa", "scifact"))]:
        for name in names:
            root = WORK / "development-inputs" / name if split == "development" else WORK / "curator/validation-inputs" / name
            source = root / "input/manifest.json"
            before = sha(source)
            manifest = json.loads(source.read_text(encoding="utf-8"))
            manifest["bundle"].update(title="Source-grounded document collection", description="Read-only source collection with authoritative evidence identities.",
                base_iri="https://example.org/knowledge/collection/", ontology_iri="https://example.org/ontology/collection", version_iri="https://example.org/ontology/collection/1", prefix="collection")
            write_json(source, manifest)
            qrels = WORK / f"curator/{split}/{name}-qrels.json"
            rows = json.loads(qrels.read_text(encoding="utf-8"))
            mappings = []
            for row in rows:
                original = row["id"]
                row["id"] = hashlib.sha256(("query-v1:" + name + ":" + original).encode()).hexdigest()[:24]
                mappings.append({"original": original, "opaque": row["id"]})
            write_json(qrels, rows)
            write_json(root / "queries.json", [{"id": row["id"], "question": row["question"]} for row in rows])
            write_json(WORK / f"curator/{split}/{name}-query-identities.json", mappings)
            if split == "validation":
                provenance = WORK / f"curator/{split}/{name}-provenance.json"
                value = json.loads(provenance.read_text(encoding="utf-8"))
                value["files"] = tree(root)
                value.setdefault("preseal_corrections", []).append("Uniform neutral bundle metadata and opaque query identities across all corpora; original queries, selected sources, bodies and relevance membership unchanged. Reuses unconsumed sampling before any candidate or gate result.")
                write_json(provenance, value)
            receipts.append({"split": split, "source_manifest_before_sha256": before, "source_manifest_after_sha256": sha(source), "query_count": len(rows), "source_files": tree(root)})
    write_json(WORK / "curator/neutralization.json", {"status": "prepared", "method": "One neutral bundle metadata template and one opaque ID scheme for all cohorts; no candidate result observed.", "cohorts": receipts})
    print(json.dumps({"stage": "neutral-agent-metadata", "cohorts": len(receipts), "status": "prepared"}))


if __name__ == "__main__":
    main()
