from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "skills" / "consult-semantic-okf-harbor-legacy"
EMBEDDINGS = ROOT / "skills" / "consult-semantic-okf-harbor-embeddings"
BASE_LEGACY = ROOT / "skills" / "consult-semantic-okf"
BASE_EMBEDDINGS = ROOT / "skills" / "consult-semantic-okf-embeddings"


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def legacy_module():
    return load_script("harbor_legacy_answer_test", LEGACY / "scripts" / "harbor_answer.py")


@pytest.fixture(scope="module")
def embeddings_module():
    return load_script("harbor_embeddings_answer_test", EMBEDDINGS / "scripts" / "harbor_answer.py")


def record(source_id: str, record_id: str, body: str) -> dict[str, object]:
    digest = hashlib.sha256(f"{source_id}\0{record_id}\0{body}".encode()).hexdigest()
    return {
        "source_id": source_id,
        "record_id": record_id,
        "concept_id": f"concepts/{source_id}/{record_id}",
        "concept_path": f"concepts/{source_id}/{record_id}.md",
        "concept_type": "Test Page",
        "source_path": f"sources/{record_id}.md",
        "record_sha256": digest,
        "title": record_id.replace("-", " ").title(),
        "attributes": {},
        "body": body,
    }


def write_legacy_bundle(tmp_path: Path) -> tuple[Path, list[dict[str, object]]]:
    bundle = tmp_path / "bundle"
    (bundle / "semantic").mkdir(parents=True)
    rows = [
        record(
            "source-actions",
            "actions",
            "Actions require authorization in every handler. An endpoint is public even when a form calls it.",
        ),
        record(
            "source-sessions",
            "sessions",
            "Sessions store user state. Validate the session before trusting membership or permissions.",
        ),
        record(
            "source-middleware",
            "middleware",
            "Middleware rewrites re-execute. Do not consume an HTML form body before a rewrite.",
        ),
    ]
    for row in rows:
        concept = bundle / str(row["concept_path"])
        concept.parent.mkdir(parents=True, exist_ok=True)
        concept.write_text(str(row["body"]), encoding="utf-8")
    (bundle / "semantic" / "build-report.json").write_text(
        json.dumps({"status": "pass", "valid": True}), encoding="utf-8"
    )
    (bundle / "semantic" / "records.jsonl").write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8"
    )
    return bundle, rows


def parameters(module, **changes):
    result = {
        "facet_limit": 8,
        "per_facet": 4,
        "max_supports": 16,
        "excerpt_chars": 160,
        "strategy": module.STRATEGY,
    }
    result.update(changes)
    return result


def valid_draft(pack: dict[str, object], support_ids: list[str]) -> dict[str, object]:
    return {
        "question_id": pack["question_id"],
        "question_sha256": pack["question_sha256"],
        "parameters": pack["parameters"],
        "support_pack_sha256": pack["support_pack_sha256"],
        "answer": {
            "summary": "Apply authorization, session, and rewrite boundaries together.",
            "claims": [
                {"statement": f"Grounded claim {index + 1}.", "evidence_indices": [index]}
                for index in range(len(support_ids))
            ],
        },
        "evidence": support_ids,
    }


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_packages_are_independent_and_preserve_original_search_scripts():
    assert "name: consult-semantic-okf-harbor-legacy" in (LEGACY / "SKILL.md").read_text()
    assert "name: consult-semantic-okf-harbor-embeddings" in (EMBEDDINGS / "SKILL.md").read_text()
    assert (LEGACY / "scripts" / "query_semantic_okf.py").read_bytes() == (
        BASE_LEGACY / "scripts" / "query_semantic_okf.py"
    ).read_bytes()
    for filename in ("query_semantic_okf_embeddings.py", "_embedding_snapshot.py"):
        assert (EMBEDDINGS / "scripts" / filename).read_bytes() == (
            BASE_EMBEDDINGS / "scripts" / filename
        ).read_bytes()
    assert "$consult-semantic-okf-harbor-legacy" in (LEGACY / "agents" / "openai.yaml").read_text()
    assert "$consult-semantic-okf-harbor-embeddings" in (
        EMBEDDINGS / "agents" / "openai.yaml"
    ).read_text()


def test_legacy_compiler_covers_facets_and_emits_ledger_bound_evidence(
    tmp_path: Path, legacy_module
):
    bundle, rows = write_legacy_bundle(tmp_path)
    before = tree_digest(bundle)
    question = (
        "Authorize an Action, validate the session, and avoid consuming an HTML form body "
        "during a middleware rewrite."
    )
    pack = legacy_module.build_support_pack(
        bundle, "q-hard", question, parameters(legacy_module)
    )
    assert before == tree_digest(bundle)
    assert len(pack["facets"]) <= 8
    assert any(facet["text"].casefold() == "validate the session" for facet in pack["facets"])
    support_ids = [support["support_id"] for support in pack["supports"]]
    assert len(support_ids) == len(set(support_ids)) == 3
    result = legacy_module.finalize(pack, valid_draft(pack, support_ids))
    assert list(result) == ["question_id", "answer", "evidence"]
    assert [list(row) for row in result["evidence"]] == [
        list(legacy_module.EVIDENCE_KEYS)
    ] * 3
    ledger = {(row["source_id"], row["record_id"]): row for row in rows}
    for evidence in result["evidence"]:
        source = ledger[(evidence["source_id"], evidence["record_id"])]
        assert evidence["locator"] == {"kind": "record", "target": "record.body"}
        assert evidence["record_sha256"] == source["record_sha256"]
        assert evidence["text_sha256"] == hashlib.sha256(str(source["body"]).encode()).hexdigest()
    assert before == tree_digest(bundle)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda draft: draft["parameters"].update({"max_supports": 2}), "parameters"),
        (lambda draft: draft["evidence"].append("support-unknown"), "unknown supports"),
        (
            lambda draft: draft["answer"]["claims"].__setitem__(
                slice(None), [{"statement": "Only first.", "evidence_indices": [0]}]
            ),
            "unused evidence",
        ),
    ],
)
def test_legacy_finalizer_closes_parameter_support_and_usage_drift(
    tmp_path: Path, legacy_module, mutate, message
):
    bundle, _ = write_legacy_bundle(tmp_path)
    pack = legacy_module.build_support_pack(
        bundle,
        "q-gate",
        "Compare action authorization and session validation.",
        parameters(legacy_module),
    )
    support_ids = [support["support_id"] for support in pack["supports"][:2]]
    draft = valid_draft(pack, support_ids)
    draft = json.loads(json.dumps(draft))
    mutate(draft)
    with pytest.raises(legacy_module.AnswerError, match=message):
        legacy_module.finalize(pack, draft)


def test_duplicate_json_keys_are_rejected(legacy_module):
    with pytest.raises(legacy_module.AnswerError, match="duplicate JSON key"):
        legacy_module._loads_json('{"question_id":"a","question_id":"b"}', "draft")


def test_finalizers_close_summary_and_claim_count_contracts(legacy_module, embeddings_module):
    for module in (legacy_module, embeddings_module):
        mode = {"mode": "auto"} if module is embeddings_module else {}
        pack = {
            "question_id": "q001",
            "question_sha256": "1" * 64,
            "parameters": parameters(module, **mode),
            "support_pack_sha256": "2" * 64,
            "supports": [
                {
                    "support_id": "support-one",
                    "source_id": "source",
                    "record_id": "record",
                    "concept_path": "concepts/source/record.md",
                    "source_path": "sources/record.md",
                    "record_sha256": "3" * 64,
                    "text_sha256": "4" * 64,
                }
            ],
        }
        draft = valid_draft(pack, ["support-one"])
        draft["answer"]["summary"] = "word " * 451
        with pytest.raises(module.AnswerError, match="at most 450 words"):
            module.finalize(pack, draft)
        draft = valid_draft(pack, ["support-one"])
        draft["answer"]["claims"] = [
            {"statement": f"Claim {index}.", "evidence_indices": [0]} for index in range(65)
        ]
        with pytest.raises(module.AnswerError, match="at most 64 items"):
            module.finalize(pack, draft)


def test_embeddings_compiler_uses_hybrid_hits_but_resolves_parent_records(
    monkeypatch: pytest.MonkeyPatch, embeddings_module
):
    long_body = "prefix " * 80 + "authorize action and preserve form body during rewrite" + " suffix" * 80
    action = record("source-actions", "actions", long_body)
    session = record("source-sessions", "sessions", "validate session membership before permissions")
    snapshot = SimpleNamespace(
        records={action["concept_id"]: action, session["concept_id"]: session}
    )
    calls: list[tuple[str, str, int]] = []

    def fake_search(_snapshot, query, *, requested_mode, top_k, **_kwargs):
        calls.append((query, requested_mode, top_k))
        chosen = session if "session" in query.casefold() else action
        start = str(chosen["body"]).find("authorize")
        if start < 0:
            start = 0
        return {
            "requested_mode": requested_mode,
            "effective_mode": "hybrid",
            "hits": [
                {
                    "concept_id": chosen["concept_id"],
                    "chunk_id": "chunk-" + str(chosen["record_id"]),
                    "locator": {
                        "kind": "character-range",
                        "start": start,
                        "end": min(len(str(chosen["body"])), start + 32),
                    },
                    "scores": {"hybrid": 0.5, "vector": 0.7, "lexical": 3.0},
                }
            ],
        }

    monkeypatch.setattr(embeddings_module, "load_snapshot", lambda _bundle: snapshot)
    monkeypatch.setattr(embeddings_module, "search_snapshot", fake_search)
    params = parameters(embeddings_module, mode="auto")
    pack = embeddings_module.build_support_pack(
        Path("unused"),
        "q-vector",
        "Authorize the action and validate the session.",
        params,
    )
    assert calls and all(mode == "auto" and top_k == 4 for _, mode, top_k in calls)
    assert {support["record_id"] for support in pack["supports"]} == {"actions", "sessions"}
    assert all(support["effective_mode"] == "hybrid" for support in pack["supports"])
    assert all(len(support["excerpt"]) <= 160 for support in pack["supports"])
    support_ids = [support["support_id"] for support in pack["supports"]]
    result = embeddings_module.finalize(pack, valid_draft(pack, support_ids))
    assert result["evidence"][0]["locator"] == {"kind": "record", "target": "record.body"}
    assert result["evidence"][0]["text_sha256"] in {
        hashlib.sha256(str(action["body"]).encode()).hexdigest(),
        hashlib.sha256(str(session["body"]).encode()).hexdigest(),
    }


def test_embeddings_pack_rejects_provider_and_snapshot_failures(
    monkeypatch: pytest.MonkeyPatch, embeddings_module
):
    monkeypatch.setattr(
        embeddings_module,
        "load_snapshot",
        lambda _bundle: (_ for _ in ()).throw(embeddings_module.SnapshotError("stale digest")),
    )
    with pytest.raises(embeddings_module.AnswerError, match="stale digest"):
        embeddings_module.build_support_pack(
            Path("unused"),
            "q-fail",
            "Find evidence.",
            parameters(embeddings_module, mode="auto"),
        )
