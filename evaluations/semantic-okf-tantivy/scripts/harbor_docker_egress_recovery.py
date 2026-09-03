"""Harbor Docker adapter pinned to the reviewed no-network sidecar repair."""

from __future__ import annotations

import asyncio
from typing import override

from harbor.environments.docker.docker import DockerEnvironment


RECOVERY_IMAGE = "knowledge-harbor-egress-control-recovery:v1"
EXPECTED_IMAGE_ID = (
    "sha256:e75be3125ea5ba876ec6f32ef6367b7b4a78dd15f912d8141cf42bf94a1def30"
)


class CompatibleDockerEnvironment(DockerEnvironment):
    """Use an immutable sidecar that supports this host's nftables kernel."""

    @override
    async def _ensure_egress_control_sidecar_image_built(self) -> None:
        process = await asyncio.create_subprocess_exec(
            "docker",
            "image",
            "inspect",
            "--format",
            "{{.Id}}",
            RECOVERY_IMAGE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        image_id = stdout.decode("utf-8", errors="strict").strip()
        if process.returncode != 0 or image_id != EXPECTED_IMAGE_ID:
            detail = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                "Reviewed Harbor egress-recovery image is absent or drifted: "
                f"expected={EXPECTED_IMAGE_ID!r}, actual={image_id!r}, "
                f"docker_error={detail!r}"
            )
        self._env_vars.egress_control_sidecar_image_name = RECOVERY_IMAGE
