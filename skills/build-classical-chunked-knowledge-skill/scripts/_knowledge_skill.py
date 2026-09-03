"""Contracts for deterministic, standalone classical knowledge skills."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterator, Mapping, Sequence

from _classical_snapshot import (
    CONCEPT_LAYOUT_SOURCE_PACKED,
    STRUCTURED_SOURCE_KINDS,
    ClassicalSnapshot,
    load_snapshot,
)
from _context_projection import (
    SCHEMA_VERSION as CONTEXT_SCHEMA_VERSION,
    validate_projection,
)


SCHEMA_VERSION = "classical-chunked-knowledge-skill/1.0"
SKILL_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_GUIDANCE_HEADINGS = (
    "## Scope",
    "## Application workflow",
    "## Decision rules",
    "## Evidence and limits",
)
EXPECTED_ARTIFACT_PATHS = {
    "skill_md": "SKILL.md",
    "guidance": "references/guidance.md",
    "query_script": "scripts/query_expert_knowledge.py",
    "snapshot_runtime": "scripts/_classical_snapshot.py",
    "context_runtime": "scripts/_context_projection.py",
    "runtime_smoke": "scripts/runtime_smoke.py",
    "requirements": "scripts/requirements.txt",
    "agents_metadata": "agents/openai.yaml",
}


class KnowledgeSkillError(ValueError):
    """Describe an invalid input or generated classical knowledge skill."""


@dataclass(frozen=True)
class TreeBinding:
    """Bind every regular file below one directory."""

    sha256: str
    file_count: int


@dataclass(frozen=True)
class KnowledgeBinding:
    """Describe a deeply validated classical knowledge snapshot."""

    tree: TreeBinding
    record_count: int
    core_tree_sha256: str
    classical_index_sha256: str
    classical_plan_sha256: str


@dataclass(frozen=True)
class EvidenceLocation:
    """Resolve one logical record to a physical Markdown citation."""

    physical_path: str
    anchor: str | None

    @property
    def citation(self) -> str:
        """Return the knowledge-relative Markdown citation."""

        return self.physical_path + (f"#{self.anchor}" if self.anchor else "")


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically and reject non-finite values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest for bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def regular_files(root: Path) -> Iterator[Path]:
    """Yield regular files in stable order and reject links or special files."""

    if not root.is_dir() or root.is_symlink():
        raise KnowledgeSkillError(f"Directory is absent or unsafe: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise KnowledgeSkillError(f"Symlinks are not allowed: {path}")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise KnowledgeSkillError(f"Special files are not allowed: {path}")
    yield from sorted(files, key=lambda item: item.relative_to(root).as_posix())


def tree_binding(root: Path) -> TreeBinding:
    """Hash relative paths, lengths, and bytes for a complete directory."""

    digest = hashlib.sha256()
    count = 0
    for path in regular_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
        count += 1
    return TreeBinding(sha256=digest.hexdigest(), file_count=count)


def safe_relative_path(raw: str, *, label: str) -> PurePosixPath:
    """Validate one portable, knowledge-relative path."""

    candidate = PurePosixPath(raw)
    if (
        not raw
        or candidate.is_absolute()
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise KnowledgeSkillError(f"Unsafe {label}: {raw!r}")
    return candidate


def read_json_object(path: Path, *, label: str) -> dict[str, Any]:
    """Read a UTF-8 JSON object with a classified diagnostic."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KnowledgeSkillError(f"Invalid {label}: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeSkillError(f"{label} must be a JSON object: {path}")
    return payload


def read_records(root: Path) -> list[dict[str, Any]]:
    """Read the authoritative record ledger and reject malformed identities."""

    ledger = root / "semantic" / "records.jsonl"
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise KnowledgeSkillError(f"Cannot read authoritative ledger: {exc}") from exc
    rows: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise KnowledgeSkillError(
                f"Invalid authoritative ledger JSON on line {number}: {exc}"
            ) from exc
        if not isinstance(row, dict):
            raise KnowledgeSkillError(
                f"Authoritative ledger line {number} must be an object"
            )
        required = (
            "source_id",
            "record_id",
            "record_sha256",
            "concept_path",
            "source_kind",
            "body",
        )
        invalid = [key for key in required if not isinstance(row.get(key), str)]
        if invalid:
            raise KnowledgeSkillError(
                f"Authoritative ledger line {number} lacks string fields: "
                + ", ".join(invalid)
            )
        identity = (row["source_id"], row["record_id"])
        if identity in identities:
            raise KnowledgeSkillError(f"Duplicate authoritative identity: {identity!r}")
        identities.add(identity)
        if not HEX_64_RE.fullmatch(row["record_sha256"]):
            raise KnowledgeSkillError(
                f"Invalid record digest for authoritative identity: {identity!r}"
            )
        rows.append(row)
    if not rows:
        raise KnowledgeSkillError("Authoritative record ledger is empty")
    return rows


def concept_layout(root: Path) -> str:
    """Return the snapshot's declared physical concept layout."""

    report = read_json_object(
        root / "semantic" / "build-report.json",
        label="Semantic OKF build report",
    )
    processor = report.get("processor")
    if not isinstance(processor, Mapping):
        return "record-per-file-v1"
    value = processor.get("concept_layout", "record-per-file-v1")
    if not isinstance(value, str):
        raise KnowledgeSkillError("Semantic OKF concept layout must be a string")
    return value


def resolve_evidence_location(
    root: Path,
    record: Mapping[str, Any],
    *,
    layout: str,
    source_counts: Mapping[str, int],
    verify_body: bool = True,
) -> EvidenceLocation:
    """Resolve and verify one logical concept against its physical document."""

    concept_raw = record.get("concept_path")
    if not isinstance(concept_raw, str):
        raise KnowledgeSkillError("Record concept_path must be a string")
    logical = safe_relative_path(concept_raw, label="concept_path")
    if not logical.parts or logical.parts[0] != "concepts" or logical.suffix != ".md":
        raise KnowledgeSkillError(f"Concept path is outside concepts/: {concept_raw}")
    logical_file = root.joinpath(*logical.parts)
    anchor: str | None = None
    if logical_file.is_file() and not logical_file.is_symlink():
        physical = logical
    elif (
        layout == CONCEPT_LAYOUT_SOURCE_PACKED
        and record.get("source_kind") in STRUCTURED_SOURCE_KINDS
        and source_counts.get(str(record.get("source_id")), 0) > 1
    ):
        physical = safe_relative_path(
            f"concepts/{record.get('source_id')}.md",
            label="packed concept path",
        )
        anchor = f"record-{record.get('record_sha256', '')[:16]}"
    else:
        raise KnowledgeSkillError(f"Logical concept has no physical document: {concept_raw}")

    target = root.joinpath(*physical.parts)
    if not target.is_file() or target.is_symlink():
        raise KnowledgeSkillError(
            f"Physical concept is absent or unsafe: {physical.as_posix()}"
        )
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise KnowledgeSkillError(
            f"Physical concept escapes the knowledge root: {physical.as_posix()}"
        ) from exc

    if verify_body:
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise KnowledgeSkillError(
                f"Cannot read physical concept {physical.as_posix()}: {exc}"
            ) from exc
        body = record.get("body")
        if not isinstance(body, str) or body not in text:
            raise KnowledgeSkillError(
                f"Physical concept does not contain the exact record body: {concept_raw}"
            )
        if anchor is not None:
            marker = f'<a id="{anchor}"></a>'
            marker_offset = text.find(marker)
            if marker_offset < 0 or text.find(marker, marker_offset + len(marker)) >= 0:
                raise KnowledgeSkillError(
                    f"Packed concept lacks the exact record anchor or body: {concept_raw}"
                )
            body_offset = text.find(body, marker_offset + len(marker))
            next_marker = text.find('\n<a id="record-', marker_offset + len(marker))
            if body_offset < 0 or (next_marker >= 0 and body_offset >= next_marker):
                raise KnowledgeSkillError(
                    f"Packed concept body is not bound to its exact anchor: {concept_raw}"
                )
    return EvidenceLocation(physical_path=physical.as_posix(), anchor=anchor)


def validate_knowledge(root: Path, *, deep_validation: bool) -> KnowledgeBinding:
    """Validate classical retrieval and every authoritative citation binding."""

    root = root.resolve()
    try:
        snapshot: ClassicalSnapshot = load_snapshot(
            root,
            deep_validation=deep_validation,
        )
    except Exception as exc:
        raise KnowledgeSkillError(f"Classical knowledge validation failed: {exc}") from exc
    rows = read_records(root)
    layout = concept_layout(root)
    counts = Counter(str(row["source_id"]) for row in rows)
    for row in rows:
        resolve_evidence_location(
            root,
            row,
            layout=layout,
            source_counts=counts,
            verify_body=True,
        )
    if snapshot.index["core"]["record_count"] != len(rows):
        raise KnowledgeSkillError("Classical core record count differs from the ledger")
    return KnowledgeBinding(
        tree=tree_binding(root),
        record_count=len(rows),
        core_tree_sha256=snapshot.index["core"]["tree_sha256"],
        classical_index_sha256=snapshot.index_sha256,
        classical_plan_sha256=snapshot.index["classical_plan_sha256"],
    )


def validate_skill_name(name: str) -> None:
    """Validate a portable skill name and directory basename."""

    if not SKILL_NAME_RE.fullmatch(name):
        raise KnowledgeSkillError(
            "Skill name must use 1-64 lowercase letters, digits, or hyphens "
            "without leading or trailing hyphens"
        )


def normalize_text(path: Path, *, label: str) -> str:
    """Read UTF-8 text and normalize it to LF with one trailing newline."""

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise KnowledgeSkillError(f"Cannot read {label}: {path}: {exc}") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"


def validate_guidance(text: str) -> None:
    """Require structured, reviewable, placeholder-free application guidance."""

    if len(text.strip()) < 200:
        raise KnowledgeSkillError("Guidance must contain at least 200 characters")
    lowered = text.casefold()
    if "todo" in lowered or "[placeholder" in lowered:
        raise KnowledgeSkillError("Guidance contains a TODO or placeholder")
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    if len(headings) != 1:
        raise KnowledgeSkillError("Guidance must contain exactly one H1 heading")
    lines = set(text.splitlines())
    missing = [heading for heading in REQUIRED_GUIDANCE_HEADINGS if heading not in lines]
    if missing:
        raise KnowledgeSkillError(
            "Guidance lacks required headings: " + ", ".join(missing)
        )


def render_expert_skill(name: str, description: str) -> str:
    """Render token-bounded instructions for the generated read-only expert."""

    title = " ".join(part.capitalize() for part in name.split("-"))
    return f'''---
name: {name}
description: {json.dumps(description, ensure_ascii=False)}
---

# {title}

Answer from the embedded immutable classical Semantic OKF evidence. Use the
budgeted context projection so complete documents do not enter model context.

## Read-only boundary

- Use only this skill, its bundled knowledge, and the user's request.
- Do not browse when this snapshot is the requested authority.
- Never build, repair, refresh, cache, or modify this skill.
- Treat rankings and chunks as discovery; the exact ledger spans are evidence.

## Workflow

1. Read [guidance.md](references/guidance.md) for scope, decision rules,
   required perspectives, important negatives, and limits.
2. On first use or after transfer, verify all knowledge and chunk bindings:

   ```bash
   python -B scripts/query_expert_knowledge.py verify --deep-validation
   ```

3. Run one complete-question context selection. Its Markdown form minimizes
   provider-visible metadata while retaining exact citations:

   ```bash
   python -B scripts/query_expert_knowledge.py context \\
     --query "COMPLETE QUESTION" --mode fusion --format markdown
   ```

4. Choose `bm25` for exact identifiers or quoted terms, `association` for
   terminology mismatch, `topic` for themes, and `fusion` for synthesis or
   uncertain wording. Do not issue repeated searches when the first bundle's
   quality guard passes.
5. If `quality_guard.complete` is false, rerun once with the reported maximum
   budget. If only a boundary is missing, hydrate the named chunk and one
   linked neighbor instead:

   ```bash
   python -B scripts/query_expert_knowledge.py chunk \\
     --chunk-id CHUNK_ID --neighbors 1 --format markdown
   ```

6. Use full `search` or `get --show-content` only as a diagnostic fallback for
   unresolved evidence. They can emit complete passages or records.
7. Answer directly from the returned exact spans. Cite `evidence_path` and
   `evidence_anchor`, distinguish synthesis from direct statements, and state
   material limits or counterevidence.

## Evidence contract

- Every chunk binds an exact record-relative range and SHA-256 digest.
- `previous_chunk_id` and `next_chunk_id` restore local continuity without
  overlapping every chunk.
- `concept_path` is logical; `evidence_path` is an existing physical file;
  `evidence_anchor` identifies a record inside a packed collection.
- A compact bundle never proves that unselected evidence is absent.

## Completion gate

- Manifest, immutable knowledge, classical index, context projection, and
  physical evidence bindings passed.
- The context quality guard passed, or the bounded escalation was explicit.
- Every material claim maps to an exact returned range and citation.
- Required perspectives and important negatives were addressed.
- Unsupported claims and source limits are explicit.
- The complete skill tree remains unchanged.
'''


def render_openai_yaml(name: str, description: str) -> str:
    """Render portable UI metadata for the generated expert."""

    title = " ".join(part.capitalize() for part in name.split("-"))
    short = description.strip().split(".", 1)[0][:64].rstrip()
    if len(short) < 25:
        short = f"Consult the bundled {title} knowledge"[:64]
    prompt = (
        f"Use ${name} to answer this request from the bundled knowledge "
        "with exact local evidence."
    )
    return (
        "interface:\n"
        f"  display_name: {json.dumps(title, ensure_ascii=False)}\n"
        f"  short_description: {json.dumps(short, ensure_ascii=False)}\n"
        f"  default_prompt: {json.dumps(prompt, ensure_ascii=False)}\n"
    )


def artifact_binding(path: Path, relative: str) -> dict[str, Any]:
    """Return one deterministic artifact binding."""

    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def load_expert_manifest(skill_root: Path) -> dict[str, Any]:
    """Load one generated expert manifest."""

    return read_json_object(
        skill_root / "expert-manifest.json",
        label="classical knowledge skill manifest",
    )


def _validate_artifact_bindings(
    skill_root: Path,
    artifacts: Mapping[str, Any],
) -> None:
    if set(artifacts) != set(EXPECTED_ARTIFACT_PATHS):
        raise KnowledgeSkillError("Expert artifact binding set is not closed")
    for key, relative in EXPECTED_ARTIFACT_PATHS.items():
        binding = artifacts.get(key)
        if not isinstance(binding, dict) or set(binding) != {"path", "bytes", "sha256"}:
            raise KnowledgeSkillError(f"Invalid expert artifact binding: {key}")
        if binding.get("path") != relative:
            raise KnowledgeSkillError(f"Expert artifact path drift: {key}")
        path = skill_root.joinpath(*PurePosixPath(relative).parts)
        if not path.is_file() or path.is_symlink():
            raise KnowledgeSkillError(f"Expert artifact is absent or unsafe: {relative}")
        if binding.get("bytes") != path.stat().st_size:
            raise KnowledgeSkillError(f"Expert artifact byte-count drift: {key}")
        if binding.get("sha256") != sha256_file(path):
            raise KnowledgeSkillError(f"Expert artifact digest drift: {key}")


def validate_generated_skill(
    skill_root: Path,
    *,
    deep_validation: bool,
) -> dict[str, Any]:
    """Validate a generated skill, its knowledge, and all executable bindings."""

    skill_root = skill_root.expanduser()
    if skill_root.is_symlink():
        raise KnowledgeSkillError("Generated skill root cannot be a symlink")
    skill_root = skill_root.resolve()
    outside_bound_data = {
        path.relative_to(skill_root).as_posix()
        for path in regular_files(skill_root)
        if not (
            path.relative_to(skill_root).as_posix().startswith("references/knowledge/")
            or path.relative_to(skill_root).as_posix().startswith("references/context/")
        )
    }
    expected_outside_bound_data = {
        "expert-manifest.json",
        *EXPECTED_ARTIFACT_PATHS.values(),
    }
    if outside_bound_data != expected_outside_bound_data:
        missing = sorted(expected_outside_bound_data - outside_bound_data)
        unknown = sorted(outside_bound_data - expected_outside_bound_data)
        raise KnowledgeSkillError(
            f"Generated skill surface is not closed; missing={missing}, unknown={unknown}"
        )
    manifest = load_expert_manifest(skill_root)
    if set(manifest) != {
        "schema_version",
        "skill_name",
        "description",
        "generation",
        "knowledge",
        "context",
        "artifacts",
    }:
        raise KnowledgeSkillError("Classical knowledge skill manifest is not closed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise KnowledgeSkillError("Unsupported classical knowledge skill schema")
    name = manifest.get("skill_name")
    description = manifest.get("description")
    if not isinstance(name, str) or not isinstance(description, str) or not description.strip():
        raise KnowledgeSkillError("Expert manifest lacks a valid skill identity")
    validate_skill_name(name)
    if skill_root.name != name:
        raise KnowledgeSkillError(
            f"Skill directory {skill_root.name!r} does not match {name!r}"
        )
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise KnowledgeSkillError("Expert manifest lacks artifact bindings")
    _validate_artifact_bindings(skill_root, artifacts)

    actual_scripts = {
        path.relative_to(skill_root).as_posix()
        for path in (skill_root / "scripts").iterdir()
        if path.is_file()
    }
    expected_scripts = {
        relative
        for relative in EXPECTED_ARTIFACT_PATHS.values()
        if relative.startswith("scripts/")
    }
    if actual_scripts != expected_scripts:
        raise KnowledgeSkillError("Generated expert scripts are missing or unbound")

    skill_text = normalize_text(skill_root / "SKILL.md", label="generated SKILL.md")
    if not skill_text.startswith(f"---\nname: {name}\n"):
        raise KnowledgeSkillError("Generated SKILL.md name differs from the manifest")
    if (
        "## Read-only boundary" not in skill_text
        or "evidence_path" not in skill_text
        or "quality_guard.complete" not in skill_text
    ):
        raise KnowledgeSkillError("Generated SKILL.md lacks its read-only evidence contract")
    guidance = normalize_text(
        skill_root / "references" / "guidance.md",
        label="generated guidance",
    )
    validate_guidance(guidance)

    generation = manifest.get("generation")
    if not isinstance(generation, dict) or set(generation) != {
        "builder",
        "concept_layout",
        "default_query_mode",
        "source_manifest_sha256",
        "classical_plan_input_sha256",
        "context_plan_input_sha256",
        "deep_validation",
    }:
        raise KnowledgeSkillError("Expert generation binding is invalid")
    if generation.get("builder") != "build-classical-chunked-knowledge-skill":
        raise KnowledgeSkillError("Expert generator identity drift")
    if generation.get("default_query_mode") != "fusion":
        raise KnowledgeSkillError("Expert default query mode drift")
    if generation.get("deep_validation") is not True:
        raise KnowledgeSkillError("Expert was not built through deep validation")
    for key in (
        "source_manifest_sha256",
        "classical_plan_input_sha256",
        "context_plan_input_sha256",
    ):
        if not isinstance(generation.get(key), str) or not HEX_64_RE.fullmatch(generation[key]):
            raise KnowledgeSkillError(f"Invalid generation digest: {key}")

    knowledge = manifest.get("knowledge")
    if not isinstance(knowledge, dict) or set(knowledge) != {
        "format",
        "path",
        "tree",
        "record_count",
        "core_tree_sha256",
        "classical_index_sha256",
        "classical_plan_sha256",
    }:
        raise KnowledgeSkillError("Expert knowledge binding is invalid")
    if knowledge.get("format") != "semantic-okf-classical" or knowledge.get("path") != "references/knowledge":
        raise KnowledgeSkillError("Expert knowledge format or path drift")
    actual = validate_knowledge(
        skill_root / "references" / "knowledge",
        deep_validation=deep_validation,
    )
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict) or set(expected_tree) != {"sha256", "file_count"}:
        raise KnowledgeSkillError("Expert knowledge tree binding is invalid")
    comparisons: Sequence[tuple[str, Any, Any]] = (
        ("knowledge tree digest", expected_tree.get("sha256"), actual.tree.sha256),
        ("knowledge file count", expected_tree.get("file_count"), actual.tree.file_count),
        ("knowledge record count", knowledge.get("record_count"), actual.record_count),
        ("core tree digest", knowledge.get("core_tree_sha256"), actual.core_tree_sha256),
        (
            "classical index digest",
            knowledge.get("classical_index_sha256"),
            actual.classical_index_sha256,
        ),
        (
            "classical plan digest",
            knowledge.get("classical_plan_sha256"),
            actual.classical_plan_sha256,
        ),
    )
    for label, expected, observed in comparisons:
        if expected != observed:
            raise KnowledgeSkillError(f"Expert {label} drift")

    context = manifest.get("context")
    if not isinstance(context, dict) or set(context) != {
        "format",
        "path",
        "tree",
        "index_sha256",
        "plan_sha256",
        "chunk_count",
        "default_budget_tokens",
        "maximum_budget_tokens",
    }:
        raise KnowledgeSkillError("Expert context binding is invalid")
    if context.get("format") != CONTEXT_SCHEMA_VERSION or context.get("path") != "references/context":
        raise KnowledgeSkillError("Expert context format or path drift")
    context_root = skill_root / "references" / "context"
    expected_context_tree = context.get("tree")
    actual_context_tree = tree_binding(context_root)
    if not isinstance(expected_context_tree, dict) or set(expected_context_tree) != {
        "sha256",
        "file_count",
    }:
        raise KnowledgeSkillError("Expert context tree binding is invalid")
    if (
        expected_context_tree.get("sha256") != actual_context_tree.sha256
        or expected_context_tree.get("file_count") != actual_context_tree.file_count
    ):
        raise KnowledgeSkillError("Expert context tree drift")
    snapshot = load_snapshot(
        skill_root / "references" / "knowledge",
        deep_validation=False,
    )
    projection = validate_projection(
        skill_root / "references" / "knowledge",
        context_root,
        snapshot,
        rederive=deep_validation,
    )
    context_plan = projection.index["plan"]["selection"]
    context_comparisons: Sequence[tuple[str, Any, Any]] = (
        (
            "context index digest",
            context.get("index_sha256"),
            sha256_file(context_root / "index.json"),
        ),
        ("context plan digest", context.get("plan_sha256"), projection.index["plan_sha256"]),
        ("context chunk count", context.get("chunk_count"), len(projection.chunks)),
        (
            "default context budget",
            context.get("default_budget_tokens"),
            context_plan["default_budget_tokens"],
        ),
        (
            "maximum context budget",
            context.get("maximum_budget_tokens"),
            context_plan["maximum_budget_tokens"],
        ),
    )
    for label, expected, observed in context_comparisons:
        if expected != observed:
            raise KnowledgeSkillError(f"Expert {label} drift")
    if generation.get("concept_layout") != concept_layout(
        skill_root / "references" / "knowledge"
    ):
        raise KnowledgeSkillError("Expert concept-layout binding drift")
    return manifest
