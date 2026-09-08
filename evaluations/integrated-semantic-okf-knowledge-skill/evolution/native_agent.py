"""Run one exact installed generator through native Harbor, without model calls."""
import json
import shlex

from harbor.agents.base import BaseAgent


class GeneratorAgent(BaseAgent):
    @staticmethod
    def name():
        return "knowledge-generator"

    def version(self):
        return "1.0.0"

    async def setup(self, environment):
        if not self.skills_dir:
            raise ValueError("Native skill staging is required")
        probe = "from pathlib import Path; import json,os; n=sorted(p.name for p in Path('/sys/class/net').iterdir()); ro=bool(os.statvfs('/dataset').f_flag & os.ST_RDONLY); print(json.dumps({'interfaces':n,'source_read_only':ro})); assert n==['lo'] and ro; assert not Path('/tests').exists()"
        result = await environment.exec(command=shlex.join(["python", "-B", "-c", probe]), timeout_sec=30)
        (self.logs_dir / "isolation.json").write_text(result.stdout or "", encoding="utf-8")
        if result.return_code:
            raise RuntimeError("Generator executor isolation probe failed")

    async def run(self, instruction, environment, context):
        request = json.loads(instruction)
        command = ["python", "-B", "/opt/generator-study/run_generator.py", "--skill",
                   self.skills_dir + "/build-semantic-okf-knowledge-skill",
                   "--request", json.dumps(request, ensure_ascii=False)]
        result = await environment.exec(command=shlex.join(command), timeout_sec=900)
        (self.logs_dir / "execution.txt").write_text((result.stdout or "") + (result.stderr or ""), encoding="utf-8")
        if result.return_code:
            raise RuntimeError("Native generator experiment transport failed")
        context.n_input_tokens = 0
        context.n_cache_tokens = 0
        context.n_output_tokens = 0
        context.cost_usd = 0.0
        context.metadata = {"execution_kind": "deterministic-generator-cli", "llm_calls": 0}
