"""Strict persisted-config decoding for a prospectively reviewed Harbor study.

Harbor 0.18.0 omits defaults in durable TrialConfig JSON. Authenticate the exact
native definitions and writer before deriving those defaults without executing
their Python. This reader supports the local, deterministic Enterprise profile;
it deliberately rejects optional MCP, TPU and artifact-object configurations.
It never admits execution, repairs a sealed study, or reads a task body.

The caller must supply an independently bound expected trial projection from
the declared native job/task policy. Only prospectively declared generated
identities and staged skill paths belong in that projection. Container image,
resources, mounts, package digest and owner lineage still require their checks.
"""
from __future__ import annotations

import ast
import copy
from functools import wraps
import hashlib
import json
import math
from uuid import UUID


SOURCE_SHA256 = {
    "config": "bcdf4a0e55d2318da0595aa63ee09c0a8c4fdc8aee3e3fd326fc00853832d9c5",
    "writer": "15a40691a5aa03152de4f6878347272503aaa3f976cf3eb22a1ec0e5d62609c9",
}

# These are accepted JSON types, not fallback values. Actual omission defaults
# are derived only from the authenticated native AST below.
FIELDS = {
    "AgentConfig": {
        "name": "str?", "import_path": "str?", "model_name": "str?",
        "n_concurrent": "positive-int?", "concurrency_group": "str?",
        "skills": "strings", "override_timeout_sec": "number?",
        "override_setup_timeout_sec": "number?", "max_timeout_sec": "number?",
        "extra_allowed_hosts": "strings", "include_logs": "strings",
        "exclude_logs": "strings", "kwargs": "json-map", "env": "string-map",
        "mcp_servers": "empty-list",
    },
    "EnvironmentConfig": {
        "type": "str?", "import_path": "str?", "force_build": "bool",
        "delete": "bool", "cpu_enforcement_policy": "resource-mode",
        "memory_enforcement_policy": "resource-mode", "override_cpus": "int?",
        "override_memory_mb": "int?", "override_storage_mb": "int?",
        "override_gpus": "int?", "override_tpu": "null",
        "suppress_override_warnings": "false", "mounts": "mounts?",
        "extra_docker_compose": "strings", "env": "string-map",
        "kwargs": "json-map", "extra_allowed_hosts": "strings",
    },
    "VerifierConfig": {
        "override_timeout_sec": "number?", "max_timeout_sec": "number?",
        "include_logs": "strings", "exclude_logs": "strings", "env": "string-map",
        "import_path": "str?", "kwargs": "json-map", "disable": "bool",
    },
    "TaskConfig": {
        "path": "str?", "git_url": "str?", "git_commit_id": "str?", "name": "str?",
        "ref": "str?", "overwrite": "bool", "download_dir": "str?", "source": "str?",
    },
    "TrialConfig": {
        "task": "TaskConfig", "trial_name": "str", "trials_dir": "str",
        "install_only": "bool", "timeout_multiplier": "number",
        "agent_timeout_multiplier": "number?", "verifier_timeout_multiplier": "number?",
        "agent_setup_timeout_multiplier": "number?", "environment_build_timeout_multiplier": "number?",
        "agent": "AgentConfig", "environment": "EnvironmentConfig", "verifier": "VerifierConfig",
        "artifacts": "empty-list", "extra_instruction_paths": "strings", "job_id": "str?",
    },
}


class NativeConfigRefusal(ValueError):
    """A sanitized failure code that never includes input values or paths."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _require(condition, code):
    if not condition:
        raise NativeConfigRefusal(code)


def _object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "native-config-duplicate-key")
        result[key] = value
    return result


def _invalid_constant(_value):
    raise NativeConfigRefusal("native-config-nonfinite-number")


def strict_json(payload: bytes | str):
    """Parse JSON without duplicate members, non-finite numbers or coercions."""
    _require(type(payload) in (bytes, str), "native-config-payload-type")
    try:
        value = json.loads(payload, object_pairs_hook=_object, parse_constant=_invalid_constant)
        _json_value(value)
        return value
    except NativeConfigRefusal:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise NativeConfigRefusal("native-config-invalid-json") from None


def _json_value(value):
    if type(value) is float:
        _require(math.isfinite(value), "native-config-nonfinite-number")
    elif type(value) is dict:
        _require(all(type(key) is str for key in value), "native-config-map-key-type")
        for item in value.values():
            _json_value(item)
    elif type(value) is list:
        for item in value:
            _json_value(item)
    else:
        _require(value is None or type(value) in (str, int, bool), "native-config-json-type")


def _defaults(config_source):
    classes = {node.name: node for node in ast.parse(config_source).body if isinstance(node, ast.ClassDef)}

    def evaluate(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Attribute) and ast.unparse(node) == "ResourceMode.AUTO":
            return "auto"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "Path" and len(node.args) == 1 and not node.keywords:
                return evaluate(node.args[0])
            if node.func.id == "Field":
                keywords = {item.arg: item.value for item in node.keywords}
                if "default" in keywords:
                    return evaluate(keywords["default"])
                factory = keywords.get("default_factory")
                if isinstance(factory, ast.Name):
                    if factory.id == "list":
                        return []
                    if factory.id == "dict":
                        return {}
                    if factory.id in FIELDS:
                        return model(factory.id)
        raise NativeConfigRefusal("native-default-definition-unsupported")

    def model(name):
        _require(name in classes, "native-model-definition-missing")
        declarations = {
            node.target.id: node for node in classes[name].body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        }
        _require(set(declarations) == set(FIELDS[name]), "native-field-inventory-drift")
        return {key: evaluate(node.value) for key, node in declarations.items() if node.value is not None}

    return {name: model(name) for name in FIELDS}


def _mount(value):
    _require(type(value) is dict, "native-mount-type")
    allowed = {"type", "source", "target", "read_only", "bind", "volume", "image"}
    _require(set(value) <= allowed, "native-mount-unknown-field")
    _require({"type", "source", "target"} <= set(value), "native-mount-required-field")
    for key in ("type", "source", "target"):
        _require(type(value[key]) is str and bool(value[key]), "native-mount-string-type")
    _require(value["type"] in {"bind", "volume", "image"}, "native-mount-kind")
    if "read_only" in value:
        _require(value["read_only"] is True, "native-mount-read-only-literal")
    for key in ("bind", "volume", "image"):
        if key in value:
            nested = value[key]
            wanted = "create_host_path" if key == "bind" else "subpath"
            _require(type(nested) is dict and set(nested) <= {wanted}, "native-mount-nested-field")
            if wanted in nested:
                _require(nested[wanted] is False if key == "bind" else type(nested[wanted]) is str,
                         "native-mount-nested-type")


def _scalar(value, kind):
    if kind.endswith("?"):
        if value is None:
            return
        kind = kind[:-1]
    if kind == "null":
        valid = value is None
    elif kind == "false":
        valid = value is False
    elif kind == "bool":
        valid = type(value) is bool
    elif kind == "str":
        valid = type(value) is str
    elif kind == "number":
        valid = type(value) in (int, float)
        if valid and type(value) is float:
            valid = math.isfinite(value)
    elif kind in {"int", "positive-int"}:
        valid = type(value) is int and (kind == "int" or value >= 1)
    elif kind == "resource-mode":
        valid = type(value) is str and value in {"auto", "limit", "request", "guarantee", "ignore"}
    elif kind == "strings":
        valid = type(value) is list and all(type(item) is str for item in value)
    elif kind == "empty-list":
        valid = type(value) is list and not value
    elif kind in {"json-map", "string-map"}:
        valid = type(value) is dict and all(type(key) is str for key in value)
        if valid:
            _json_value(value)
            if kind == "string-map":
                valid = all(type(item) is str for item in value.values())
    elif kind == "mounts":
        valid = type(value) is list
        if valid:
            for item in value:
                _mount(item)
    else:
        raise NativeConfigRefusal("native-config-unsupported-type-rule")
    _require(valid, "native-config-field-type-or-unsupported-feature")


def _required_identity(raw):
    for chain in (
        ("trial_name",), ("trials_dir",), ("job_id",), ("task", "path"),
        ("agent", "name"), ("agent", "import_path"), ("agent", "model_name"),
        ("environment", "type"),
    ):
        item = raw
        for key in chain:
            _require(type(item) is dict and key in item, "native-config-required-identity-missing")
            item = item[key]
        _require(type(item) is str and bool(item.strip()), "native-config-required-identity-type")
    try:
        _require(str(UUID(raw["job_id"])) == raw["job_id"], "native-config-job-id-format")
    except ValueError:
        raise NativeConfigRefusal("native-config-job-id-format") from None
    _require("skills" in raw["agent"] and type(raw["agent"]["skills"]) is list
             and len(raw["agent"]["skills"]) == 1
             and type(raw["agent"]["skills"][0]) is str and bool(raw["agent"]["skills"][0]),
             "native-config-staged-skill-identity")


def _equivalent(left, right, kind=None):
    if type(left) is not type(right):
        return (kind in {"number", "number?"} and type(left) in (int, float)
                and type(right) in (int, float) and left == right)
    if type(left) is dict:
        fields = FIELDS.get(kind, {})
        return set(left) == set(right) and all(_equivalent(left[key], right[key], fields.get(key)) for key in left)
    if type(left) is list:
        return len(left) == len(right) and all(_equivalent(a, b) for a, b in zip(left, right))
    return left == right


def _refusal_boundary(operation):
    """Keep recursion failures in expansion/comparison out of caller messages."""
    @wraps(operation)
    def checked(*args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except NativeConfigRefusal:
            raise
        except RecursionError:
            raise NativeConfigRefusal("native-config-nesting-limit") from None
    return checked


class NativeTrialReader:
    """Decode supported durable inputs using source-authenticated defaults."""

    def __init__(self, *, config_source: bytes, writer_source: bytes):
        for name, value in (("config", config_source), ("writer", writer_source)):
            _require(type(value) is bytes and hashlib.sha256(value).hexdigest() == SOURCE_SHA256[name],
                     "native-" + name + "-source-drift")
        self._defaults = _defaults(config_source)

    @_refusal_boundary
    def decode(self, payload: bytes | str) -> dict:
        """Restore only source-proven omissions; preserve explicit values."""
        raw = strict_json(payload)
        _require(type(raw) is dict, "native-trial-config-object-required")
        _required_identity(raw)

        def expand(value, model):
            _require(type(value) is dict, "native-config-model-type")
            _require(set(value) <= set(FIELDS[model]), "native-config-unknown-field")
            result = copy.deepcopy(self._defaults[model])
            result.update(copy.deepcopy(value))
            _require(set(result) == set(FIELDS[model]), "native-config-required-field-missing")
            for key, kind in FIELDS[model].items():
                if kind in FIELDS:
                    result[key] = expand(result[key], kind)
                else:
                    _scalar(result[key], kind)
            return result

        return expand(raw, "TrialConfig")

    @_refusal_boundary
    def require_policy(self, payload: bytes | str, *, expected: bytes | str,
                       phase: str, role: str) -> dict:
        """Match every effective input against a separately bound projection.

        ``expected`` must come from trusted job/task/owner policy, never by
        copying the observed runtime configuration. Role does not transform
        TrialConfig: Harbor uses the same trial inputs for agent and verifier.
        The caller separately enforces that role's native container contract.
        """
        _require(type(phase) is str and phase in {"development", "recalculation", "validation"}, "native-config-phase")
        _require(type(role) is str and role in {"agent", "verifier"}, "native-config-role")
        actual, wanted = self.decode(payload), self.decode(expected)
        final = phase == "recalculation"
        agent_name = "enterprise-stratified-final" if final else "enterprise-stratified-retrieval"
        agent_import = "enterprise_final_agent:SkillRetrievalAgent" if final else "enterprise_agent:SkillRetrievalAgent"
        for value in (actual, wanted):
            agent, environment, verifier, task = (value[key] for key in ("agent", "environment", "verifier", "task"))
            _require(not value["install_only"] and value["timeout_multiplier"] == 1.0
                     and not value["extra_instruction_paths"] and not value["artifacts"], "native-extra-execution-input")
            _require(all(value[key] is None for key in (
                "agent_timeout_multiplier", "verifier_timeout_multiplier", "agent_setup_timeout_multiplier",
                "environment_build_timeout_multiplier")), "native-timeout-multiplier-policy")
            _require(agent["name"] == agent_name and agent["import_path"] == agent_import
                     and agent["model_name"] == "local/deterministic-retrieval-v3", "native-agent-policy")
            _require(agent["override_timeout_sec"] == (10800 if final else None), "native-timeout-profile-policy")
            _require(environment["type"] == "docker" and environment["import_path"] is None,
                     "native-environment-policy")
            _require(all(task[key] is None for key in ("git_url", "git_commit_id", "name", "ref", "download_dir", "source"))
                     and task["overwrite"] is False, "native-local-task-policy")
            _require(verifier["disable"] is False, "native-verifier-disabled")
        _require(_equivalent(actual, wanted, "TrialConfig"), "native-effective-input-policy-drift")
        return actual
