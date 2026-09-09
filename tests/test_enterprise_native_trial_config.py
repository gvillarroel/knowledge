"""Pure persisted-config regression cases; no Harbor jobs or private fixtures."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / "evaluations/enterprise_native_trial_config.py"
spec = importlib.util.spec_from_file_location("enterprise_native_trial_config", MODULE)
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)

# An independent synthetic AST fixture. Production accepts only its two pinned
# complete native source files. Actual-runtime parity is a separate review;
# these unit tests do not claim native source provenance or live admission.
DEFINITIONS = b'''
class AgentConfig(BaseModel):
    name: str | None = None
    import_path: str | None = None
    model_name: str | None = None
    n_concurrent: int | None = Field(default=None, ge=1)
    concurrency_group: str | None = None
    skills: list[str] = Field(default_factory=list)
    override_timeout_sec: float | None = None
    override_setup_timeout_sec: float | None = None
    max_timeout_sec: float | None = None
    extra_allowed_hosts: list[str] = Field(default_factory=list)
    include_logs: list[str] = Field(default_factory=list)
    exclude_logs: list[str] = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)
    env: dict = Field(default_factory=dict)
    mcp_servers: list = Field(default_factory=list)
class EnvironmentConfig(BaseModel):
    type: str | None = None
    import_path: str | None = None
    force_build: bool = False
    delete: bool = True
    cpu_enforcement_policy: str = ResourceMode.AUTO
    memory_enforcement_policy: str = ResourceMode.AUTO
    override_cpus: int | None = None
    override_memory_mb: int | None = None
    override_storage_mb: int | None = None
    override_gpus: int | None = None
    override_tpu: object = None
    suppress_override_warnings: bool = Field(default=False, exclude=True)
    mounts: list | None = None
    extra_docker_compose: list = Field(default_factory=list)
    env: dict = Field(default_factory=dict)
    kwargs: dict = Field(default_factory=dict)
    extra_allowed_hosts: list = Field(default_factory=list)
class VerifierConfig(BaseModel):
    override_timeout_sec: float | None = None
    max_timeout_sec: float | None = None
    include_logs: list = Field(default_factory=list)
    exclude_logs: list = Field(default_factory=list)
    env: dict = Field(default_factory=dict)
    import_path: str | None = None
    kwargs: dict = Field(default_factory=dict)
    disable: bool = False
class TaskConfig(BaseModel):
    path: Path | None = None
    git_url: str | None = None
    git_commit_id: str | None = None
    name: str | None = None
    ref: str | None = None
    overwrite: bool = False
    download_dir: Path | None = None
    source: str | None = None
class TrialConfig(BaseModel):
    task: TaskConfig
    trial_name: str = ""
    trials_dir: Path = Path("trials")
    install_only: bool = Field(default=False)
    timeout_multiplier: float = 1.0
    agent_timeout_multiplier: float | None = None
    verifier_timeout_multiplier: float | None = None
    agent_setup_timeout_multiplier: float | None = None
    environment_build_timeout_multiplier: float | None = None
    agent: AgentConfig = Field(default_factory=AgentConfig)
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig)
    verifier: VerifierConfig = Field(default_factory=VerifierConfig)
    artifacts: list = Field(default_factory=list)
    extra_instruction_paths: list = Field(default_factory=list)
    job_id: UUID | None = None
'''
WRITER = b'config_path.write_text(config.model_dump_json(indent=4, exclude_defaults=True))\n'


def synthetic_trial():
    """Provide only non-default fields, like the actual native durable writer."""
    return {
        "task": {"path": "/repo/tasks/public/task"},
        "trial_name": "task__example", "trials_dir": "/repo/jobs/example",
        "job_id": "8df50416-9030-4c50-8ead-d06dbbca0b8c",
        "agent": {
            "name": "enterprise-stratified-retrieval",
            "import_path": "enterprise_agent:SkillRetrievalAgent",
            "model_name": "local/deterministic-retrieval-v3",
            "skills": ["/repo/staging/skills/build-semantic-okf-knowledge-skill"],
        },
        "environment": {"type": "docker", "mounts": [{
            "type": "bind", "source": "/repo/models", "target": "/models/huggingface/hub",
            "read_only": True, "bind": {"create_host_path": False},
        }]},
    }


def replace(value, chain, item):
    value = copy.deepcopy(value)
    cursor = value
    for key in chain[:-1]:
        cursor = cursor.setdefault(key, {})
    cursor[chain[-1]] = item
    return value


class NativeTrialConfigTests(unittest.TestCase):
    def setUp(self):
        self.hashes = patch.dict(codec.SOURCE_SHA256, {
            "config": hashlib.sha256(DEFINITIONS).hexdigest(),
            "writer": hashlib.sha256(WRITER).hexdigest(),
        })
        self.hashes.start()
        self.addCleanup(self.hashes.stop)
        self.reader = codec.NativeTrialReader(config_source=DEFINITIONS, writer_source=WRITER)
        self.raw = synthetic_trial()

    def policy(self, actual=None, expected=None, phase="development", role="agent"):
        return self.reader.require_policy(json.dumps(actual or self.raw),
            expected=json.dumps(expected or self.raw), phase=phase, role=role)

    def test_actual_shape_and_explicit_default_shape_are_equivalent(self):
        full = self.policy()
        self.assertEqual(full["extra_instruction_paths"], [])
        self.assertIs(full["install_only"], False)
        self.assertEqual(full["timeout_multiplier"], 1.0)
        self.assertEqual(full["agent"]["mcp_servers"], [])
        self.assertEqual(full["agent"]["kwargs"], {})
        self.assertIsNone(full["agent"]["override_timeout_sec"])
        self.assertEqual(full["environment"]["extra_docker_compose"], [])
        self.assertEqual(full["environment"]["kwargs"], {})
        self.assertEqual(self.policy(full), full)
        self.assertEqual(self.policy(expected=full), full)

    def test_all_eight_original_overrides_are_rejected(self):
        for chain, value in (
            (("extra_instruction_paths",), ["/extra"]), (("install_only",), True),
            (("timeout_multiplier",), 2), (("agent", "mcp_servers"), [{"name": "unexpected"}]),
            (("agent", "kwargs"), {"extra": 1}), (("agent", "override_timeout_sec"), 10800),
            (("environment", "extra_docker_compose"), ["/extra.yaml"]),
            (("environment", "kwargs"), {"extra": 1}),
        ):
            with self.subTest(field=chain), self.assertRaises(codec.NativeConfigRefusal):
                self.policy(replace(self.raw, chain, value))

    def test_decoding_preserves_explicit_values_before_policy_comparison(self):
        explicit = replace(self.raw, ("agent", "kwargs"), {"limit": 2})
        explicit["timeout_multiplier"] = 3
        decoded = self.reader.decode(json.dumps(explicit))
        self.assertEqual(decoded["agent"]["kwargs"], {"limit": 2})
        self.assertEqual(decoded["timeout_multiplier"], 3)
        self.assertEqual(explicit["agent"]["kwargs"], {"limit": 2})

    def test_complete_effective_input_comparison_covers_unindexed_fields(self):
        cases = [
            (("agent", "env"), {"TOKEN": "synthetic-sensitive-value"}),
            (("agent", "extra_allowed_hosts"), ["example.invalid"]),
            (("agent", "max_timeout_sec"), 12), (("agent", "n_concurrent"), 2),
            (("agent", "concurrency_group"), "another"), (("agent", "include_logs"), ["*"]),
            (("agent", "override_setup_timeout_sec"), 12), (("environment", "force_build"), True),
            (("environment", "delete"), False), (("environment", "cpu_enforcement_policy"), "ignore"),
            (("environment", "override_cpus"), 8), (("environment", "env"), {"EXTRA": "1"}),
            (("verifier", "kwargs"), {"extra": True}), (("verifier", "disable"), True),
            (("verifier", "override_timeout_sec"), 20), (("agent_timeout_multiplier",), 2),
            (("task", "git_url"), "https://example.invalid/task"),
            (("task", "overwrite"), True), (("trial_name",), "other"),
            (("task", "path"), "/another/task"), (("trials_dir",), "/another/job"),
            (("job_id",), "4847ea2a-5e32-438d-a001-b38c4fe70468"),
            (("agent", "skills"), ["/another/skill"]),
        ]
        for chain, value in cases:
            with self.subTest(field=chain), self.assertRaises(codec.NativeConfigRefusal) as raised:
                self.policy(replace(self.raw, chain, value))
            self.assertNotIn("synthetic-sensitive-value", str(raised.exception))

    def test_missing_identities_never_receive_model_generated_defaults(self):
        for chain in (("trial_name",), ("job_id",), ("trials_dir",), ("task",),
                      ("task", "path"), ("agent",), ("agent", "name"), ("agent", "import_path"),
                      ("agent", "model_name"), ("agent", "skills"), ("environment", "type")):
            value = copy.deepcopy(self.raw)
            cursor = value
            for key in chain[:-1]:
                cursor = cursor[key]
            del cursor[chain[-1]]
            with self.subTest(field=chain), self.assertRaises(codec.NativeConfigRefusal):
                self.reader.decode(json.dumps(value))

    def test_unknown_fields_and_legacy_aliases_reject_at_all_model_levels(self):
        for chain in (("unexpected",), ("task", "unexpected"), ("agent", "unexpected"),
                      ("environment", "unexpected"), ("verifier", "unexpected"),
                      ("environment", "mounts_json")):
            with self.subTest(field=chain), self.assertRaises(codec.NativeConfigRefusal):
                self.policy(replace(self.raw, chain, None))

    def test_mount_unknown_fields_and_implicit_modes_reject(self):
        mount = self.raw["environment"]["mounts"][0]
        changes = [dict(mount, unexpected=1), dict(mount, bind={"unexpected": False}),
                   dict(mount, bind={"create_host_path": 0}), dict(mount, read_only=1),
                   dict(mount, read_only=False), dict(mount, target="/workspace"),
                   dict(mount, source="/another/cache"), {k: v for k, v in mount.items() if k != "read_only"}]
        for changed in changes:
            with self.subTest(mount=changed), self.assertRaises(codec.NativeConfigRefusal):
                self.policy(replace(self.raw, ("environment", "mounts"), [changed]))

    def test_duplicate_json_members_reject_even_when_values_are_identical(self):
        for payload in ('{"task": {}, "task": {}}', '{"agent": {"name": "a", "name": "a"}}',
                        '{"environment": {"mounts": [{"bind": {"create_host_path": false, "create_host_path": false}}]}}'):
            with self.subTest(payload=payload), self.assertRaisesRegex(codec.NativeConfigRefusal, "duplicate-key"):
                self.reader.decode(payload)

    def test_nonfinite_numbers_and_malformed_json_reject(self):
        for payload in ('NaN', 'Infinity', '-Infinity', '1e9999', '{"a": 1e9999}',
                        b'\xff', '[', '[1,]', '{"a": 1} trailing'):
            with self.subTest(payload=payload), self.assertRaises(codec.NativeConfigRefusal):
                self.reader.decode(payload)

    def test_invalid_types_do_not_coerce(self):
        for chain, value in (
            (("timeout_multiplier",), True), (("timeout_multiplier",), "1"),
            (("agent", "override_timeout_sec"), True), (("agent", "n_concurrent"), 1.0),
            (("agent", "n_concurrent"), 0), (("environment", "override_cpus"), True),
            (("install_only",), 0), (("verifier", "disable"), 0),
            (("agent", "skills"), [3]), (("environment", "env"), ["A=B"]),
            (("environment", "env"), {"A": 3}), (("environment", "cpu_enforcement_policy"), "AUTO"),
            (("job_id",), "not-a-uuid"), (("trial_name",), ""), (("verifier",), []),
        ):
            with self.subTest(field=chain, value=value), self.assertRaises(codec.NativeConfigRefusal):
                self.reader.decode(json.dumps(replace(self.raw, chain, value)))

    def test_all_three_phases_and_both_roles_keep_timeout_policy(self):
        for phase in ("development", "recalculation", "validation"):
            expected = copy.deepcopy(self.raw)
            if phase == "recalculation":
                expected["agent"].update(name="enterprise-stratified-final",
                    import_path="enterprise_final_agent:SkillRetrievalAgent", override_timeout_sec=10800)
            for role in ("agent", "verifier"):
                with self.subTest(phase=phase, role=role):
                    full = self.policy(expected, expected, phase, role)
                    self.assertEqual(self.policy(full, expected, phase, role), full)
                    wrong = copy.deepcopy(expected)
                    if phase == "recalculation":
                        del wrong["agent"]["override_timeout_sec"]
                    else:
                        wrong["agent"]["override_timeout_sec"] = 10800
                    with self.assertRaisesRegex(codec.NativeConfigRefusal, "timeout-profile"):
                        self.policy(wrong, expected, phase, role)

    def test_invalid_phase_role_and_expected_policy_reject(self):
        for phase, role in (("preparation", "agent"), ("development", "unknown")):
            with self.assertRaises(codec.NativeConfigRefusal):
                self.policy(phase=phase, role=role)
        with self.assertRaises(codec.NativeConfigRefusal):
            self.policy(expected=replace(self.raw, ("agent", "name"), "different"))

    def test_integer_json_spelling_of_float_default_is_equivalent(self):
        full = self.policy()
        full["timeout_multiplier"] = 1
        self.assertEqual(self.policy(full)["timeout_multiplier"], 1)

    def test_arbitrary_json_maps_preserve_numeric_types_at_every_depth(self):
        for component in ("agent", "environment", "verifier"):
            for expected_value, actual_value in (
                ({"typed_switch": 1}, {"typed_switch": 1.0}),
                ({"typed_switch": 1.0}, {"typed_switch": 1}),
                ({"nested": [{"timeout_multiplier": 1}]}, {"nested": [{"timeout_multiplier": 1.0}]}),
            ):
                expected = replace(self.raw, (component, "kwargs"), expected_value)
                actual = replace(self.raw, (component, "kwargs"), actual_value)
                with self.subTest(component=component, expected=expected_value):
                    self.assertEqual(self.policy(expected, expected)[component]["kwargs"], expected_value)
                    with self.assertRaisesRegex(codec.NativeConfigRefusal, "effective-input-policy-drift"):
                        self.policy(actual, expected)

    def test_integer_parsing_limit_gets_a_static_refusal(self):
        with self.assertRaisesRegex(codec.NativeConfigRefusal, "^native-config-invalid-json$"):
            self.reader.decode('{"integer": ' + '1' * 5000 + '}')

    def test_nonstring_phase_and_role_get_static_refusals(self):
        for value in ([], {}, None, 1, True):
            with self.subTest(value=value):
                with self.assertRaisesRegex(codec.NativeConfigRefusal, "^native-config-phase$"):
                    self.policy(phase=value)
                with self.assertRaisesRegex(codec.NativeConfigRefusal, "^native-config-role$"):
                    self.policy(role=value)

    def test_deep_supported_json_gets_a_static_refusal_during_expansion(self):
        # Exhausting Python's stack can disable a coverage trace hook even when
        # the public API catches the error. Keep the genuine boundary check in
        # a child process so later application tests remain measured.
        trace_before = sys.gettrace()
        program = (
            "import runpy, sys, unittest\n"
            "case = runpy.run_path(sys.argv[1])['NativeTrialConfigTests']"
            "('_check_deep_supported_json_refusals')\n"
            "result = unittest.TextTestRunner().run(unittest.TestSuite([case]))\n"
            "raise SystemExit(0 if result.wasSuccessful() else 1)\n"
        )
        result = subprocess.run([sys.executable, "-B", "-c", program, str(Path(__file__).resolve())],
                                capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIs(sys.gettrace(), trace_before)

    def _check_deep_supported_json_refusals(self):
        nested = 1
        for _ in range(600):
            nested = {"inner": nested}
        raw = synthetic_trial()
        raw["agent"]["kwargs"] = nested
        payload = json.dumps(raw)
        # JSON parsing itself succeeds. Expansion's copy stack is separately
        # bounded, so public decode must normalize its recursion failure too.
        self.assertEqual(codec.strict_json(payload)["trial_name"], raw["trial_name"])
        for operation in (
            lambda: self.reader.decode(payload),
            lambda: self.reader.require_policy(payload, expected=json.dumps(self.raw),
                                                phase="development", role="agent"),
        ):
            with self.assertRaisesRegex(codec.NativeConfigRefusal, "^native-config-nesting-limit$"):
                operation()

    def test_policy_comparison_recursion_and_specific_refusals_keep_static_codes(self):
        with patch.object(codec, "_equivalent", side_effect=RecursionError("synthetic-sensitive-value")):
            with self.assertRaisesRegex(codec.NativeConfigRefusal, "^native-config-nesting-limit$"):
                self.policy()
        with patch.object(codec, "_equivalent", side_effect=codec.NativeConfigRefusal("native-effective-input-policy-drift")):
            with self.assertRaisesRegex(codec.NativeConfigRefusal, "^native-effective-input-policy-drift$"):
                self.policy()

    def test_each_native_source_is_authenticated_before_any_default(self):
        for sources in ({"config_source": DEFINITIONS + b"\n", "writer_source": WRITER},
                        {"config_source": DEFINITIONS, "writer_source": WRITER + b"\n"}):
            with self.assertRaisesRegex(codec.NativeConfigRefusal, "source-drift"):
                codec.NativeTrialReader(**sources)

    def test_supported_inventory_is_checked_against_authenticated_ast(self):
        changed = DEFINITIONS + b'    new_execution_input: str = "unexpected"\n'
        with patch.dict(codec.SOURCE_SHA256, {"config": hashlib.sha256(changed).hexdigest()}):
            with self.assertRaisesRegex(codec.NativeConfigRefusal, "field-inventory-drift"):
                codec.NativeTrialReader(config_source=changed, writer_source=WRITER)

    def test_default_factories_are_never_executed(self):
        changed = DEFINITIONS.replace(b"Path(\"trials\")", b'open("/synthetic/forbidden", "w")')
        with patch.dict(codec.SOURCE_SHA256, {"config": hashlib.sha256(changed).hexdigest()}):
            with self.assertRaisesRegex(codec.NativeConfigRefusal, "default-definition-unsupported"):
                codec.NativeTrialReader(config_source=changed, writer_source=WRITER)

    def test_separate_decode_results_never_share_mutable_defaults(self):
        first = self.policy()
        first["agent"]["kwargs"]["altered"] = True
        first["environment"]["extra_docker_compose"].append("changed")
        second = self.policy()
        self.assertEqual(second["agent"]["kwargs"], {})
        self.assertEqual(second["environment"]["extra_docker_compose"], [])


if __name__ == "__main__":
    unittest.main()
