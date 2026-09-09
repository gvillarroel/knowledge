"""Pure process/mount classification for prospectively reviewed Enterprise studies.

No process execution, inventory collection, reservation, scoring or admission is
performed here. A future study must bind this source and independently review
its caller. E8 keeps its original sealed classifier unchanged. Scope primitives
derive from that classifier (SHA-256
608535f5d9ca3788315d8885cde7352f1c5884749c3e003f642d4f64e2fa631e).
Both native Compose executable forms are recognized only at the command head;
text mentioning Docker inside another executable's arguments gets no exception.
The caller must bind absolute repositoryRoots, resolve filesystem aliases before
classification, and verify process ownership and current-study mounts separately.
"""
from __future__ import annotations

import re
import shlex

PHASES = {"preparation", "development", "recalculation", "validation"}


def docker_command_shape(command):
    """Identify a leading Docker CLI or native Compose plugin, never a mention."""
    value = normalize(command).strip()
    match = re.match(r"^(?:\"([^\"]+)\"|'([^']+)'|(\S+))(.*)$", value)
    if not match:
        return False, False, False
    executable = next(part for part in match.groups()[:3] if part is not None)
    executable = executable.rsplit("/", 1)[-1]
    arguments = match.group(4)
    cli = executable in {"docker", "docker.exe"}
    plugin = executable in {"docker-compose", "docker-compose.exe"}
    compose = plugin or (cli and bool(re.match(r"\s+compose(?:\s|$)", arguments)))
    build = cli and bool(re.match(r"\s+(?:build|buildx\s+build)(?:\s|$)", arguments))
    return cli or plugin, compose, build


def normalize(value):
    """Normalize command path separators, preserving token boundaries."""
    return re.sub(r"/+", "/", str(value).replace("\\", "/").lower())


def has_dot_components(value):
    """Reject noncanonical traversal before considering a path exception."""
    return bool(re.search(r"(?:^|/)\.{1,2}(?:/|$)", normalize(value)))


def declared_paths(reservation, declared):
    """Expand one relative declaration only under bound absolute host roots."""
    roots = reservation.get("repositoryRoots")
    if not isinstance(roots, list) or not roots or not all(
        isinstance(root, str) and bool(re.match(r"(?:/|[a-z]:/)", normalize(root)))
        and not has_dot_components(root) for root in roots
    ):
        raise ValueError("canonical absolute repositoryRoots are required")
    declared = normalize(declared)
    if not declared or declared.startswith("/") or ":" in declared or has_dot_components(declared):
        raise ValueError("declared source must be a canonical relative path")
    return [normalize(root).rstrip("/") + "/" + declared.rstrip("/") for root in roots]


def at_or_below(path, parent):
    """Compare path components, including filesystem and drive roots."""
    path, parent = normalize(path).rstrip("/"), normalize(parent).rstrip("/")
    return path == parent or path.startswith(parent + "/")


def exact_source(source, declared, reservation):
    """Match an exact declared source under a bound host root."""
    return not has_dot_components(source) and normalize(source).rstrip("/") in declared_paths(reservation, declared)


def under_source(source, declared, reservation):
    """Match a canonical descendant of a declared source under a bound root."""
    return not has_dot_components(source) and any(
        at_or_below(source, path) for path in declared_paths(reservation, declared))


def historical_reference(value, reservation):
    """Detect any remaining old work-root or executable entrypoint reference."""
    value = normalize(value)
    for root in reservation["historicalWorkRoots"]:
        if re.search(re.escape(normalize(root)) + r"(?=/|[\s\"',:]|$)", value):
            return True
    return any(normalize(path) in value for path in reservation["legacyDispatchEntrypoints"])


def verifier_identity(labels=None, command=""):
    """Require Harbor's separate-verifier project marker for test access."""
    labels = labels or {}
    project = str(labels.get("com.docker.compose.project", ""))
    return "__verifier__" in project or bool(re.search(
        r"(?:--project-name|-p|--name)(?:=|\s+)[\"']?[^\s\"']*__verifier__[^\s\"']*",
        normalize(command)))


def allowed_mount(mount, reservation, phase, *, labels=None, command=""):
    """Allow only exact declared RO test mounts or the scoped RO model cache."""
    if mount.get("RW") is not False or mount.get("Type") != "bind":
        return False
    source, target = mount.get("Source", ""), normalize(mount.get("Destination", ""))
    if has_dot_components(source) or has_dot_components(target):
        return False
    for entry in reservation["historicalReadOnlyMounts"]:
        if phase not in entry["phases"] or target != entry["target"]:
            continue
        if entry["purpose"] == "pinned-model-cache":
            if under_source(source, entry["path"], reservation):
                return True
        elif entry["purpose"] == "separate-verifier-tests":
            if exact_source(source, entry["path"], reservation) and verifier_identity(labels, command):
                return True
    return False


def parse_mount(declaration):
    """Parse only Docker's supported bind-mount command shapes for inspection."""
    raw = re.sub(r"^(?:--mount(?:=|\s+)|(?:-v|--volume)(?:=|\s+))", "", declaration)
    raw = raw.strip("\"'")
    if declaration.startswith("--mount"):
        fields = {}
        for part in raw.split(","):
            key, _, value = part.partition("=")
            if key in fields:
                return {"Type": "invalid", "Source": raw, "RW": True}
            fields[key] = value
        if any(sum(key in fields for key in aliases) > 1 for aliases in
               (("src", "source"), ("dst", "target", "destination"))):
            return {"Type": "invalid", "Source": raw, "RW": True}
        readonly = (fields.get("readonly") in {"", "true"} or fields.get("ro") in {"", "true"})
        readonly = readonly and fields.get("readonly") != "false" and fields.get("ro") != "false" and "rw" not in fields
        return {"Type": fields.get("type"), "Source": fields.get("src", fields.get("source", "")),
                "Destination": fields.get("dst", fields.get("target", fields.get("destination", ""))),
                "RW": not readonly}
    parts = raw.rsplit(":", 2)
    if len(parts) != 3:
        return {"Type": "bind", "Source": raw, "Destination": "", "RW": True}
    return {"Type": "bind", "Source": parts[0], "Destination": parts[1], "RW": parts[2] != "ro"}


def noncanonical_context(command, *, compose, build):
    """Reject traversal in recognized Docker input arguments before redaction."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return True
    if compose:
        flags = ("--file", "-f", "--project-directory")
        for index, token in enumerate(tokens):
            if token in flags:
                if index + 1 == len(tokens) or has_dot_components(tokens[index + 1]):
                    return True
            elif any(token.startswith(flag + "=") for flag in flags):
                if has_dot_components(token.partition("=")[2]):
                    return True
    return bool(build and tokens and has_dot_components(tokens[-1]))


def references_old_execution(command, reservation, phase="development"):
    """Recognize declared Docker input reads; reject all other old dispatch."""
    value = normalize(command)
    docker, compose, build = docker_command_shape(value)
    rejected_mount = False
    if docker:
        if noncanonical_context(value, compose=compose, build=build):
            return True
        original = value
        def redact_mount(match):
            nonlocal rejected_mount
            declaration = match.group(0)
            mount = parse_mount(declaration)
            rejected_mount |= old_execution_mount(mount, reservation, phase, command=original)
            return " declared-read-only-input " if allowed_mount(
                mount, reservation, phase, command=original) else declaration
        value = re.sub(r"(?:--mount[=\s]+|(?:-v|--volume)[=\s]+)(?:\"[^\"]*\"|'[^']*'|\S+)",
                       redact_mount, value)
        for entry in reservation["historicalDockerContexts"]:
            if phase not in entry["phases"]:
                continue
            if entry["role"] == "separate-verifier" and not verifier_identity(command=original):
                continue
            token = "(?:" + "|".join(re.escape(path) for path in declared_paths(reservation, entry["path"])) + ")"
            if compose:
                pattern = (r"(?P<prefix>(?:--file|-f)(?:=|\s+)[\"']?)"
                           + token + r"/docker-compose\.yaml(?=[\s\"']|$)")
                value = re.sub(pattern, r"\g<prefix>declared-read-only-compose", value)
                pattern = (r"(?P<prefix>--project-directory(?:=|\s+)[\"']?)"
                           + token + r"(?=[\s\"']|$)")
                value = re.sub(pattern, r"\g<prefix>declared-read-only-context", value)
            if build:
                pattern = r"(?<=[\s\"'])" + token + r"(?=[\s\"']*$)"
                value = re.sub(pattern, " declared-read-only-context ", value)
    return rejected_mount or historical_reference(value, reservation)


def old_execution_mount(mount, reservation, phase="development", labels=None, *, command=""):
    """Reject undeclared historical mounts, including a broader ancestor mount."""
    if mount.get("Type") == "invalid":
        return True
    historical = [path for root in reservation["historicalWorkRoots"]
                  for path in declared_paths(reservation, root)]
    source = mount.get("Source", "")
    if has_dot_components(source):
        return True
    if allowed_mount(mount, reservation, phase, labels=labels, command=command):
        return False
    if source and any(at_or_below(path, source) for path in historical):
        return True
    return historical_reference(source, reservation)
