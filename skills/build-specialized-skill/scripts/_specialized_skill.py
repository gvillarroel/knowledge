"""Shared deterministic contracts for specialized expert skills."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterator

from _supervised_profile import (
    SupervisedProfileError,
    validate_profile_against_manifest,
)

SCHEMA_VERSION = "semantic-okf-expert-skill/1.0"
PROFILE_SCHEMA_VERSION = "semantic-okf-expert-skill/1.1"
SUPPORTED_SCHEMA_VERSIONS = (SCHEMA_VERSION, PROFILE_SCHEMA_VERSION)
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$|^[a-z0-9]$")
REQUIRED_GUIDANCE_HEADINGS = (
    "## Scope",
    "## Application workflow",
    "## Decision rules",
    "## Evidence and limits",
)
REQUIRED_KNOWLEDGE_FILES = (
    "index.md",
    "semantic/build-report.json",
    "semantic/records.jsonl",
)


class SpecializedSkillError(ValueError):
    """Raised when knowledge or a generated expert skill violates the contract."""


@dataclass(frozen=True)
class TreeBinding:
    """Bind one directory's complete regular-file content."""

    sha256: str
    file_count: int


@dataclass(frozen=True)
class KnowledgeBinding:
    """Describe the validated Semantic OKF input."""

    tree: TreeBinding
    record_count: int
    build_report_sha256: str


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def regular_files(root: Path) -> Iterator[Path]:
    """Yield regular files in stable POSIX-relative order and reject symlinks."""

    if not root.is_dir():
        raise SpecializedSkillError(f"Directory is absent: {root}")
    paths: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise SpecializedSkillError(f"Symlinks are not allowed: {path}")
        if path.is_file():
            paths.append(path)
    yield from sorted(paths, key=lambda item: item.relative_to(root).as_posix())


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


def _safe_relative_path(raw: str, *, label: str) -> PurePosixPath:
    candidate = PurePosixPath(raw)
    if (
        not raw
        or candidate.is_absolute()
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise SpecializedSkillError(f"Unsafe {label}: {raw!r}")
    return candidate


def _read_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SpecializedSkillError(f"Invalid {label}: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SpecializedSkillError(f"{label} must be a JSON object: {path}")
    return payload


def validate_knowledge(root: Path) -> KnowledgeBinding:
    """Validate the minimum immutable Semantic OKF read surface."""

    root = root.resolve()
    for relative in REQUIRED_KNOWLEDGE_FILES:
        path = root / PurePosixPath(relative)
        if not path.is_file():
            raise SpecializedSkillError(f"Required knowledge file is absent: {relative}")

    report_path = root / "semantic" / "build-report.json"
    report = _read_json_object(report_path, label="Semantic OKF build report")
    if report.get("status") != "pass" or report.get("valid") is not True:
        raise SpecializedSkillError(
            "Semantic OKF build report must have status 'pass' and valid true"
        )

    ledger_path = root / "semantic" / "records.jsonl"
    identities: set[tuple[str, str]] = set()
    concept_paths: set[str] = set()
    record_count = 0
    try:
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SpecializedSkillError(f"Cannot read record ledger: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SpecializedSkillError(
                f"Invalid ledger JSON on line {line_number}: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise SpecializedSkillError(
                f"Ledger line {line_number} must be a JSON object"
            )
        required = ("source_id", "record_id", "concept_path", "body")
        missing = [key for key in required if not isinstance(record.get(key), str)]
        if missing:
            raise SpecializedSkillError(
                f"Ledger line {line_number} lacks string fields: {', '.join(missing)}"
            )
        identity = (record["source_id"], record["record_id"])
        if identity in identities:
            raise SpecializedSkillError(f"Duplicate ledger identity: {identity!r}")
        identities.add(identity)
        concept_raw = record["concept_path"]
        concept = _safe_relative_path(concept_raw, label="concept_path")
        if concept.suffix != ".md":
            raise SpecializedSkillError(f"Concept path is not Markdown: {concept_raw}")
        if concept_raw in concept_paths:
            raise SpecializedSkillError(f"Duplicate concept path: {concept_raw}")
        concept_paths.add(concept_raw)
        target = root.joinpath(*concept.parts)
        if not target.is_file():
            raise SpecializedSkillError(f"Ledger concept is absent: {concept_raw}")
        try:
            target.resolve().relative_to(root)
        except ValueError as exc:
            raise SpecializedSkillError(
                f"Ledger concept escapes the knowledge root: {concept_raw}"
            ) from exc
        record_count += 1

    if record_count == 0:
        raise SpecializedSkillError("Semantic OKF record ledger is empty")
    summary = report.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("records"), int):
        if summary["records"] != record_count:
            raise SpecializedSkillError(
                "Build report record count does not match semantic/records.jsonl"
            )

    return KnowledgeBinding(
        tree=tree_binding(root),
        record_count=record_count,
        build_report_sha256=sha256_file(report_path),
    )


def validate_skill_name(name: str) -> None:
    """Validate a portable skill directory name."""

    if not SKILL_NAME_RE.fullmatch(name):
        raise SpecializedSkillError(
            "Skill name must be 1-64 lowercase letters, digits, or hyphens, "
            "without leading or trailing hyphens"
        )


def normalize_text(path: Path, *, label: str) -> str:
    """Read UTF-8 text and normalize it to LF with one trailing newline."""

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SpecializedSkillError(f"Cannot read {label}: {path}: {exc}") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"


def validate_guidance(text: str) -> None:
    """Require concise, structured, placeholder-free application guidance."""

    if len(text.strip()) < 200:
        raise SpecializedSkillError("Guidance must contain at least 200 characters")
    lowered = text.casefold()
    if "todo" in lowered or "[placeholder" in lowered:
        raise SpecializedSkillError("Guidance contains a TODO or placeholder")
    h1_count = sum(1 for line in text.splitlines() if line.startswith("# "))
    if h1_count != 1:
        raise SpecializedSkillError("Guidance must contain exactly one H1 heading")
    lines = set(text.splitlines())
    missing = [heading for heading in REQUIRED_GUIDANCE_HEADINGS if heading not in lines]
    if missing:
        raise SpecializedSkillError(
            f"Guidance lacks required headings: {', '.join(missing)}"
        )


def render_expert_skill(
    name: str,
    description: str,
    *,
    retrieval_profile: dict[str, Any] | None = None,
) -> str:
    """Render the generated expert's concise read-only instructions."""

    title = " ".join(part.capitalize() for part in name.split("-"))
    profile_section = ""
    if retrieval_profile is not None:
        development = retrieval_profile["development_evidence"]
        profile_section = f"""
## Retrospective retrieval profile

- The routing profile was derived from all
  `{development["question_count"]}` exposed questions and qrels in
  `{retrieval_profile["dataset_id"]}`.
- It is non-authoritative, in-sample evidence only and
  `promotion_eligible: false`.
- It contains terminology n-grams, not question-to-answer entries. Exact
  question lookup is forbidden.
- Treat only the embedded ledger and concept files as answer evidence. Do not
  claim behavior on unseen queries or an untouched holdout.
"""
    return f"""---
name: {name}
description: {json.dumps(description, ensure_ascii=False)}
---

# {title}

Apply the bundled knowledge using its reviewed domain guidance and exact local
evidence. This skill is a self-contained read-only expert artifact.

## Standalone boundary

- Use only this skill's files and the user's query.
- Treat `references/knowledge/` as immutable and authoritative.
- Do not use the web or unstated prior knowledge when the snapshot is the
  requested authority.
- Do not rebuild, repair, refresh, or modify the embedded knowledge.

## Workflow

1. Read [guidance.md](references/guidance.md) and translate the request into its
   domain-specific decision and evidence checklist.
2. Verify the artifact binding and discover candidate records:

   ```bash
   python scripts/query_expert_knowledge.py verify
   python scripts/query_expert_knowledge.py search --contains "QUERY TERMS"
   ```

3. Use exact `source_id`, `record_id`, and `concept_path` values from the results.
4. Open only the selected files below `references/knowledge/` and apply the
   guidance's decision rules.
5. Return the requested answer with exact bundled evidence paths. Label any
   inference and stop when the knowledge does not support a conclusion.

## Exact lookup

```bash
python scripts/query_expert_knowledge.py get \
  --source-id SOURCE_ID --record-id RECORD_ID --show-content
```

The helper verifies [expert-manifest.json](expert-manifest.json) before every
operation. It is local and read-only.
{profile_section}

## Completion gate

- The manifest and complete embedded knowledge tree passed verification.
- Every material claim is supported by an exact bundled concept path.
- The guidance's scope, decision rules, important negatives, and limits were
  applied.
- No file in this skill was changed.
"""


def render_openai_yaml(name: str, description: str) -> str:
    """Render portable interface metadata for the generated expert."""

    title = " ".join(part.capitalize() for part in name.split("-"))
    short = description.strip().split(".", 1)[0][:64].rstrip()
    if len(short) < 25:
        short = f"Apply bundled knowledge as the {title} expert"[:64]
    default_prompt = (
        f"Use ${name} to answer this request from the bundled knowledge "
        "with exact local evidence."
    )
    return (
        "interface:\n"
        f"  display_name: {json.dumps(title, ensure_ascii=False)}\n"
        f"  short_description: {json.dumps(short, ensure_ascii=False)}\n"
        f"  default_prompt: {json.dumps(default_prompt, ensure_ascii=False)}\n"
    )


def load_manifest(skill_root: Path) -> dict[str, Any]:
    """Load one generated expert manifest."""

    return _read_json_object(
        skill_root / "expert-manifest.json",
        label="expert manifest",
    )


def validate_generated_skill(skill_root: Path) -> dict[str, Any]:
    """Validate a complete generated expert skill and every bound artifact."""

    skill_root = skill_root.resolve()
    manifest = load_manifest(skill_root)
    schema_version = manifest.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise SpecializedSkillError("Unsupported expert manifest schema")
    name = manifest.get("skill_name")
    description = manifest.get("description")
    if not isinstance(name, str) or not isinstance(description, str):
        raise SpecializedSkillError("Expert manifest lacks skill identity")
    validate_skill_name(name)
    if skill_root.name != name:
        raise SpecializedSkillError(
            f"Skill directory {skill_root.name!r} does not match {name!r}"
        )

    expected_paths = {
        "skill_md": skill_root / "SKILL.md",
        "guidance": skill_root / "references" / "guidance.md",
        "query_script": skill_root / "scripts" / "query_expert_knowledge.py",
        "agents_metadata": skill_root / "agents" / "openai.yaml",
    }
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise SpecializedSkillError("Expert manifest lacks artifact bindings")
    for key, path in expected_paths.items():
        if not path.is_file():
            raise SpecializedSkillError(f"Generated expert artifact is absent: {key}")
        binding = artifacts.get(key)
        if not isinstance(binding, dict) or binding.get("sha256") != sha256_file(path):
            raise SpecializedSkillError(f"Generated expert artifact digest drift: {key}")

    query_support = artifacts.get("query_support", [])
    if not isinstance(query_support, list):
        raise SpecializedSkillError("Expert query_support binding must be an array")
    support_paths: set[str] = set()
    for index, binding in enumerate(query_support):
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise SpecializedSkillError(
                f"Invalid query_support binding at index {index}"
            )
        raw_path = binding.get("path")
        if not isinstance(raw_path, str):
            raise SpecializedSkillError(
                f"Invalid query_support path at index {index}"
            )
        relative = _safe_relative_path(raw_path, label="query_support path")
        if (
            len(relative.parts) != 2
            or relative.parts[0] != "scripts"
            or relative.name == "query_expert_knowledge.py"
        ):
            raise SpecializedSkillError(
                f"Query support must be a distinct direct scripts/ child: {raw_path}"
            )
        if raw_path in support_paths:
            raise SpecializedSkillError(
                f"Duplicate query_support path: {raw_path}"
            )
        support_paths.add(raw_path)
        path = skill_root.joinpath(*relative.parts)
        if not path.is_file() or path.is_symlink():
            raise SpecializedSkillError(
                f"Generated query support is absent or unsafe: {raw_path}"
            )
        if binding.get("sha256") != sha256_file(path):
            raise SpecializedSkillError(
                f"Generated query-support artifact digest drift: {raw_path}"
            )

    scripts_root = skill_root / "scripts"
    actual_support = {
        path.relative_to(skill_root).as_posix()
        for path in scripts_root.iterdir()
        if path.is_file() and path.name != "query_expert_knowledge.py"
    }
    if actual_support != support_paths:
        raise SpecializedSkillError(
            "Generated expert has missing or unbound query-support files"
        )

    skill_text = normalize_text(expected_paths["skill_md"], label="SKILL.md")
    if not skill_text.startswith(f"---\nname: {name}\n"):
        raise SpecializedSkillError("Generated SKILL.md name does not match manifest")
    if "## Standalone boundary" not in skill_text:
        raise SpecializedSkillError("Generated SKILL.md lacks standalone boundary")
    guidance = normalize_text(expected_paths["guidance"], label="guidance")
    validate_guidance(guidance)

    knowledge = manifest.get("knowledge")
    if not isinstance(knowledge, dict):
        raise SpecializedSkillError("Expert manifest lacks knowledge binding")
    knowledge_root = skill_root / "references" / "knowledge"
    actual_knowledge = validate_knowledge(knowledge_root)
    expected_tree = knowledge.get("tree")
    if not isinstance(expected_tree, dict):
        raise SpecializedSkillError("Expert manifest lacks knowledge tree binding")
    if expected_tree.get("sha256") != actual_knowledge.tree.sha256:
        raise SpecializedSkillError("Embedded knowledge tree digest drift")
    if expected_tree.get("file_count") != actual_knowledge.tree.file_count:
        raise SpecializedSkillError("Embedded knowledge file count drift")
    if knowledge.get("record_count") != actual_knowledge.record_count:
        raise SpecializedSkillError("Embedded knowledge record count drift")
    if knowledge.get("build_report_sha256") != actual_knowledge.build_report_sha256:
        raise SpecializedSkillError("Embedded build report digest drift")
    retrieval_profile = manifest.get("retrieval_profile")
    if schema_version == SCHEMA_VERSION:
        if retrieval_profile is not None:
            raise SpecializedSkillError(
                "Schema 1.0 expert must not declare a retrieval profile"
            )
    else:
        if not isinstance(retrieval_profile, dict):
            raise SpecializedSkillError(
                "Schema 1.1 expert lacks its retrieval-profile binding"
            )
        if support_paths != {"scripts/expert_routing_index.json"}:
            raise SpecializedSkillError(
                "Schema 1.1 expert must bind exactly one routing index"
            )
        profile_path = skill_root / "scripts" / "expert_routing_index.json"
        payload = _read_json_object(
            profile_path,
            label="supervised retrieval profile",
        )
        artifact = retrieval_profile.get("artifact")
        if (
            not isinstance(artifact, dict)
            or artifact.get("path") != "scripts/expert_routing_index.json"
            or artifact.get("sha256") != sha256_file(profile_path)
        ):
            raise SpecializedSkillError(
                "Retrieval-profile artifact binding drift"
            )
        try:
            validate_profile_against_manifest(
                payload,
                retrieval_profile,
                ledger_sha256=sha256_file(
                    knowledge_root / "semantic" / "records.jsonl"
                ),
                record_count=actual_knowledge.record_count,
            )
        except SupervisedProfileError as exc:
            raise SpecializedSkillError(str(exc)) from exc
    return manifest
