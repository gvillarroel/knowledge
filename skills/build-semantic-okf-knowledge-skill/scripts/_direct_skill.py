"""Shared contracts for deterministic multi-family knowledge skills."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
from typing import Any, Iterator, Mapping

from _family_registry import FamilyProfile, profile


SCHEMA_VERSION = "semantic-okf-family-knowledge-skill/1.0"
SKILL_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
STRUCTURED_SOURCE_KINDS = {"csv", "json", "rdf"}
SOURCE_PACKED_LAYOUT = "source-packed-v1"
REQUIRED_GUIDANCE_HEADINGS = (
    "## Scope",
    "## Application workflow",
    "## Decision rules",
    "## Evidence and limits",
)


class DirectSkillError(ValueError):
    """Describe invalid direct-generation inputs or artifacts."""


@dataclass(frozen=True)
class TreeBinding:
    """Bind a complete file tree by SHA-256 and file count."""

    sha256: str
    file_count: int


def canonical_json(value: Any) -> str:
    """Serialize deterministic JSON and reject non-finite values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash one regular file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def regular_files(root: Path) -> Iterator[Path]:
    """Yield a sorted closed tree and reject links or special files."""

    if not root.is_dir() or root.is_symlink():
        raise DirectSkillError(f"Directory is absent or unsafe: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise DirectSkillError(f"Symlink is not allowed: {path}")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise DirectSkillError(f"Special file is not allowed: {path}")
    yield from sorted(files, key=lambda item: item.relative_to(root).as_posix())


def tree_binding(root: Path) -> TreeBinding:
    """Hash relative paths, byte lengths, and bytes for a complete tree."""

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
    return TreeBinding(digest.hexdigest(), count)


def safe_relative(raw: str, *, label: str) -> PurePosixPath:
    """Validate a portable relative path."""

    candidate = PurePosixPath(raw)
    if (
        not raw
        or candidate.is_absolute()
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise DirectSkillError(f"Unsafe {label}: {raw!r}")
    return candidate


def validate_skill_name(name: str) -> None:
    """Require the portable skill naming contract."""

    if not SKILL_NAME_RE.fullmatch(name):
        raise DirectSkillError(
            "Skill name must contain 1-64 lowercase letters, digits, or hyphens"
        )


def normalize_text(path: Path, *, label: str) -> str:
    """Read text strictly and normalize it to one LF-terminated value."""

    if not path.is_file() or path.is_symlink():
        raise DirectSkillError(f"{label} is absent or unsafe: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DirectSkillError(f"Cannot read {label}: {path}: {exc}") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"


def validate_guidance(text: str) -> None:
    """Require reviewed, structured, placeholder-free application guidance."""

    if len(text.strip()) < 200:
        raise DirectSkillError("Guidance must contain at least 200 characters")
    lowered = text.casefold()
    if "todo" in lowered or "[placeholder" in lowered:
        raise DirectSkillError("Guidance contains a TODO or placeholder")
    if len([line for line in text.splitlines() if line.startswith("# ")]) != 1:
        raise DirectSkillError("Guidance must contain exactly one H1 heading")
    lines = set(text.splitlines())
    missing = [heading for heading in REQUIRED_GUIDANCE_HEADINGS if heading not in lines]
    if missing:
        raise DirectSkillError(
            "Guidance lacks required headings: " + ", ".join(missing)
        )


def load_json(path: Path, *, label: str) -> dict[str, Any]:
    """Load one JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DirectSkillError(f"Invalid {label}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DirectSkillError(f"{label} must be a JSON object: {path}")
    return value


def load_records(knowledge: Path) -> list[dict[str, Any]]:
    """Load the authoritative ledger with exact identity checks."""

    ledger = knowledge / "semantic" / "records.jsonl"
    if not ledger.is_file() or ledger.is_symlink():
        raise DirectSkillError("Authoritative ledger is absent or unsafe")
    rows: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for line_number, raw in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            raise DirectSkillError(f"Blank ledger line: {line_number}")
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise DirectSkillError(f"Invalid ledger JSON at line {line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise DirectSkillError(f"Ledger row {line_number} is not an object")
        source_id, record_id = row.get("source_id"), row.get("record_id")
        if not isinstance(source_id, str) or not isinstance(record_id, str):
            raise DirectSkillError(f"Ledger row {line_number} lacks exact identity")
        identity = (source_id, record_id)
        if identity in identities:
            raise DirectSkillError(f"Duplicate ledger identity: {identity!r}")
        identities.add(identity)
        rows.append(row)
    if not rows:
        raise DirectSkillError("Authoritative ledger is empty")
    return rows


def concept_layout(knowledge: Path) -> str:
    """Return the declared physical concept layout."""

    report = load_json(
        knowledge / "semantic" / "build-report.json",
        label="Semantic OKF build report",
    )
    if report.get("status") != "pass":
        raise DirectSkillError("Semantic OKF build report is not passing")
    processor = report.get("processor")
    if not isinstance(processor, dict):
        raise DirectSkillError("Semantic OKF processor report is invalid")
    value = processor.get("concept_layout", "record-per-file-v1")
    if value not in {"record-per-file-v1", SOURCE_PACKED_LAYOUT}:
        raise DirectSkillError(f"Unsupported concept layout: {value!r}")
    return value


def evidence_location(
    knowledge: Path,
    record: Mapping[str, Any],
    *,
    layout: str,
    source_counts: Mapping[str, int],
) -> dict[str, Any]:
    """Resolve and verify one logical record against exact physical evidence."""

    logical_raw = record.get("concept_path")
    if not isinstance(logical_raw, str):
        raise DirectSkillError("Ledger record lacks concept_path")
    logical = safe_relative(logical_raw, label="logical concept path")
    logical_file = knowledge.joinpath(*logical.parts)
    anchor: str | None = None
    if logical_file.is_file() and not logical_file.is_symlink():
        physical = logical
    elif (
        layout == SOURCE_PACKED_LAYOUT
        and record.get("source_kind") in STRUCTURED_SOURCE_KINDS
        and source_counts.get(str(record.get("source_id")), 0) > 1
    ):
        physical = safe_relative(
            f"concepts/{record.get('source_id')}.md",
            label="packed concept path",
        )
        record_hash = record.get("record_sha256")
        if not isinstance(record_hash, str) or not HEX_64_RE.fullmatch(record_hash):
            raise DirectSkillError("Packed record has an invalid authoritative digest")
        anchor = f"record-{record_hash[:16]}"
    else:
        raise DirectSkillError(f"Logical concept has no physical document: {logical_raw}")

    target = knowledge.joinpath(*physical.parts)
    if not target.is_file() or target.is_symlink():
        raise DirectSkillError(f"Physical evidence is absent or unsafe: {physical}")
    try:
        target.resolve().relative_to(knowledge.resolve())
    except ValueError as exc:
        raise DirectSkillError(f"Physical evidence escapes knowledge: {physical}") from exc
    text = target.read_text(encoding="utf-8")
    body = record.get("body")
    if not isinstance(body, str) or body not in text:
        raise DirectSkillError(f"Physical evidence lacks exact body: {logical_raw}")
    if anchor is not None:
        marker = f'<a id="{anchor}"></a>'
        marker_offset = text.find(marker)
        if marker_offset < 0 or text.find(marker, marker_offset + len(marker)) >= 0:
            raise DirectSkillError(f"Packed evidence anchor is absent or duplicated: {anchor}")
        body_offset = text.find(body, marker_offset + len(marker))
        next_marker = text.find('\n<a id="record-', marker_offset + len(marker))
        if body_offset < 0 or (next_marker >= 0 and body_offset >= next_marker):
            raise DirectSkillError(f"Packed body is not bound to exact anchor: {anchor}")
    physical_raw = physical.as_posix()
    evidence_path = f"references/knowledge/{physical_raw}"
    return {
        "logical_concept_path": logical.as_posix(),
        "physical_concept_path": physical_raw,
        "evidence_path": evidence_path,
        "evidence_anchor": anchor,
        "citation": evidence_path + (f"#{anchor}" if anchor else ""),
    }


def validate_knowledge(knowledge: Path) -> tuple[TreeBinding, int, str]:
    """Validate every authoritative record-to-physical-evidence binding."""

    knowledge = knowledge.resolve()
    binding = tree_binding(knowledge)
    rows = load_records(knowledge)
    layout = concept_layout(knowledge)
    counts = Counter(str(row["source_id"]) for row in rows)
    for row in rows:
        evidence_location(knowledge, row, layout=layout, source_counts=counts)
    return binding, len(rows), layout


def copy_regular_tree(source: Path, target: Path) -> None:
    """Copy a closed tree without links, special files, or bytecode."""

    if target.exists() or target.is_symlink():
        raise DirectSkillError(f"Copy target already exists: {target}")
    target.mkdir(parents=True)
    for path in regular_files(source):
        if path.suffix == ".pyc" or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)


def artifact_binding(root: Path, path: Path) -> dict[str, Any]:
    """Return one exact generated artifact binding."""

    relative = path.relative_to(root).as_posix()
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def render_expert_skill(name: str, description: str, family: FamilyProfile) -> str:
    """Render the generated read-only expert instructions."""

    title = " ".join(part.capitalize() for part in name.split("-"))
    modes = ", ".join(f"`{mode}`" for mode in family.modes)
    return f'''---
name: {name}
description: {json.dumps(description, ensure_ascii=False)}
---

# {title}

Answer only from the embedded immutable {family.display_name} snapshot. Treat
retrieval and graph scores as discovery signals, never as domain facts.

## Read-only boundary

- Use only this skill, its embedded knowledge, and the user's request.
- Never build, repair, refresh, cache, download models, or modify this skill.
- Do not browse when the embedded snapshot is the requested authority.
- Stop or qualify the answer when exact bundled evidence is insufficient.

## Workflow

1. Read [guidance.md](references/guidance.md). For advanced native operations,
   read [the matched consultation skill](references/consultation/SKILL.md) and
   only the relevant file under `references/consultation/references/`.
2. On first use or after transfer, verify the complete expert:

   ```bash
   python -B scripts/query_expert_knowledge.py verify --deep-validation
   ```

3. Search with the complete question. The default mode is
   `{family.default_mode}`; available modes are {modes}:

   ```bash
   python -B scripts/query_expert_knowledge.py search \\
     --query "COMPLETE QUESTION" --mode {family.default_mode} --top-k 10
   ```

4. Run focused searches only for missing facets. Preserve distinct evidence
   identities and important counterevidence.
5. Hydrate an exact ledger record before relying on it:

   ```bash
   python -B scripts/query_expert_knowledge.py get \\
     --source-id SOURCE_ID --record-id RECORD_ID --show-content
   ```

6. Cite the returned `evidence_path` and `evidence_anchor`. Distinguish direct
   statements from synthesis and state material limits.

## Native consultation

The stable façade preserves the matched native result fields and adds physical
citations. The exact `{family.consult_skill}` scripts are under
`scripts/native/` for advanced operations described by the bundled consultation
references. Always pass `references/knowledge` as the snapshot, except Turso,
which uses `references/knowledge/semantic/knowledge.db`.

## Completion gate

- Manifest, artifact, knowledge-tree, family, and record bindings pass.
- Native family verification passes without changing knowledge bytes.
- Every material claim has an exact physical citation and ledger identity.
- Guidance requirements, negative evidence, and limitations are respected.
- No file in the complete generated skill has changed.
'''


def render_openai_yaml(name: str, description: str) -> str:
    """Render generated skill UI metadata."""

    title = " ".join(part.capitalize() for part in name.split("-"))
    short = description.strip().split(".", 1)[0][:64].rstrip()
    if len(short) < 25:
        short = f"Consult bundled {title} knowledge"[:64]
    prompt = f"Use ${name} to answer from the bundled knowledge with exact evidence."
    return (
        "interface:\n"
        f"  display_name: {json.dumps(title, ensure_ascii=False)}\n"
        f"  short_description: {json.dumps(short, ensure_ascii=False)}\n"
        f"  default_prompt: {json.dumps(prompt, ensure_ascii=False)}\n"
    )


def validate_generated_skill(skill_root: Path) -> dict[str, Any]:
    """Validate a generated family expert and its entire closed surface."""

    skill_root = skill_root.expanduser()
    if skill_root.is_symlink():
        raise DirectSkillError("Generated skill root cannot be a symlink")
    skill_root = skill_root.resolve()
    manifest = load_json(skill_root / "expert-manifest.json", label="expert manifest")
    if set(manifest) != {
        "schema_version",
        "skill_name",
        "description",
        "family",
        "generation",
        "knowledge",
        "artifacts",
    }:
        raise DirectSkillError("Generated expert manifest is not closed")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise DirectSkillError("Unsupported generated expert schema")
    name = manifest.get("skill_name")
    description = manifest.get("description")
    if not isinstance(name, str) or not isinstance(description, str) or not description:
        raise DirectSkillError("Generated expert identity is invalid")
    validate_skill_name(name)
    if skill_root.name != name:
        raise DirectSkillError("Generated skill directory/name binding drift")

    family_value = manifest.get("family")
    if not isinstance(family_value, dict) or not isinstance(family_value.get("id"), str):
        raise DirectSkillError("Generated family binding is invalid")
    expected_profile = profile(family_value["id"])
    if family_value != expected_profile.as_manifest():
        raise DirectSkillError("Generated family contract drift")

    generation = manifest.get("generation")
    if not isinstance(generation, dict) or set(generation) != {
        "builder",
        "concept_layout",
        "source_manifest_sha256",
        "plan_input_sha256",
        "deep_validation",
        "active_requirements",
    }:
        raise DirectSkillError("Generated construction binding is invalid")
    if generation.get("builder") != "build-semantic-okf-knowledge-skill":
        raise DirectSkillError("Generated builder identity drift")
    if generation.get("deep_validation") is not True:
        raise DirectSkillError("Generated expert lacks deep build validation")
    if generation.get("concept_layout") not in {
        "record-per-file-v1",
        SOURCE_PACKED_LAYOUT,
    }:
        raise DirectSkillError("Generated concept layout is invalid")
    if not isinstance(generation.get("source_manifest_sha256"), str) or not HEX_64_RE.fullmatch(
        generation["source_manifest_sha256"]
    ):
        raise DirectSkillError("Generated source-manifest digest is invalid")
    plan_hash = generation.get("plan_input_sha256")
    if expected_profile.uses_plan:
        if not isinstance(plan_hash, str) or not HEX_64_RE.fullmatch(plan_hash):
            raise DirectSkillError("Generated plan-input digest is invalid")
    elif plan_hash is not None:
        raise DirectSkillError("Planless generated family unexpectedly binds a plan")
    active_requirements = generation.get("active_requirements")
    if not isinstance(active_requirements, str):
        raise DirectSkillError("Generated active requirements binding is invalid")
    safe_relative(active_requirements, label="active requirements")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise DirectSkillError("Generated expert artifact bindings are invalid")
    expected_paths: set[str] = set()
    for index, binding in enumerate(artifacts):
        if not isinstance(binding, dict) or set(binding) != {"path", "bytes", "sha256"}:
            raise DirectSkillError(f"Invalid artifact binding at index {index}")
        raw = binding.get("path")
        if not isinstance(raw, str):
            raise DirectSkillError(f"Invalid artifact path at index {index}")
        relative = safe_relative(raw, label="artifact path")
        if raw.startswith("references/knowledge/") or raw == "expert-manifest.json":
            raise DirectSkillError(f"Reserved artifact binding: {raw}")
        if raw in expected_paths:
            raise DirectSkillError(f"Duplicate artifact binding: {raw}")
        expected_paths.add(raw)
        path = skill_root.joinpath(*relative.parts)
        if not path.is_file() or path.is_symlink():
            raise DirectSkillError(f"Bound artifact is absent or unsafe: {raw}")
        if binding.get("bytes") != path.stat().st_size:
            raise DirectSkillError(f"Artifact byte-count drift: {raw}")
        if binding.get("sha256") != sha256_file(path):
            raise DirectSkillError(f"Artifact digest drift: {raw}")
    actual_paths = {
        path.relative_to(skill_root).as_posix()
        for path in regular_files(skill_root)
        if not path.relative_to(skill_root).as_posix().startswith("references/knowledge/")
        and path.name != "expert-manifest.json"
    }
    if actual_paths != expected_paths:
        raise DirectSkillError(
            "Generated artifact surface is not closed; "
            f"missing={sorted(expected_paths - actual_paths)}, "
            f"unknown={sorted(actual_paths - expected_paths)}"
        )

    knowledge = manifest.get("knowledge")
    if not isinstance(knowledge, dict) or set(knowledge) != {
        "format",
        "path",
        "tree",
        "record_count",
        "build_report_sha256",
    }:
        raise DirectSkillError("Generated knowledge binding is invalid")
    if knowledge.get("format") != "semantic-okf" or knowledge.get("path") != "references/knowledge":
        raise DirectSkillError("Generated knowledge format/path drift")
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict) or set(expected_tree) != {"sha256", "file_count"}:
        raise DirectSkillError("Generated knowledge tree binding is invalid")
    knowledge_root = skill_root / "references" / "knowledge"
    binding, record_count, layout = validate_knowledge(knowledge_root)
    if expected_tree != {"sha256": binding.sha256, "file_count": binding.file_count}:
        raise DirectSkillError("Generated knowledge tree drift")
    if knowledge.get("record_count") != record_count:
        raise DirectSkillError("Generated knowledge record-count drift")
    report_hash = knowledge.get("build_report_sha256")
    if report_hash != sha256_file(knowledge_root / "semantic" / "build-report.json"):
        raise DirectSkillError("Generated build-report digest drift")
    if layout != generation.get("concept_layout"):
        raise DirectSkillError("Generated concept-layout binding drift")

    skill_text = normalize_text(skill_root / "SKILL.md", label="generated SKILL.md")
    if not skill_text.startswith(f"---\nname: {name}\n"):
        raise DirectSkillError("Generated SKILL.md identity drift")
    if "## Read-only boundary" not in skill_text or "evidence_path" not in skill_text:
        raise DirectSkillError("Generated SKILL.md lacks its evidence boundary")
    guidance = normalize_text(
        skill_root / "references" / "guidance.md",
        label="generated guidance",
    )
    validate_guidance(guidance)
    if active_requirements not in expected_paths:
        raise DirectSkillError("Active requirements are not artifact-bound")
    return manifest
