"""Inspect the actual optimizer container before releasing its input.

Adapted without policy changes from the independently tested E16 handoff.
"""
from __future__ import annotations

def checked_config(inspected: dict, image_id: str, mounts: dict[str, str],
                   expected_env: dict[str, str], expected_command: list[str],
                   stdin_open: bool = False) -> dict:
    """Reject unsafe creation options and return a source-bound safe projection."""
    host = inspected["HostConfig"]
    config = inspected["Config"]
    checks = {
        "image_digest": inspected["Image"] == image_id,
        "unprivileged_user": config["User"] == "65534:65534",
        "network_none": host["NetworkMode"] == "none",
        "ipc_none": host["IpcMode"] == "none",
        "pid_private": host["PidMode"] == "",
        "uts_private": host["UTSMode"] == "",
        "cgroup_private": host["CgroupnsMode"] == "private",
        "no_privilege": host["Privileged"] is False,
        "root_readonly": host["ReadonlyRootfs"] is True,
        "capabilities_dropped": host["CapDrop"] == ["ALL"] and not host["CapAdd"],
        "no_new_privileges": host["SecurityOpt"] == ["no-new-privileges=true"],
        "no_devices": not host["Devices"] and not host["DeviceRequests"],
        "no_volumes_from": not host["VolumesFrom"],
        "no_extra_hosts": not host["ExtraHosts"],
        "no_ports": not host["PortBindings"] and not config.get("ExposedPorts"),
        "no_log_archive": host["LogConfig"]["Type"] == "none",
        "single_python_entry": config["Entrypoint"] == ["/usr/local/bin/python"],
        "exact_command": config["Cmd"] == expected_command,
        "exact_stdin_policy": config["OpenStdin"] is stdin_open and config["Tty"] is False,
        "no_initialization_helper": not host.get("Init"),
        "no_published_ports": not host["PublishAllPorts"],
        "fixed_workdir": config["WorkingDir"] == "/work",
        "no_device_rules": not host.get("DeviceCgroupRules"),
        "no_extra_groups": not host.get("GroupAdd"),
        "no_healthcheck": not config.get("Healthcheck"),
        "no_restart": host["RestartPolicy"] == {"Name": "no", "MaximumRetryCount": 0},
        "fixed_resource_limits": host["Memory"] == 268435456
            and host["MemorySwap"] == 268435456 and host["NanoCpus"] == 1000000000
            and host["PidsLimit"] == 32,
    }
    realized = inspected["Mounts"]
    checks["exact_readonly_mounts"] = len(realized) == len(mounts) and all(
        mount["Type"] == "bind" and mount["Destination"] in mounts
        and mount["Source"] == mounts[mount["Destination"]]
        and mount["RW"] is False and mount["Propagation"] == "rprivate"
        for mount in realized
    )
    # Reject image-declared volumes, even if an operator omitted an explicit bind.
    checks["no_image_volumes"] = not config.get("Volumes")
    checks["exact_environment"] = len(config["Env"]) == len(expected_env) and {
        item.split("=", 1)[0]: item.split("=", 1)[1] for item in config["Env"]
    } == expected_env
    checks["exact_ephemeral_mounts"] = host["Tmpfs"] == {
        "/tmp": "rw,nosuid,nodev,noexec,size=16m,mode=700,uid=65534,gid=65534",
        "/work": "rw,nosuid,nodev,noexec,size=64m,mode=700,uid=65534,gid=65534",
    }
    bindings = host.get("Mounts", [])
    checks["no_recursive_mounts"] = len(bindings) == len(mounts) and all(
        mount.get("BindOptions", {}).get("NonRecursive") is True for mount in bindings)
    if not all(checks.values()):
        raise RuntimeError("Unsafe container configuration: "
                           + ", ".join(key for key, value in checks.items() if not value))
    return {"container_id": inspected["Id"], "image_id": inspected["Image"],
            "checks": checks, "environment_keys": sorted(
                entry.split("=", 1)[0] for entry in config["Env"]),
            "mount_destinations": sorted(mounts)}
