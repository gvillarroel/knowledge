"""Native Harbor adapter for deterministic skill construction/retrieval trials.

This agent uses no language model and never reads task solutions or verifier data.
Harbor owns skill staging, task/environment locks, execution, and result records.
"""
from __future__ import annotations

import json
import shlex
from pathlib import PurePosixPath

from harbor.agents.base import BaseAgent


class SkillRetrievalAgent(BaseAgent):
    @staticmethod
    def name() -> str:
        return "skill-retrieval"

    def version(self) -> str:
        return "1.0.0"

    async def setup(self, environment) -> None:
        if not self.skills_dir:
            raise ValueError("Harbor did not supply the staged skills directory")
        probe = "from pathlib import Path; import json; names=sorted(p.name for p in Path('/sys/class/net').iterdir()); print(json.dumps({'network_interfaces':names})); assert names == ['lo'], 'Agent must have only loopback networking'"
        result = await environment.exec(command=shlex.join(["python", "-B", "-c", probe]), timeout_sec=30)
        (self.logs_dir / "network-isolation.json").write_text(result.stdout or "", encoding="utf-8")
        if result.return_code != 0:
            raise RuntimeError("Agent container has an unexpected network interface")

    async def run(self, instruction, environment, context) -> None:
        request = json.loads(instruction)
        if set(request) != {"family", "instruction", "output_path"}:
            raise ValueError("Unexpected task instruction contract")
        output = PurePosixPath(request["output_path"])
        if not output.is_relative_to("/workspace") or ".." in output.parts or output.suffix != ".json":
            raise ValueError("Task output must be an explicit JSON artifact under /workspace")
        command = shlex.join([
            "python", "-B", "/opt/knowledge/evolution/runtime/bridge.py",
            "--skill", self.skills_dir + "/build-semantic-okf-knowledge-skill",
            "--family", request["family"],
            "--input", "/dataset", "--output", str(output),
        ])
        result = await environment.exec(command=command, timeout_sec=3600)
        (self.logs_dir / "execution.txt").write_text(
            (result.stdout or "") + "\n" + (result.stderr or ""), encoding="utf-8")
        if result.return_code != 0:
            raise RuntimeError(f"Skill runtime failed with exit code {result.return_code}")
        context.n_input_tokens = 0
        context.n_cache_tokens = 0
        context.n_output_tokens = 0
        context.cost_usd = 0.0
        context.metadata = {"execution_kind": "deterministic-skill-runtime", "llm_calls": 0}
