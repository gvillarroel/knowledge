"""Harbor Pi adapter pinned to the Luna-capable Pi distribution."""

from __future__ import annotations

from typing import override

from harbor.agents.installed.node_install import nvm_node_install_snippet
from harbor.agents.installed.pi import Pi
from harbor.environments.base import BaseEnvironment


class PiLuna(Pi):
    """Install the Luna-capable Pi fork while preserving Harbor's Pi contract."""

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        await self.exec_as_root(
            environment,
            command="apt-get update && apt-get install -y curl",
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )
        version_spec = f"@{self._version}" if self._version else "@latest"
        await self.exec_as_agent(
            environment,
            command=(
                "set -euo pipefail; "
                f"{nvm_node_install_snippet()} && "
                "npm install -g "
                f"@earendil-works/pi-coding-agent{version_spec} && "
                "pi --version"
            ),
        )

