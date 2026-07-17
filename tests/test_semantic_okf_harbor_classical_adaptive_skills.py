from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


REPO = Path(__file__).resolve().parents[1]
FAMILIES = ("classical", "adaptive")


def load_compiler(family: str) -> ModuleType:
    scripts = REPO / f"skills/consult-semantic-okf-harbor-{family}/scripts"
    module_name = f"semantic_okf_harbor_{family}_answer"
    spec = importlib.util.spec_from_file_location(module_name, scripts / "harbor_answer.py")
    assert spec and spec.loader
    sys.path.insert(0, str(scripts))
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(scripts))
    return module


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_fixture(tmp_path: Path, module: ModuleType):
    rows = []
    for number, (record_id, source_path) in enumerate(
        (
            ("alpha", "sources/mdx/guides/alpha.mdx"),
            ("beta", "sources/mdx/guides/beta.mdx"),
            ("alpha-detail", "sources/mdx/reference/alpha-detail.mdx"),
            ("beta-error", "sources/mdx/reference/errors/beta-error.mdx"),
            ("gamma", "sources/mdx/guides/gamma.mdx"),
        ),
        start=1,
    ):
        body = (
            f"# Record {record_id}\n\n"
            f"This authoritative parent explains {record_id} and its safe condition.\n\n"
            f"The mechanism for {record_id} has an explicit exclusion and boundary."
        )
        rows.append(
            {
                "source_id": f"source-{number}",
                "record_id": record_id,
                "record_sha256": hashlib.sha256(f"record-{number}".encode()).hexdigest(),
                "concept_path": f"concepts/source-{number}/{record_id}.md",
                "source_path": source_path,
                "body": body,
            }
        )
    semantic = tmp_path / "semantic"
    semantic.mkdir()
    (semantic / "records.jsonl").write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    snapshot = SimpleNamespace(
        root=tmp_path,
        index={"core": {"tree_sha256": "a" * 64}},
        index_sha256="b" * 64,
    )
    by_id = {row["record_id"]: row for row in rows}
    question = "Alpha mechanism, beta condition, and gamma."
    facets = module.derive_facets(question, 8)
    assert facets == ["Alpha mechanism", "beta condition", "gamma"]
    routes = {
        question: ["alpha", "beta"],
        facets[0]: ["alpha", "alpha-detail"],
        facets[1]: ["beta", "beta-error"],
        facets[2]: ["beta-error", "gamma"],
    }

    def result(record_id: str, rank: int):
        row = by_id[record_id]
        body = row["body"]
        if record_id == "alpha-detail":
            start = body.index("authoritative")
            end = body.index(".\n", start)
            locator = {"kind": "character-range", "start": start, "end": end}
            text = body[start:end]
        else:
            locator = {"kind": "record"}
            text = body
        return {
            "rank": rank,
            "source_id": row["source_id"],
            "record_id": row["record_id"],
            "record_sha256": row["record_sha256"],
            "concept_path": row["concept_path"],
            "source_path": row["source_path"],
            "locator": locator,
            "text": text,
            "text_sha256": sha256_text(text),
        }

    calls = []

    def search(_snapshot, query, mode, top_k):
        calls.append((query, mode, top_k))
        record_ids = routes[query][:top_k]
        return {
            "status": "pass",
            "effective_mode": module.RETRIEVAL_MODE,
            "results": [result(record_id, rank) for rank, record_id in enumerate(record_ids, 1)],
        }

    retrieval = {
        "mode": module.RETRIEVAL_MODE,
        "full_top_k": 4,
        "per_facet_top_k": 3,
        "max_facets": 8,
        "max_supports": 5,
        "protected_full": 1,
        "snippet_chars": 300,
        "snippets_per_support": 1,
    }
    return snapshot, question, search, retrieval, calls, by_id


@pytest.mark.parametrize("family", FAMILIES)
def test_bounded_facet_union_projects_parent_records_and_deduplicates(
    tmp_path: Path, family: str
) -> None:
    module = load_compiler(family)
    snapshot, question, search, retrieval, calls, by_id = build_fixture(tmp_path, module)
    pack = module.build_pack(
        snapshot,
        question_id="q031",
        question=question,
        retrieval=retrieval,
        search=search,
    )

    assert [call[0] for call in calls] == [question, *pack["facets"]]
    assert {call[1] for call in calls} == {module.RETRIEVAL_MODE}
    assert len(pack["supports"]) == 5
    identities = [(row["source_id"], row["record_id"]) for row in pack["supports"]]
    assert len(identities) == len(set(identities))
    assert {row["record_id"] for row in pack["supports"]} == set(by_id)
    support_order = [row["record_id"] for row in pack["supports"]]
    assert support_order.index("gamma") < support_order.index("beta-error")

    projected = next(row for row in pack["supports"] if row["record_id"] == "alpha-detail")
    assert projected["locator"] == {"kind": "record"}
    assert projected["text_sha256"] == sha256_text(by_id["alpha-detail"]["body"])
    assert len(projected["snippets"]) == 1
    assert len(projected["snippets"][0]["text"]) <= 460
    assert projected["snippets"][0]["text_sha256"] == sha256_text(
        projected["snippets"][0]["text"]
    )


@pytest.mark.parametrize("family", FAMILIES)
def test_finalizer_rederives_pack_and_emits_only_first_use_evidence(
    tmp_path: Path, family: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_compiler(family)
    snapshot, question, search, retrieval, _calls, _by_id = build_fixture(tmp_path, module)
    pack = module.build_pack(
        snapshot,
        question_id="q031",
        question=question,
        retrieval=retrieval,
        search=search,
    )
    monkeypatch.setattr(module, "search_snapshot", search)
    supplied = module._validate_pack_shape(pack)
    assert module._rederive_pack(snapshot, supplied) == pack

    by_record = {row["record_id"]: row["support_id"] for row in pack["supports"]}
    draft = {
        "question_id": "q031",
        "parameters_sha256": pack["parameters_sha256"],
        "summary": "The three selected records establish an explicit mechanism, condition, and exclusion.",
        "claims": [
            {"statement": "Gamma has an explicit exclusion.", "support_ids": [by_record["gamma"]]},
            {
                "statement": "Alpha and beta establish the joined mechanism and condition.",
                "support_ids": [by_record["alpha"], by_record["beta"]],
            },
        ],
    }
    answer = module.compile_answer(pack, draft)

    assert list(answer) == ["question_id", "answer", "evidence"]
    assert [row["record_id"] for row in answer["evidence"]] == ["gamma", "alpha", "beta"]
    assert [row["evidence_indices"] for row in answer["answer"]["claims"]] == [[0], [1, 2]]
    assert all(list(row) == module.EVIDENCE_KEYS for row in answer["evidence"])
    assert len(answer["evidence"]) < len(pack["supports"])

    tampered = copy.deepcopy(pack)
    tampered["supports"][0]["snippets"][0]["text"] += " tampered"
    with pytest.raises(module.SnapshotError, match="tampered"):
        module._rederive_pack(snapshot, module._validate_pack_shape(tampered))


@pytest.mark.parametrize("family", FAMILIES)
def test_compiler_rejects_duplicate_keys_unknown_supports_and_parameter_mismatch(
    tmp_path: Path, family: str
) -> None:
    module = load_compiler(family)
    snapshot, question, search, retrieval, _calls, _by_id = build_fixture(tmp_path, module)
    pack = module.build_pack(
        snapshot,
        question_id="q031",
        question=question,
        retrieval=retrieval,
        search=search,
    )
    with pytest.raises(module.SnapshotError, match="duplicate JSON key"):
        module.strict_json('{"question_id":"q031","question_id":"q032"}', label="draft")

    draft = {
        "question_id": "q031",
        "parameters_sha256": pack["parameters_sha256"],
        "summary": "A supported answer.",
        "claims": [{"statement": "A claim.", "support_ids": ["support-unknown"]}],
    }
    with pytest.raises(module.SnapshotError, match="unknown support"):
        module.compile_answer(pack, draft)
    draft["parameters_sha256"] = "0" * 64
    with pytest.raises(module.SnapshotError, match="parameter mismatch"):
        module.compile_answer(pack, draft)

    support_id = pack["supports"][0]["support_id"]
    bounded = {
        "question_id": "q031",
        "parameters_sha256": pack["parameters_sha256"],
        "summary": "word " * 451,
        "claims": [{"statement": "A claim.", "support_ids": [support_id]}],
    }
    with pytest.raises(module.SnapshotError, match="1 through 450 words"):
        module.compile_answer(pack, bounded)
    bounded["summary"] = "A bounded summary."
    bounded["claims"] = [
        {"statement": f"Claim {index}.", "support_ids": [support_id]} for index in range(65)
    ]
    with pytest.raises(module.SnapshotError, match="1 through 64 claims"):
        module.compile_answer(pack, bounded)


@pytest.mark.parametrize("family", FAMILIES)
def test_evolved_packages_keep_family_retrieval_byte_identical_and_standalone(family: str) -> None:
    original = REPO / f"skills/consult-semantic-okf-{family}"
    evolved = REPO / f"skills/consult-semantic-okf-harbor-{family}"
    family_module = f"_{family}_snapshot.py"
    query_script = f"query_semantic_okf_{family}.py"
    for relative in (
        f"scripts/{family_module}",
        f"scripts/{query_script}",
        "scripts/runtime_smoke.py",
        "scripts/requirements.in",
        "scripts/requirements.txt",
    ):
        assert (evolved / relative).read_bytes() == (original / relative).read_bytes()

    compiler = (evolved / "scripts/harbor_answer.py").read_text(encoding="utf-8")
    skill = (evolved / "SKILL.md").read_text(encoding="utf-8")
    metadata = (evolved / "agents/openai.yaml").read_text(encoding="utf-8")
    assert f"name: consult-semantic-okf-harbor-{family}" in skill
    assert f"$consult-semantic-okf-harbor-{family}" in metadata
    assert "evaluations/" not in compiler
    assert "skills/consult-semantic-okf" not in compiler
    assert "write_text(" not in compiler
    assert "open(\"w" not in compiler
