"""Pure admission scope regressions using synthetic metadata, without dispatch."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "evaluations/enterprise_execution_scope.py"
spec = importlib.util.spec_from_file_location("enterprise_execution_scope", MODULE)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ScopeChecks(unittest.TestCase):
    COMPOSE_EXECUTABLES = (
        "docker compose", "/usr/bin/docker compose",
        "/usr/libexec/docker/cli-plugins/docker-compose",
        "/usr/libexec/docker/cli-plugins/docker-compose compose",
        '"C:\\Program Files\\Docker\\docker.exe" compose',
        '"C:\\Program Files\\Docker\\docker-compose.exe" compose',
    )

    def compose(self, executable, *, context=None, project="synthetic"):
        context = context or "/repo/tmp/e7/tasks/development/opaque-public/environment"
        return (f'{executable} --project-name {project} --project-directory "{context}" '
                f'-f "{context}/docker-compose.yaml" up -d')

    def test_native_parent_and_plugin_child_receive_the_same_scope_decision(self):
        # The process hierarchy reproduces the observed native relationship;
        # ancestry itself grants no task, phase or mount exception.
        processes = [
            {"pid": 100, "parent": 1, "command": "python /repo/tmp/current/run.py"},
            {"pid": 101, "parent": 100, "command": self.compose("/usr/bin/docker compose")},
            {"pid": 102, "parent": 101, "command": self.compose(
                "/usr/libexec/docker/cli-plugins/docker-compose compose")},
        ]
        self.assertFalse(any(guard.references_old_execution(p["command"], self.reservation)
                             for p in processes))
        processes[-1]["command"] += " -f /repo/tmp/e7/undeclared.yaml"
        self.assertTrue(guard.references_old_execution(processes[-1]["command"], self.reservation))

    def test_native_compose_spellings_accept_only_declared_development_context(self):
        for executable in self.COMPOSE_EXECUTABLES:
            with self.subTest(executable=executable):
                command = self.compose(executable)
                self.assertFalse(guard.references_old_execution(command, self.reservation))
                for changed in (
                    command.replace("/environment", "/environment-extra"),
                    command.replace("docker-compose.yaml", "other.yaml"),
                    command.replace("/environment", "/environment/../tests"),
                    command + " /repo/tmp/e7/search/old-job",
                    command + " -v /repo/tmp/e7:/workspace:ro",
                    command + " /repo/evaluations/enterprise-stratified-evolution/run.py",
                ):
                    self.assertTrue(guard.references_old_execution(changed, self.reservation))

    def test_native_compose_does_not_bypass_verifier_or_private_phase_controls(self):
        for executable in self.COMPOSE_EXECUTABLES:
            with self.subTest(executable=executable):
                context = "/repo/tmp/e7/tasks/development/opaque-public/tests"
                command = self.compose(executable, context=context, project="synthetic__verifier__main")
                self.assertFalse(guard.references_old_execution(command, self.reservation))
                self.assertTrue(guard.references_old_execution(
                    command.replace("__verifier__", "__agent__"), self.reservation))
                private = self.compose(executable, context="/repo/tmp/e7/tasks/validation/opaque-private/environment")
                for phase in ("preparation", "development", "recalculation"):
                    self.assertTrue(guard.references_old_execution(private, self.reservation, phase))
                self.assertFalse(guard.references_old_execution(private, self.reservation, "validation"))

    def test_plugin_mount_exceptions_preserve_mode_destination_and_role(self):
        for executable in self.COMPOSE_EXECUTABLES:
            with self.subTest(executable=executable):
                command = self.compose(executable)
                cache = " --mount type=bind,src=/repo/tmp/e5/models/hub,dst=/models/huggingface/hub,readonly"
                self.assertFalse(guard.references_old_execution(command + cache, self.reservation))
                for altered in (cache.replace(",readonly", ",readonly=false"),
                                cache.replace("dst=/models/huggingface/hub", "dst=/workspace"),
                                cache.replace("src=/repo/tmp/e5/models/hub", "src=/repo/tmp/e5/models")):
                    self.assertTrue(guard.references_old_execution(command + altered, self.reservation))

    def test_docker_mentions_or_similar_executable_names_gain_no_exception(self):
        for executable in ("python docker compose", "echo docker compose", "notdocker compose",
                           "docker-compose-helper", "my-docker-compose", '"unterminated docker compose'):
            with self.subTest(executable=executable):
                self.assertTrue(guard.references_old_execution(self.compose(executable), self.reservation))

    def test_only_native_cli_build_is_a_build_context_exception(self):
        context = "/repo/tmp/e7/tasks/development/opaque-public/environment"
        for executable in ("docker build", "/usr/bin/docker buildx build", "docker.exe build"):
            self.assertFalse(guard.references_old_execution(executable + " " + context, self.reservation))
        for executable in ("docker-compose build", "echo docker build", "notdocker build"):
            self.assertTrue(guard.references_old_execution(executable + " " + context, self.reservation))

    def test_empty_or_unrelated_command_and_mount_metadata_have_no_old_reference(self):
        for command in ("", "   ", "python -B script.py", "docker --version", "docker-compose version"):
            self.assertFalse(guard.references_old_execution(command, self.reservation))
        self.assertFalse(guard.old_execution_mount({}, self.reservation))

    def setUp(self):
        self.reservation = {
            "repositoryRoots": ["/repo", "C:/repo", "/mnt/c/repo"],
            "historicalStudies": [{"studyRoot": "old/study", "studySha256": "a",
                "ledgerSha256": "b", "headSha256": "c", "requireAllStagesTerminal": True}],
            "historicalWorkRoots": ["tmp/e7", "tmp/e5"],
            "legacyDispatchEntrypoints": ["evaluations/enterprise-stratified-evolution/run.py"],
            "historicalReadOnlyMounts": [
                {"path": "tmp/e5/models/hub", "target": "/models/huggingface/hub",
                 "phases": sorted(guard.PHASES), "purpose": "pinned-model-cache"},
                {"path": "tmp/e7/tasks/development/opaque-public/tests", "target": "/tests",
                 "phases": ["preparation", "development"], "purpose": "separate-verifier-tests"},
                {"path": "tmp/e7/tasks/validation/opaque-private/tests", "target": "/tests",
                 "phases": ["validation"], "purpose": "separate-verifier-tests"}],
            "historicalDockerContexts": [
                {"path": "tmp/e7/tasks/development/opaque-public/environment",
                 "phases": ["preparation", "development"], "role": "agent"},
                {"path": "tmp/e7/tasks/development/opaque-public/tests",
                 "phases": ["preparation", "development"], "role": "separate-verifier"},
                {"path": "tmp/e7/tasks/validation/opaque-private/environment",
                 "phases": ["validation"], "role": "agent"}],
        }
        self.labels = {"com.docker.compose.project": "synthetic__verifier__main"}

    def mount(self, source, *, target="/tests", readonly=True):
        return {"Type": "bind", "Source": "/mnt/c/repo/" + source,
                "Destination": target, "RW": not readonly}

    def test_current_and_prefix_neighbor_paths_are_distinct(self):
        for value in ("python /repo/tmp/e8/run.py", "python /repo/tmp/e70/run.py"):
            self.assertFalse(guard.references_old_execution(value, self.reservation))

    def test_original_dispatch_and_job_mount_are_rejected(self):
        for value in ("python /repo/tmp/e7/run.py", "harbor run --config /repo/tmp/e7/jobs/job.json",
                      "python /repo/evaluations/enterprise-stratified-evolution/run.py"):
            self.assertTrue(guard.references_old_execution(value, self.reservation))
        for value in ("tmp/e7", "tmp/e7/search", "tmp/e7/tasks/development/opaque-public"):
            self.assertTrue(guard.old_execution_mount(self.mount(value), self.reservation, labels=self.labels))

    def test_model_cache_requires_readonly_and_exact_target(self):
        for path in ("tmp/e5/models/hub", "tmp/e5/models/hub/snapshot"):
            self.assertFalse(guard.old_execution_mount(self.mount(path, target="/models/huggingface/hub"), self.reservation))
        for path, target, readonly in (("tmp/e5/models/hub", "/models/huggingface/hub", False),
                                       ("tmp/e5/models/hub-extra", "/models/huggingface/hub", True),
                                       ("tmp/e5/models/hub", "/workspace", True)):
            self.assertTrue(guard.old_execution_mount(self.mount(path, target=target, readonly=readonly), self.reservation))

    def test_tests_require_exact_path_readonly_target_and_separate_identity(self):
        path = "tmp/e7/tasks/development/opaque-public/tests"
        self.assertFalse(guard.old_execution_mount(self.mount(path), self.reservation, labels=self.labels))
        for mount, labels in ((self.mount(path), {}), (self.mount(path, readonly=False), self.labels),
                              (self.mount(path, target="/dataset"), self.labels),
                              (self.mount(path + "/runtime"), self.labels),
                              (self.mount(path + "-extra"), self.labels)):
            self.assertTrue(guard.old_execution_mount(mount, self.reservation, labels=labels))

    def test_private_tests_are_phase_sealed(self):
        mount = self.mount("tmp/e7/tasks/validation/opaque-private/tests")
        for phase in ("preparation", "development", "recalculation"):
            self.assertTrue(guard.old_execution_mount(mount, self.reservation, phase, self.labels))
        self.assertFalse(guard.old_execution_mount(mount, self.reservation, "validation", self.labels))

    def test_nonbind_mount_is_not_allowed(self):
        mount = self.mount("tmp/e7/tasks/development/opaque-public/tests"); mount["Type"] = "volume"
        self.assertTrue(guard.old_execution_mount(mount, self.reservation, labels=self.labels))

    def test_docker_cli_readonly_mounts_are_scoped(self):
        command = "docker run --name synthetic__verifier__main -v /repo/tmp/e7/tasks/development/opaque-public/tests:/tests:ro image"
        self.assertFalse(guard.references_old_execution(command, self.reservation))
        for changed in (command.replace(":ro", ":rw"), command.replace("__verifier__", "__agent__"),
                        command.replace(":/tests:", ":/dataset:"), command.replace("/tests:/tests", ":/tests")):
            self.assertTrue(guard.references_old_execution(changed, self.reservation))
        model = "docker run --mount type=bind,src=/repo/tmp/e5/models/hub,dst=/models/huggingface/hub,readonly image"
        self.assertFalse(guard.references_old_execution(model, self.reservation))
        self.assertTrue(guard.references_old_execution(model.replace(",readonly", ",readonly=false"), self.reservation))

    def test_readonly_conflicts_are_not_an_exception(self):
        command = "docker run --mount type=bind,src=/repo/tmp/e5/models/hub,dst=/models/huggingface/hub,readonly=false,ro image"
        self.assertTrue(guard.references_old_execution(command, self.reservation))

    def test_native_compose_project_directory_and_files_are_exact(self):
        root = "/repo/tmp/e7/tasks/development/opaque-public/environment"
        command = f"docker compose --project-name synthetic --project-directory {root} -f {root}/docker-compose.yaml up -d"
        self.assertFalse(guard.references_old_execution(command, self.reservation))
        for changed in (command.replace("/environment", "/environment-extra"),
                        command.replace("docker-compose.yaml", "other.yaml")):
            self.assertTrue(guard.references_old_execution(changed, self.reservation))
        verifier = command.replace("/environment", "/tests").replace("--project-name synthetic", "--project-name synthetic__verifier__main")
        self.assertFalse(guard.references_old_execution(verifier, self.reservation))
        self.assertTrue(guard.references_old_execution(verifier.replace("__verifier__", "__agent__"), self.reservation))

    def test_docker_build_context_is_not_a_mount_exception(self):
        path = "/repo/tmp/e7/tasks/development/opaque-public/environment"
        self.assertFalse(guard.references_old_execution(f"docker build --network=none -t fixture {path}", self.reservation))
        self.assertTrue(guard.references_old_execution(f"docker run -v {path}:/workspace:ro image", self.reservation))

    def test_extra_historical_reference_is_not_redacted(self):
        command = "docker run -v /repo/tmp/e5/models/hub:/models/huggingface/hub:ro -v /repo/tmp/e7:/workspace:ro image"
        self.assertTrue(guard.references_old_execution(command, self.reservation))

    def test_mount_ancestors_are_rejected_on_both_bound_hosts(self):
        for source in ("/", "/repo", "/repo/tmp", "C:/", "C:/repo", "C:/repo/tmp", "/mnt/c", "/mnt/c/repo"):
            mount = {"Type": "bind", "Source": source, "Destination": "/workspace", "RW": False}
            with self.subTest(source=source):
                self.assertTrue(guard.old_execution_mount(mount, self.reservation))
                self.assertTrue(guard.references_old_execution(
                    f'docker run -v "{source}:/workspace:ro" image', self.reservation))
        self.assertFalse(guard.old_execution_mount(
            self.mount("tmp/e8/logs", target="/logs", readonly=False), self.reservation))

    def test_traversal_and_undeclared_host_aliases_cannot_gain_cache_exception(self):
        for source in ("/repo/tmp/e5/models/hub/../../../e7", "/repo/tmp/e5/models/hub/./snapshot",
                       "/unexpected/tmp/e5/models/hub", "/repo/prefix/../tmp/e5/models/hub"):
            mount = {"Type": "bind", "Source": source, "Destination": "/models/huggingface/hub", "RW": False}
            with self.subTest(source=source):
                self.assertTrue(guard.old_execution_mount(mount, self.reservation))
                self.assertTrue(guard.references_old_execution(
                    f'docker run -v "{source}:/models/huggingface/hub:ro" image', self.reservation))

    def test_undeclared_or_traversing_context_alias_is_not_redacted(self):
        for executable in self.COMPOSE_EXECUTABLES:
            for root in ("/unexpected/tmp/e7/tasks/development/opaque-public/environment",
                         "/repo/prefix/../tmp/e7/tasks/development/opaque-public/environment",
                         "/repo/tmp/e8/../e7/tasks/development/opaque-public/environment"):
                self.assertTrue(guard.references_old_execution(
                    self.compose(executable, context=root), self.reservation))
        self.assertTrue(guard.references_old_execution(
            'docker build "/repo/tmp/e8/../e7/tasks/development/opaque-public/environment"', self.reservation))
        self.assertTrue(guard.references_old_execution('docker compose --project-directory=/repo/tmp/e8/..', self.reservation))
        self.assertTrue(guard.references_old_execution('docker compose --file', self.reservation))
        self.assertTrue(guard.references_old_execution('docker compose --file "unterminated', self.reservation))

    def test_missing_relative_or_traversing_repository_roots_fail_closed(self):
        for roots in (None, [], ["repo"], ["/repo/../elsewhere"]):
            reservation = dict(self.reservation, repositoryRoots=roots)
            with self.assertRaisesRegex(ValueError, "repositoryRoots"):
                guard.old_execution_mount(self.mount("tmp/e7"), reservation)

    def test_duplicate_and_alias_mount_fields_are_not_accepted(self):
        mount = "type=bind,src=/repo/tmp/e5/models/hub,dst=/models/huggingface/hub,readonly"
        for extra in (",readonly=false,readonly", ",source=/repo/tmp/e7", ",target=/workspace"):
            self.assertTrue(guard.references_old_execution("docker run --mount " + mount + extra + " image", self.reservation))
        for declaration in ("type=bind,src=/repo,source=/repo,dst=/workspace,readonly",
                            "type=bind,src=/repo,src=/repo,dst=/workspace,readonly"):
            self.assertTrue(guard.references_old_execution("docker run --mount " + declaration + " image", self.reservation))
