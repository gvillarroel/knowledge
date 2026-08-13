#!/usr/bin/env python3
"""Freeze and generate the eight-family single-folder builder token study."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REGISTRY = HERE / "families.json"
INPUT_ROOT = HERE / "generated/inputs/graphrag-papers-40"
SKILLS_ROOT = REPO / "skills"
SCORER = HERE / "builder_token_score.py"
HARBOR_SOURCE_ROOT = (
    HERE
    / "generated/campaigns/20260723-papers-consult-gpt53-spark-05"
    / "frozen/repo/vendor"
)
DEFAULT_OUTPUT = (
    REPO
    / "evaluations"
    / "semantic-okf-token-efficiency-study-v7"
    / "private"
    / "frozen"
)
RUNTIME_IMAGE = (
    "semantic-okf-harbor-runtime:"
    "sha256-bcd2b2b57b968ff8b4976bedf8c5ddf7b7e2ff41c341f7a13a05ae4df2ffc9d8"
)
RUNTIME_IMAGE_ID = (
    "sha256:bcd2b2b57b968ff8b4976bedf8c5ddf7b7e2ff41c341f7a13a05ae4df2ffc9d8"
)
MODEL = "openai-codex/gpt-5.3-codex-spark"
PI_VERSION = "0.73.1"
THINKING = "high"
HARBOR_VERSION = "0.18.0"
EXPECTED_RECORDS_SHA256 = (
    "df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc"
)
EXPECTED_RECORDS_COUNT = 874
REPLICATES = {
    "replicate-a": ("/workspace/knowledge",),
    "replicate-b": ("/workspace/release",),
}
FAMILY_SENTINELS = {
    "adaptive": "adaptive/index.json",
    "classical": "classical/index.json",
    "embeddings": "retrieval/embeddings.jsonl",
    "ensemble": "ensemble/index.json",
    "entity-graph": "entity-graph/index.json",
    "graphify": "retrieval/graphify/index.json",
    "legacy": "semantic/data.ttl",
    "turso": "semantic/knowledge.db",
}


class StudyPreparationError(ValueError):
    """Raised when the frozen builder study cannot be reproduced safely."""


def canonical_json(value: Any) -> str:
    """Render deterministic human-readable JSON."""

    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path, *, exclude: set[str] | None = None) -> str:
    """Hash paths and file bytes with cross-platform POSIX byte ordering."""

    if not root.is_dir():
        raise StudyPreparationError(f"tree does not exist: {root}")
    excluded = exclude or set()
    entries = [
        path
        for path in root.rglob("*")
        if path.relative_to(root).as_posix() not in excluded
    ]
    entries.sort(
        key=lambda path: path.relative_to(root).as_posix().encode("utf-8")
    )
    digest = hashlib.sha256()
    for path in entries:
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise StudyPreparationError(f"symbolic link is forbidden: {path}")
        digest.update(("D:" if path.is_dir() else "F:").encode())
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        if path.is_file():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StudyPreparationError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise StudyPreparationError(f"expected a JSON object: {path}")
    return value


def registered_families() -> dict[str, dict[str, Any]]:
    """Load and validate the exact eight-family registry."""

    value = load_object(REGISTRY)
    families = value.get("families")
    if not isinstance(families, dict) or set(families) != set(FAMILY_SENTINELS):
        raise StudyPreparationError(
            "family registry does not contain the expected eight strategies"
        )
    result: dict[str, dict[str, Any]] = {}
    for family_id, family in families.items():
        if not isinstance(family, dict):
            raise StudyPreparationError(f"invalid family entry: {family_id}")
        result[family_id] = family
    return result


def replace_output(arguments: Sequence[object], output: str) -> list[str]:
    """Replace the canonical output argument in a staged command."""

    result = []
    replacements = 0
    for argument in arguments:
        if not isinstance(argument, str):
            raise StudyPreparationError("agent command arguments must be strings")
        if argument == "/workspace/knowledge":
            result.append(output)
            replacements += 1
        else:
            result.append(argument)
    if replacements != 1:
        raise StudyPreparationError(
            "agent command must contain one canonical output argument"
        )
    return result


def shell_words(values: Sequence[str]) -> str:
    """Render the controlled absolute-path command arguments."""

    for value in values:
        if any(character.isspace() for character in value):
            raise StudyPreparationError(
                f"unexpected whitespace in controlled argument: {value!r}"
            )
    return " ".join(values)


def instruction(
    *,
    family_id: str,
    build_skill: str,
    build_script: str,
    validate_script: str,
    build_arguments: Sequence[object],
    validate_arguments: Sequence[object],
    outputs: tuple[str],
) -> str:
    """Render one bounded single-folder builder instruction."""

    command_rows: list[str] = []
    for output in outputs:
        build = replace_output(build_arguments, output)
        validate = replace_output(validate_arguments, output)
        command_rows.extend(
            [
                (
                    f'python "$HOME/.agents/skills/{build_skill}/scripts/'
                    f'{build_script}" {shell_words(build)}'
                ),
                (
                    f'python "$HOME/.agents/skills/{build_skill}/scripts/'
                    f'{validate_script}" {shell_words(validate)}'
                ),
            ]
        )
    numbered = "\n".join(
        f"{index}. `{command}`"
        for index, command in enumerate(command_rows, start=1)
    )
    output = outputs[0]
    return f"""Use only the installed `{build_skill}` skill and the immutable
raw input mounted read-only at `/dataset` to build and independently validate
one `{family_id}` Semantic OKF knowledge folder.

Run these commands exactly once and in this order:

{numbered}

The destination `{output}` is initially absent and must remain an atomic
no-replace publication. Set any Bash tool timeout to 3600 seconds. Never retry
either command: if one fails or times out, stop and report the failure. Do not
consult the folder, answer a knowledge question, download anything, install
dependencies, modify `/dataset`, or remove the completed destination. Return
one concise JSON object containing only `status` and `outputs`.
"""


def task_toml(family_id: str, replicate: str) -> str:
    """Render the common Harbor task contract."""

    return f"""schema_version = "1.3"
artifacts = [{{ source = "/logs/agent/pi.txt", destination = "pi.jsonl" }}]

[task]
name = "knowledge/graphrag-papers-40__builder-token__{family_id}__{replicate}"
description = "Direct single-folder token measurement for the {family_id} builder."
keywords = ["semantic-okf", "graphrag-papers-40", "builder-token", "{family_id}", "development"]

[metadata]
difficulty = "hard"
category = "knowledge-evaluation"
dataset_id = "graphrag-papers-40"
family = "{family_id}"
mode = "builder-token"
cohort = "development"
replicate = "{replicate}"

[agent]
timeout_sec = 7200.0
network_mode = "public"

[verifier]
timeout_sec = 600.0
environment_mode = "shared"
network_mode = "public"

[environment]
docker_image = "{RUNTIME_IMAGE}"
os = "linux"
network_mode = "public"
memory_mb = 8192
storage_mb = 24576
workdir = "/workspace"
"""


def copy_checked_tree(source: Path, destination: Path) -> None:
    """Copy a regular-file tree while rejecting links and special files."""

    if not source.is_dir():
        raise StudyPreparationError(f"source tree does not exist: {source}")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise StudyPreparationError(f"symbolic link is forbidden: {path}")
        if not (path.is_dir() or path.is_file()):
            raise StudyPreparationError(f"special file is forbidden: {path}")
    shutil.copytree(source, destination)


def freeze_patched_harbor(output: Path) -> dict[str, str]:
    """Freeze Harbor and repair its Pi version check without changing runtime."""

    source_package = HARBOR_SOURCE_ROOT / "harbor"
    source_entrypoint = HARBOR_SOURCE_ROOT / "harbor-cli"
    destination_root = output / "harbor"
    destination_package = destination_root / "harbor"
    destination_entrypoint = destination_root / "harbor-cli"
    if not source_package.is_dir():
        raise StudyPreparationError(
            f"Harbor source tree does not exist: {source_package}"
        )
    shutil.copytree(
        source_package,
        destination_package,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    destination_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_entrypoint, destination_entrypoint)
    adapter = destination_package / "agents/installed/pi.py"
    source_tree_sha256 = tree_digest(destination_package)
    before = adapter.read_text(encoding="utf-8")
    old = 'test "$(pi --version | tail -n 1)" = "0.73.1"; '
    new = (
        "grep -Fq \\'\"version\": \"0.73.1\"\\' "
        "/opt/semantic-okf/pi-coding-agent/node_modules/"
        "@mariozechner/pi-coding-agent/package.json; "
    )
    if before.count(old) != 1:
        raise StudyPreparationError(
            "frozen Harbor Pi version-check patch context drift"
        )
    patched = before.replace(old, new)
    old_final = '"node --version; pi --version"'
    if patched.count(old_final) != 1:
        raise StudyPreparationError(
            "frozen Harbor Pi diagnostic patch context drift"
        )
    patched = patched.replace(old_final, '"node --version"')
    try:
        compile(patched, str(adapter), "exec")
    except SyntaxError as exc:
        raise StudyPreparationError(
            "patched Harbor Pi adapter is not valid Python"
        ) from exc
    adapter.write_text(
        patched,
        encoding="utf-8",
        newline="\n",
    )
    return {
        "version": HARBOR_VERSION,
        "source_tree_sha256": source_tree_sha256,
        "source_entrypoint_sha256": sha256_file(source_entrypoint),
        "patched_tree_sha256": tree_digest(destination_package),
        "patched_entrypoint_sha256": sha256_file(destination_entrypoint),
        "patched_adapter_sha256": sha256_file(adapter),
        "patch": "pi-version-package-metadata-no-cli-v3",
    }


def task_files(
    *,
    family_id: str,
    family: Mapping[str, Any],
    input_manifest: Mapping[str, Any],
    replicate: str,
    outputs: tuple[str],
) -> dict[str, bytes]:
    """Return every file in one generated task."""

    agent_build = input_manifest.get("agent_build")
    agent_validate = input_manifest.get("agent_validate")
    if not isinstance(agent_build, Mapping) or not isinstance(
        agent_validate, Mapping
    ):
        raise StudyPreparationError(
            f"{family_id} input manifest lacks agent commands"
        )
    build_skill = family.get("build_skill")
    build_script = family.get("build_script")
    validate_script = family.get("validate_script")
    if (
        agent_build.get("skill") != build_skill
        or agent_validate.get("skill") != build_skill
        or agent_build.get("script") != build_script
        or agent_validate.get("script") != validate_script
    ):
        raise StudyPreparationError(
            f"{family_id} registry and staged command bindings disagree"
        )
    build_arguments = agent_build.get("arguments")
    validate_arguments = agent_validate.get("arguments")
    if not isinstance(build_arguments, list) or not isinstance(
        validate_arguments, list
    ):
        raise StudyPreparationError(
            f"{family_id} agent command arguments are invalid"
        )
    config = {
        "schema_version": "semantic-okf-builder-token-task/3.0",
        "family": family_id,
        "replicate": replicate,
        "outputs": list(outputs),
        "build_script": build_script,
        "validate_script": validate_script,
        "family_sentinel": FAMILY_SENTINELS[family_id],
        "expected_records_sha256": EXPECTED_RECORDS_SHA256,
        "expected_records_count": EXPECTED_RECORDS_COUNT,
    }
    return {
        "instruction.md": instruction(
            family_id=family_id,
            build_skill=str(build_skill),
            build_script=str(build_script),
            validate_script=str(validate_script),
            build_arguments=build_arguments,
            validate_arguments=validate_arguments,
            outputs=outputs,
        ).encode(),
        "task.toml": task_toml(family_id, replicate).encode(),
        "tests/Dockerfile": (
            f"FROM {RUNTIME_IMAGE}\n"
            "COPY . /tests\n"
            "RUN chmod 0555 /tests/test.sh /tests/score.py\n"
            "WORKDIR /tests\n"
        ).encode(),
        "tests/test.sh": (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "python /tests/score.py \\\n"
            "  --config /tests/task-config.json \\\n"
            "  --pi-log /logs/agent/pi.txt \\\n"
            "  --reward /logs/verifier/reward.json \\\n"
            "  --diagnostics /logs/verifier/diagnostics.json\n"
        ).encode(),
        "tests/score.py": SCORER.read_bytes(),
        "tests/task-config.json": canonical_json(config).encode(),
    }


def materialize(output: Path) -> dict[str, Any]:
    """Create a new append-only frozen builder study."""

    if output.exists():
        raise StudyPreparationError(
            f"refusing to overwrite frozen study: {output}"
        )
    families = registered_families()
    output.mkdir(parents=True)
    harbor = freeze_patched_harbor(output)
    frozen_families: dict[str, dict[str, Any]] = {}
    for family_id in sorted(families):
        family = families[family_id]
        build_skill = family.get("build_skill")
        if not isinstance(build_skill, str) or not build_skill:
            raise StudyPreparationError(
                f"{family_id} has no build skill binding"
            )
        source_input = INPUT_ROOT / family_id
        source_skill = SKILLS_ROOT / build_skill
        destination_input = output / "inputs" / family_id
        destination_skill = output / "skills" / build_skill
        copy_checked_tree(source_input, destination_input)
        copy_checked_tree(source_skill, destination_skill)
        input_manifest = load_object(destination_input / "input-manifest.json")
        family_tasks = output / "tasks/development" / family_id
        for replicate, outputs in REPLICATES.items():
            task_root = family_tasks / replicate
            (task_root / "environment").mkdir(parents=True)
            for relative, payload in task_files(
                family_id=family_id,
                family=family,
                input_manifest=input_manifest,
                replicate=replicate,
                outputs=outputs,
            ).items():
                destination = task_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(payload)
        frozen_families[family_id] = {
            "build_skill": build_skill,
            "build_script": family["build_script"],
            "validate_script": family["validate_script"],
            "requires_hf_cache": bool(family["requires_hf_cache"]),
            "input_tree_sha256": tree_digest(destination_input),
            "skill_tree_sha256": tree_digest(destination_skill),
            "task_tree_sha256": tree_digest(family_tasks),
            "input_manifest_sha256": sha256_file(
                destination_input / "input-manifest.json"
            ),
        }
    shutil.copy2(REGISTRY, output / "families.json")
    manifest = {
        "schema_version": "semantic-okf-builder-token-frozen-inputs/3.0",
        "study_id": "20260730-semantic-okf-builder-token-v7",
        "dataset_id": "graphrag-papers-40",
        "mode": "builder-token",
        "model": MODEL,
        "pi_version": PI_VERSION,
        "thinking": THINKING,
        "runtime_image": RUNTIME_IMAGE,
        "runtime_image_id": RUNTIME_IMAGE_ID,
        "expected_records_sha256": EXPECTED_RECORDS_SHA256,
        "expected_records_count": EXPECTED_RECORDS_COUNT,
        "replicates": {
            key: list(value) for key, value in REPLICATES.items()
        },
        "families_registry_sha256": sha256_file(REGISTRY),
        "scorer_sha256": sha256_file(SCORER),
        "harbor": harbor,
        "families": frozen_families,
    }
    (output / "frozen-inputs.json").write_text(
        canonical_json(manifest), encoding="utf-8", newline="\n"
    )
    return manifest


def verify(output: Path) -> dict[str, Any]:
    """Verify one immutable frozen study against its recorded internal digests."""

    if not output.is_dir():
        raise StudyPreparationError(f"frozen study does not exist: {output}")
    expected_entries = {
        "families.json",
        "frozen-inputs.json",
        "harbor",
        "inputs",
        "skills",
        "tasks",
    }
    actual_entries = {path.name for path in output.iterdir()}
    if actual_entries != expected_entries:
        raise StudyPreparationError(
            "frozen builder study has unexpected top-level entries"
        )
    manifest = load_object(output / "frozen-inputs.json")
    if manifest.get("schema_version") != "semantic-okf-builder-token-frozen-inputs/3.0":
        raise StudyPreparationError("frozen builder study has an unsupported schema")

    def require_digest(actual: str, expected: Any, label: str) -> None:
        if not isinstance(expected, str) or actual != expected:
            raise StudyPreparationError(f"frozen {label} digest differs from its manifest")

    require_digest(
        sha256_file(output / "families.json"),
        manifest.get("families_registry_sha256"),
        "family registry",
    )
    families = manifest.get("families")
    if not isinstance(families, Mapping) or not families:
        raise StudyPreparationError("frozen builder study has no family bindings")
    expected_family_ids = set(families)
    for relative in ("inputs", "tasks/development"):
        actual = {path.name for path in (output / relative).iterdir() if path.is_dir()}
        if actual != expected_family_ids:
            raise StudyPreparationError(f"frozen {relative} family set differs from its manifest")

    expected_skill_names: set[str] = set()
    for family_id, value in families.items():
        if not isinstance(family_id, str) or not isinstance(value, Mapping):
            raise StudyPreparationError("frozen family binding is invalid")
        build_skill = value.get("build_skill")
        if not isinstance(build_skill, str) or not build_skill:
            raise StudyPreparationError(f"frozen family {family_id} has no build skill")
        expected_skill_names.add(build_skill)
        input_root = output / "inputs" / family_id
        skill_root = output / "skills" / build_skill
        task_root = output / "tasks" / "development" / family_id
        require_digest(
            tree_digest(input_root), value.get("input_tree_sha256"), f"{family_id} input tree"
        )
        require_digest(
            sha256_file(input_root / "input-manifest.json"),
            value.get("input_manifest_sha256"),
            f"{family_id} input manifest",
        )
        require_digest(
            tree_digest(skill_root), value.get("skill_tree_sha256"), f"{family_id} skill tree"
        )
        require_digest(
            tree_digest(task_root), value.get("task_tree_sha256"), f"{family_id} task tree"
        )
        for replicate in manifest.get("replicates", {}):
            scorer = task_root / str(replicate) / "tests" / "score.py"
            require_digest(
                sha256_file(scorer), manifest.get("scorer_sha256"), f"{family_id} scorer"
            )

    actual_skill_names = {
        path.name for path in (output / "skills").iterdir() if path.is_dir()
    }
    if actual_skill_names != expected_skill_names:
        raise StudyPreparationError("frozen skill set differs from its manifest")

    harbor = manifest.get("harbor")
    if not isinstance(harbor, Mapping):
        raise StudyPreparationError("frozen builder study has no Harbor binding")
    harbor_root = output / "harbor"
    require_digest(
        tree_digest(harbor_root / "harbor"),
        harbor.get("patched_tree_sha256"),
        "Harbor tree",
    )
    require_digest(
        sha256_file(harbor_root / "harbor-cli"),
        harbor.get("patched_entrypoint_sha256"),
        "Harbor entrypoint",
    )
    require_digest(
        sha256_file(harbor_root / "harbor" / "agents" / "installed" / "pi.py"),
        harbor.get("patched_adapter_sha256"),
        "Harbor Pi adapter",
    )
    return manifest


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate or check the frozen study."""

    args = parse_args(argv)
    output = args.output.resolve()
    manifest = verify(output) if args.check else materialize(output)
    print(
        json.dumps(
            {
                "status": "pass" if args.check else "generated",
                "output": str(output),
                "family_count": len(manifest["families"]),
                "task_count": len(manifest["families"]) * len(REPLICATES),
                "tree_sha256": tree_digest(output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StudyPreparationError as exc:
        raise SystemExit(str(exc)) from exc
