"""Prospectively isolate agent feedback in the pinned native Harbor executor.

This process-local wrapper changes one agent mount. It neither modifies the
installed package nor changes the verifier's own result mount or scoring.
Both public and private workers install these exact bytes before owner import.
"""
from __future__ import annotations

from importlib import metadata
import inspect
from pathlib import Path

from .files import host, sha
from .planner import ProtocolError

HARBOR_VERSION = "0.18.0"
TRIAL_SOURCE_SHA256 = "15a40691a5aa03152de4f6878347272503aaa3f976cf3eb22a1ec0e5d62609c9"
_MARKER = "_enterprise_e16_isolated_feedback_policy"


def compose_policy(*, verifier: bool) -> dict:
    """Keep large knowledge on a fresh disk volume, with narrowly writable tmpfs."""
    main = {"network_mode": "none", "cap_drop": ["ALL"],
            "security_opt": ["no-new-privileges:true"], "ipc": "none", "read_only": True,
            "pids_limit": 128, "logging": {"driver": "none"},
            "volumes": [{"type": "volume", "target": "/workspace", "volume": {"nocopy": True}}],
            "tmpfs": ["/tmp:rw,nosuid,nodev,mode=1777", "/root/.cache:rw,nosuid,nodev,mode=700",
                      "/harbor:rw,nosuid,nodev,mode=755"]}
    if verifier:
        main["volumes"].append({"type": "bind", "source": ".", "target": "/tests", "read_only": True})
        main["tmpfs"].append("/logs/artifacts:rw,nosuid,nodev,mode=755")
    return {"services": {"main": main}}


def _install_trial(trial_class, volume_class, binding: tuple[str, str]) -> None:
    """Install once, rejecting incompatible modes, mount drift and later patches."""
    installed = getattr(trial_class, _MARKER, None)
    if installed is not None:
        if (installed["binding"] != binding
                or trial_class._agent_env_mounts.fget is not installed["replacement"]
                or trial_class._verifier_env_mounts is not installed["verifier"]):
            raise ProtocolError("Harbor feedback isolation changed after installation")
        return
    original = trial_class._agent_env_mounts
    if not isinstance(original, property) or original.fget.__name__ != "_agent_env_mounts":
        raise ProtocolError("Unexpected native agent mount implementation")
    verifier = trial_class._verifier_env_mounts

    def isolated_agent_mounts(self):
        mode = self.task.config.verifier.environment_mode
        if (getattr(mode, "value", mode) != "separate" or self.task.config.steps
                or str(self.agent_env_paths.verifier_dir) != "/logs/verifier"):
            raise ProtocolError("Feedback isolation requires the declared separate verifier")
        mounts = original.fget(self)
        targets = [str(mount["target"]) for mount in mounts]
        if len(targets) != len(set(targets)) or targets.count("/logs/verifier") != 1:
            raise ProtocolError("Ambiguous native agent mounts")
        position = targets.index("/logs/verifier")
        inherited = mounts[position]
        expected = self.paths.verifier_dir.resolve().absolute().as_posix()
        if inherited.get("type") != "bind" or str(inherited.get("source")) != expected:
            raise ProtocolError("Unexpected inherited agent feedback mount")
        result = list(mounts)
        result[position] = volume_class(type="tmpfs", target="/logs/verifier")
        return result

    trial_class._agent_env_mounts = property(isolated_agent_mounts, doc=original.__doc__)
    setattr(trial_class, _MARKER, {"binding": binding, "replacement": isolated_agent_mounts, "verifier": verifier})


def install(contract: dict) -> None:
    """Verify frozen policy and installed native source, then isolate feedback."""
    source = host(contract["executor_policy"])
    checksum = contract["source_files"].get(contract["executor_policy"])
    if source.resolve() != Path(__file__).resolve() or checksum != sha(source):
        raise ProtocolError("Executor policy is not bound to this source")
    if (contract["harbor_trial_source_sha256"] != TRIAL_SOURCE_SHA256
            or metadata.version("harbor") != HARBOR_VERSION):
        raise ProtocolError("Native executor version is outside the frozen policy")
    from harbor.models.trial.config import ServiceVolumeConfig
    from harbor.trial.trial import Trial
    trial_source = inspect.getsourcefile(Trial)
    if trial_source is None or sha(Path(trial_source)) != TRIAL_SOURCE_SHA256:
        raise ProtocolError("Native executor source changed")
    _install_trial(Trial, ServiceVolumeConfig, (checksum, TRIAL_SOURCE_SHA256))
