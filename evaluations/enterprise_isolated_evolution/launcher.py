"""Start one inspected isolated planner and enforce permanent termination."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import uuid

from .authority import ExclusiveAuthority, Journal, safe_path
from .broker import Broker
from .container_policy import checked_config
from .files import REPO, host, inventory, parse_json, posix, read, sha, write
from .native_adapter import HarborAdapter
from .planner import ProtocolError, digest, exact
from .sandbox_runtime import container_options


def docker(*arguments: str) -> str:
    """Use argv-only local Docker access; keep daemon details out of output."""
    result = subprocess.run(["wsl", "-d", "Ubuntu", "--", "docker", *arguments], capture_output=True, timeout=45, check=False)
    if result.returncode:
        raise ProtocolError("Docker control operation failed: " + arguments[0])
    return result.stdout.decode("utf-8").strip()


class IsolatedPlanner:
    """Attach inherited stdio to one fixed, inspected, unprivileged container."""

    def __init__(self, work: Path, contract: dict):
        self.work, self.contract = work, contract
        self.container = None
        self.process = None
        self.stderr = None
        self.terminated = False

    def start(self) -> dict:
        """Inspect all created options before starting the frozen entrypoint."""
        image = json.loads(docker("image", "inspect", self.contract["optimizer_image"]))[0]
        if image["Id"] != self.contract["optimizer_image"] or image["Architecture"] != "amd64" or image["Os"] != "linux":
            raise ProtocolError("Optimizer image or architecture drift")
        source = host(self.contract["optimizer_code"])
        if inventory(source)[0] != self.contract["optimizer_code_sha256"]:
            raise ProtocolError("Frozen optimizer code drift")
        command = ["-I", "-B", "/opt/optimizer/bootstrap.py"]
        self.container = docker("create", "--interactive", "--name", "enterprise-e16-optimizer-" + uuid.uuid4().hex[:12],
            *container_options(), "--mount", "type=bind,src=" + posix(source) + ",dst=/opt/optimizer,readonly,bind-recursive=disabled",
            image["Id"], *command)
        if not re.fullmatch(r"[a-f0-9]{64}", self.container):
            raise ProtocolError("Invalid created container identity")
        state = json.loads(docker("inspect", self.container))[0]
        expected_env = dict(item.split("=", 1) for item in image["Config"]["Env"])
        expected_env["HOME"] = "/nonexistent"
        checked = checked_config(state, image["Id"], {"/opt/optimizer": posix(source)}, expected_env, command, stdin_open=True)
        write(self.work / "optimizer-created.json", {"inspection": state, "checked": checked})
        self.stderr = (self.work / "optimizer-stderr.log").open("xb")
        self.process = subprocess.Popen(["wsl", "-d", "Ubuntu", "--", "docker", "start", "--attach", "--interactive", self.container],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.stderr)
        ready = self.receive()
        exact(ready, {"schema", "lock"}, "optimizer ready")
        if (ready["schema"] != "enterprise-optimizer-ready/1.0" or ready["lock"]["uid"] != 65534
                or ready["lock"]["gid"] != 65534 or ready["lock"]["kernel_status"]["NoNewPrivs"] != "1"
                or ready["lock"]["kernel_status"]["Seccomp"] != "2"):
            raise ProtocolError("Optimizer failed irreversible process lockdown")
        write(self.work / "optimizer-ready.json", ready)
        return ready

    def send(self, value: dict) -> None:
        """Write one bounded public-development packet to a live planner."""
        if self.terminated or self.process is None or self.process.poll() is not None:
            raise ProtocolError("Optimizer input is permanently closed")
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n"
        if len(payload) > 2_000_000:
            raise ProtocolError("Oversized optimizer input")
        self.process.stdin.write(payload)
        self.process.stdin.flush()

    def receive(self) -> dict:
        """Read one closed JSON packet without executing its contents."""
        line = self.process.stdout.readline(2_000_001)
        if not line or len(line) > 2_000_000 or not line.endswith(b"\n"):
            raise ProtocolError("Optimizer exited or emitted an invalid packet")
        return parse_json(line)

    def finish(self) -> int:
        """Close input, verify exit and remove the exact nonrestartable container."""
        self.process.stdin.close()
        self.terminated = True
        code = self.process.wait(timeout=30)
        if self.process.stdout.read(1):
            raise ProtocolError("Optimizer emitted additional output after selection")
        state = json.loads(docker("inspect", self.container))[0]["State"]
        if code != 0 or state["Running"] or state["ExitCode"] != 0 or state["Pid"] != 0:
            raise ProtocolError("Optimizer did not terminate cleanly")
        write(self.work / "optimizer-exited.json", {"container_id": self.container, "state": state,
                                                   "stdin_closed": True, "restart_permitted": False})
        docker("rm", self.container)
        self.container = None
        return code

    def close(self) -> None:
        """Remove only this launcher's container on any terminal failure."""
        self.terminated = True
        if self.container is not None:
            docker("rm", "--force", self.container)
            self.container = None
        if self.process is not None:
            self.process.wait(timeout=30)
            for stream in (self.process.stdin, self.process.stdout):
                if stream is not None and not stream.closed:
                    stream.close()
        if self.stderr is not None:
            self.stderr.close()


def launch(work: Path) -> dict:
    """Execute the complete frozen campaign under one cross-process authority."""
    work = safe_path(work.absolute(), REPO)
    plan, contract = read(work / "plan.json"), read(work / "runtime-contract.json")
    if contract["plan_sha256"] != digest(plan):
        raise ProtocolError("Runtime contract is not bound to the exact public policy")
    with ExclusiveAuthority(REPO / "tmp/enterprise-next-preparation/enterprise-evolution-authority.lock", root=REPO) as authority:
        journal = Journal(work / "authority.jsonl", authority, root=REPO)
        adapter = HarborAdapter(work, plan, contract)
        broker = Broker(plan, journal, adapter)
        planner = IsolatedPlanner(work, contract)
        failed = False
        try:
            adapter.verify_admission("development")
            planner.start()
            journal.append("optimizer-started", {"plan_sha256": digest(plan), "contract_sha256": sha(work / "runtime-contract.json")})
            planner.send(plan)
            while True:
                packet = planner.receive()
                if packet.get("schema") == "enterprise-optimizer-selection/1.0":
                    broker.optimizer_exited(planner.finish(), packet)
                    return broker.finalize(packet)
                planner.send(broker.execute_batch(packet))
        except BaseException as error:
            failed = True
            if not journal.terminal:
                journal.append("terminal", {"status": "stopped", "reason": type(error).__name__, "retry_permitted": False})
            raise
        finally:
            try:
                planner.close()
            finally:
                journal.close()
            if failed:
                try:
                    adapter.stop_study()
                    write(work / "terminal-cleanup.json", {"study_closed": True, "optimizer_closed": True})
                except Exception as cleanup_error:
                    write(work / "terminal-cleanup.json", {"study_closed": False, "optimizer_closed": True,
                                                           "reason": type(cleanup_error).__name__})


def main() -> None:
    """Launch an independently registered and sealed current study."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path)
    args = parser.parse_args()
    result = launch(args.work)
    print(json.dumps({"status": "terminal", "decision": result["decision"]}))


if __name__ == "__main__":
    main()
