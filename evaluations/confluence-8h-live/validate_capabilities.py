#!/usr/bin/env python3
"""Validate declarative evidence for the live Confluence capability campaign."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from types import ModuleType
from typing import Any
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


SCHEMA_VERSION = "1.0"
PASS = "pass"
FAIL = "fail"
MISSING = "missing"
PREREQUISITE = "prerequisite"
VALID_CHECK_STATUSES = {PASS, FAIL, MISSING, PREREQUISITE}

_CAMPAIGN_ARTIFACT_FIELDS = {
    "api_evidence",
    "api_report",
    "browser_evidence",
    "completion_report",
    "conflict_evidence",
    "evidence",
    "interaction_evidence",
    "inventory",
    "manifest",
    "upload_report",
}

_AC_URI = "urn:confluence-storage:ac"
_RI_URI = "urn:confluence-storage:ri"
_PREFIX_BY_URI = {_AC_URI: "ac", _RI_URI: "ri"}
_DIGEST_RE = re.compile(r"[0-9a-f]{64}")
_PAGE_ID_RE = re.compile(r"[1-9][0-9]*")


@lru_cache(maxsize=1)
def _roundtrip_module() -> ModuleType:
    """Load the authoritative skill implementation used by the live campaign."""

    script = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "roundtrip-confluence-pages"
        / "scripts"
        / "confluence_roundtrip.py"
    )
    spec = importlib.util.spec_from_file_location("confluence_live_roundtrip_contract", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load round-trip contract from {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _parse_timestamp(value: Any, label: str) -> tuple[datetime | None, str | None]:
    """Parse a timezone-aware ISO timestamp without accepting placeholder text."""

    if not isinstance(value, str) or not value.strip():
        return None, f"{label} must be a non-empty ISO timestamp"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None, f"{label} must be a valid ISO timestamp"
    if parsed.tzinfo is None:
        return None, f"{label} must include a timezone"
    return parsed.astimezone(timezone.utc), None


def _nonempty_unique_strings(value: Any, label: str) -> tuple[list[str], list[str]]:
    """Return normalized strings and configuration issues for an ID list."""

    if not isinstance(value, list) or not value:
        return [], [f"{label} must be a non-empty array of strings"]
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return [], [f"{label} must be a non-empty array of strings"]
    normalized = [item.strip() for item in value]
    duplicates = sorted(name for name, count in Counter(normalized).items() if count > 1)
    if duplicates:
        return normalized, [f"{label} contains duplicate IDs: {', '.join(duplicates)}"]
    return normalized, []


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"cannot read valid JSON from {path}: {exc}"
    if not isinstance(value, dict):
        return None, f"expected a JSON object in {path}"
    return value, None


def _inside(base: Path, relative: str) -> tuple[Path | None, str | None]:
    if not isinstance(relative, str) or not relative.strip():
        return None, "artifact path must be a non-empty string"
    base = base.resolve()
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None, f"artifact path escapes its workspace: {relative!r}"
    return candidate, None


def _inside_from(boundary: Path, origin: Path, relative: str) -> tuple[Path | None, str | None]:
    if not isinstance(relative, str) or not relative.strip():
        return None, "artifact path must be a non-empty string"
    boundary = boundary.resolve()
    candidate = (origin.resolve() / relative).resolve()
    try:
        candidate.relative_to(boundary)
    except ValueError:
        return None, f"artifact path escapes its workspace: {relative!r}"
    return candidate, None


class _RenderedHTMLObservation(HTMLParser):
    """Collect semantic image alternative text from rendered HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.image_alternative_texts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "img":
            return
        attributes = {name.casefold(): value for name, value in attrs}
        alternative = attributes.get("alt")
        if isinstance(alternative, str) and alternative:
            self.image_alternative_texts.append(alternative)


def _rendered_html_observation(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, f"cannot read rendered HTML from {path}: {exc}"
    parser = _RenderedHTMLObservation()
    try:
        parser.feed(payload)
        parser.close()
    except Exception as exc:  # HTMLParser can surface malformed entity/handler errors.
        return None, f"cannot parse rendered HTML from {path}: {exc}"
    return {
        "image_alternative_texts": sorted(set(parser.image_alternative_texts)),
        "html": payload,
    }, None


def _adf_observation(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Derive capability evidence from the hashed remote ADF artifact."""

    payload, error = _read_json(path)
    if error or payload is None:
        return None, error or f"cannot read ADF evidence from {path}"
    if payload.get("type") != "doc":
        return None, f"ADF evidence in {path} must have top-level type 'doc'"
    version = payload.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version <= 0:
        return None, f"ADF evidence in {path} must have a positive integer version"
    if not isinstance(payload.get("content"), list):
        return None, f"ADF evidence in {path} must have a content array"

    nodes: Counter[str] = Counter()
    marks: Counter[str] = Counter()
    extensions: set[str] = set()
    urls: set[str] = set()
    media_ids: set[str] = set()
    image_alternative_texts: set[str] = set()

    def visit(value: Any, *, is_mark: bool = False) -> None:
        if isinstance(value, dict):
            node_type = value.get("type")
            if isinstance(node_type, str) and node_type:
                (marks if is_mark else nodes)[node_type] += 1
            attrs = value.get("attrs")
            if isinstance(attrs, dict):
                for key in ("extensionKey", "extensionType"):
                    extension = attrs.get(key)
                    if isinstance(extension, str) and extension:
                        extensions.add(extension)
                for key in ("href", "url"):
                    url = attrs.get(key)
                    if isinstance(url, str) and url:
                        urls.add(url)
                if node_type in {"media", "mediaInline"}:
                    media_id = attrs.get("id")
                    if isinstance(media_id, str) and media_id:
                        media_ids.add(media_id)
                    alternative = attrs.get("alt")
                    if isinstance(alternative, str) and alternative:
                        image_alternative_texts.add(alternative)
            for key, child in value.items():
                if key == "marks" and isinstance(child, list):
                    for item in child:
                        visit(item, is_mark=True)
                elif key != "attrs":
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child, is_mark=is_mark)

    visit(payload)
    return {
        "nodes": dict(sorted(nodes.items())),
        "marks": dict(sorted(marks.items())),
        "extensions": sorted(extensions),
        "urls": sorted(urls),
        "media_ids": sorted(media_ids),
        "image_alternative_texts": sorted(image_alternative_texts),
    }, None


def _evidence_inventory(
    report_path: Path,
    report: dict[str, Any],
    manifest: dict[str, Any],
) -> tuple[dict[str, Path], list[str]]:
    """Verify every API evidence record and require the operation-bound core set."""

    issues: list[str] = []
    evidence = report.get("evidence")
    if not isinstance(evidence, dict):
        return {}, ["API report evidence must be an object"]
    required = {"storage", "atlas_doc_format", "view", "restrictions"}
    if all(key in manifest for key in ("properties", "operations")):
        required.update({"properties", "operations"})
    missing = sorted(required - set(evidence))
    issues.extend(f"API report evidence is missing {name!r}" for name in missing)

    resolved: dict[str, Path] = {}
    for name, record in evidence.items():
        if not isinstance(name, str) or not name:
            issues.append("API report evidence names must be non-empty strings")
            continue
        if not isinstance(record, dict):
            issues.append(f"API report evidence {name!r} must be an object")
            continue
        relative = record.get("path")
        candidate, path_error = _inside(report_path.parent, relative)
        if path_error or candidate is None:
            issues.append(f"API report evidence {name!r} {path_error or 'cannot be resolved'}")
            continue
        digest = record.get("sha256")
        if not isinstance(digest, str) or _DIGEST_RE.fullmatch(digest) is None:
            issues.append(f"API report evidence {name!r} has an invalid SHA-256 digest")
            continue
        if not candidate.is_file():
            issues.append(f"API report evidence {name!r} file is missing")
            continue
        try:
            actual = _digest(candidate)
        except OSError as exc:
            issues.append(f"cannot hash API report evidence {name!r}: {exc}")
            continue
        if digest != actual:
            issues.append(f"API report evidence {name!r} digest mismatch")
            continue
        resolved[name] = candidate
    return resolved, issues


def _expanded_name(name: str) -> str:
    if not name.startswith("{"):
        return name
    uri, local = name[1:].split("}", 1)
    prefix = _PREFIX_BY_URI.get(uri)
    return f"{prefix}:{local}" if prefix else local


def _attribute(element: ET.Element, local_name: str) -> str | None:
    for name, value in element.attrib.items():
        if _expanded_name(name).split(":")[-1] == local_name:
            return value
    return None


def _storage_observation(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, f"cannot read storage XML from {path}: {exc}"
    wrapped = (
        f'<campaign-root xmlns:ac="{_AC_URI}" xmlns:ri="{_RI_URI}">'
        + raw.replace("&nbsp;", "&#160;")
        + "</campaign-root>"
    )
    try:
        root = ET.fromstring(wrapped)
    except ET.ParseError as exc:
        return None, f"invalid storage XML in {path}: {exc}"

    tags: Counter[str] = Counter()
    macros: Counter[str] = Counter()
    hrefs: list[str] = []
    page_references: list[str] = []
    attachment_references: list[str] = []
    image_alternative_texts: list[str] = []
    parameter_values: dict[str, list[str]] = {}
    for element in root.iter():
        tag = _expanded_name(element.tag)
        if tag == "campaign-root":
            continue
        tags[tag] += 1
        href = _attribute(element, "href")
        if href:
            hrefs.append(href)
        if tag == "ac:structured-macro":
            macro_name = _attribute(element, "name")
            if macro_name:
                macros[macro_name] += 1
        elif tag == "ac:parameter":
            parameter_name = _attribute(element, "name")
            if parameter_name:
                parameter_value = re.sub(r"\s+", " ", " ".join(element.itertext())).strip()
                parameter_values.setdefault(parameter_name, []).append(parameter_value)
        elif tag == "ri:page":
            title = _attribute(element, "content-title")
            if title:
                page_references.append(title)
        elif tag == "ri:attachment":
            filename = _attribute(element, "filename")
            if filename:
                attachment_references.append(filename)
        elif tag == "ac:image":
            alternative_text = _attribute(element, "alt")
            if alternative_text:
                image_alternative_texts.append(alternative_text)

    visible_text = re.sub(r"\s+", " ", " ".join(root.itertext())).strip()
    return {
        "tags": dict(sorted(tags.items())),
        "macros": dict(sorted(macros.items())),
        "hrefs": sorted(set(hrefs)),
        "page_references": sorted(set(page_references)),
        "attachment_references": sorted(set(attachment_references)),
        "image_alternative_texts": sorted(set(image_alternative_texts)),
        "parameter_counts": {
            name: len(values) for name, values in sorted(parameter_values.items())
        },
        "parameter_values": {
            name: sorted(set(values)) for name, values in sorted(parameter_values.items())
        },
        "visible_text": visible_text,
    }, None


def _check(stage: str, status: str, issues: list[str], **evidence: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"stage": stage, "status": status, "issues": issues}
    result.update(evidence)
    return result


def _missing_or_prerequisite(
    stage: str, path: Path, prerequisite_status: str | None
) -> dict[str, Any]:
    if prerequisite_status is not None and prerequisite_status != PASS:
        return _check(
            stage,
            PREREQUISITE,
            [f"{stage} evidence awaits a passing prerequisite"],
            artifact=str(path),
            prerequisite_status=prerequisite_status,
        )
    return _check(stage, MISSING, [f"required artifact is missing: {path}"], artifact=str(path))


def _minimum_mapping_issues(
    actual: Any, expected: Any, label: str
) -> list[str]:
    issues: list[str] = []
    if not isinstance(expected, dict):
        return [f"{label} expectation must be an object"]
    if not isinstance(actual, dict):
        return [f"{label} evidence must be an object"]
    for name, minimum in expected.items():
        if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 0:
            issues.append(f"{label}.{name} minimum must be a non-negative integer")
            continue
        value = actual.get(name, 0)
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            issues.append(f"{label}.{name} expected >= {minimum}, observed {value!r}")
    return issues


def _required_values_issues(actual: Any, expected: Any, label: str) -> list[str]:
    if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
        return [f"{label} expectation must be an array of strings"]
    if not isinstance(actual, list):
        return [f"{label} evidence must be an array"]
    available = {item for item in actual if isinstance(item, str)}
    return [f"{label} is missing {item!r}" for item in expected if item not in available]


def _required_parameter_values_issues(actual: Any, expected: Any) -> list[str]:
    """Require named storage parameters and specific normalized values."""

    if not isinstance(expected, dict):
        return ["parameter_values expectation must be an object"]
    if not isinstance(actual, dict):
        return ["parameter_values evidence must be an object"]
    issues: list[str] = []
    for name, required in expected.items():
        if not isinstance(name, str) or not isinstance(required, list) or not all(
            isinstance(value, str) for value in required
        ):
            issues.append(f"parameter_values.{name} must be an array of strings")
            continue
        available = actual.get(name, [])
        if not isinstance(available, list):
            issues.append(f"parameter_values.{name} evidence must be an array")
            continue
        issues.extend(
            f"parameter_values.{name} is missing {value!r}"
            for value in required
            if value not in available
        )
    return issues


def _identity_check(workspace: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Require a valid tenant/page/version manifest instead of treating it as optional."""

    path = workspace / "manifest.json"
    manifest, error = _read_json(path)
    if error or manifest is None:
        return {}, _check("identity", FAIL, [error or "manifest read failed"], artifact=str(path))
    issues: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        issues.append("manifest schema_version is unsupported")
    base_url = manifest.get("base_url")
    if not isinstance(base_url, str) or not base_url:
        issues.append("manifest base_url must be a non-empty HTTPS URL")
    else:
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
            issues.append("manifest base_url must be an absolute HTTPS tenant URL")
    page = manifest.get("page")
    if not isinstance(page, dict):
        issues.append("manifest page must be an object")
        page = {}
    page_id = page.get("page_id")
    if not isinstance(page_id, str) or _PAGE_ID_RE.fullmatch(page_id) is None:
        issues.append("manifest page.page_id must be a positive ASCII decimal string")
    version = page.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version <= 0:
        issues.append("manifest page.version must be a positive integer")
    operation_id = manifest.get("last_verified_operation_id")
    if not isinstance(operation_id, str) or not operation_id:
        issues.append("manifest last_verified_operation_id must be a non-empty string")
    desired_digest = manifest.get("last_verified_desired_state_sha256")
    if not isinstance(desired_digest, str) or _DIGEST_RE.fullmatch(desired_digest) is None:
        issues.append("manifest last_verified_desired_state_sha256 must be a SHA-256 digest")

    meta, meta_error = _read_json(workspace / "page.meta.json")
    if meta_error or meta is None:
        issues.append(meta_error or "page.meta.json cannot be read")
    else:
        for key in ("page_id", "title", "space_id", "parent_id"):
            if str(meta.get(key) or "") != str(page.get(key) or ""):
                issues.append(f"manifest page.{key} does not match page.meta.json")
    return manifest, _check(
        "identity",
        FAIL if issues else PASS,
        issues,
        artifact=str(path),
        page_id=page_id,
        remote_version=version,
        base_url=base_url,
    )


def _local_check(workspace: Path, config: dict[str, Any], storage_path: Path) -> dict[str, Any]:
    if not storage_path.is_file():
        return _missing_or_prerequisite("local", storage_path, None)
    observation, error = _storage_observation(storage_path)
    if error or observation is None:
        return _check("local", FAIL, [error or "storage observation failed"], artifact=str(storage_path))

    issues: list[str] = []
    issues.extend(_minimum_mapping_issues(observation["tags"], config.get("tags_min", {}), "tags"))
    issues.extend(
        _minimum_mapping_issues(observation["macros"], config.get("macros_min", {}), "macros")
    )
    issues.extend(
        _minimum_mapping_issues(
            observation["parameter_counts"], config.get("parameters_min", {}), "parameters"
        )
    )
    issues.extend(
        _required_parameter_values_issues(
            observation["parameter_values"], config.get("parameter_values", {})
        )
    )
    issues.extend(_required_values_issues(observation["hrefs"], config.get("hrefs", []), "hrefs"))
    issues.extend(
        _required_values_issues(
            observation["page_references"], config.get("page_references", []), "page_references"
        )
    )
    issues.extend(
        _required_values_issues(
            observation["attachment_references"],
            config.get("attachment_references", []),
            "attachment_references",
        )
    )
    issues.extend(
        _required_values_issues(
            observation["image_alternative_texts"],
            config.get("image_alternative_texts", []),
            "image_alternative_texts",
        )
    )
    markers = config.get("visible_markers", [])
    if not isinstance(markers, list) or not all(isinstance(marker, str) for marker in markers):
        issues.append("visible_markers expectation must be an array of strings")
    else:
        normalized = observation["visible_text"]
        for marker in markers:
            if re.sub(r"\s+", " ", marker).strip() not in normalized:
                issues.append(f"visible marker is missing: {marker!r}")

    attachment_files = config.get("attachment_files", [])
    if not isinstance(attachment_files, list) or not all(
        isinstance(filename, str) for filename in attachment_files
    ):
        issues.append("attachment_files expectation must be an array of strings")
    else:
        for filename in attachment_files:
            candidate, path_error = _inside(workspace, f"attachments/{filename}")
            if path_error:
                issues.append(path_error)
            elif candidate is None or not candidate.is_file():
                issues.append(f"referenced local attachment file is missing: {filename!r}")

    public_observation = {
        key: value for key, value in observation.items() if key != "visible_text"
    }
    public_observation["parameter_counts"] = [
        {"name": name, "count": count}
        for name, count in observation["parameter_counts"].items()
    ]
    public_observation["parameter_values"] = [
        {"name": name, "values": values}
        for name, values in observation["parameter_values"].items()
    ]
    return _check(
        "local",
        FAIL if issues else PASS,
        issues,
        artifact=str(storage_path),
        observation=public_observation,
    )


def _manifest_page_id(workspace: Path) -> str | None:
    manifest_path = workspace / "manifest.json"
    if not manifest_path.is_file():
        return None
    manifest, error = _read_json(manifest_path)
    if error or manifest is None:
        return None
    page = manifest.get("page")
    if not isinstance(page, dict) or page.get("page_id") is None:
        return None
    return str(page["page_id"])


def _workspace_manifest(workspace: Path) -> dict[str, Any]:
    manifest, error = _read_json(workspace / "manifest.json")
    return {} if error or manifest is None else manifest


def _api_check(
    workspace: Path,
    config: dict[str, Any],
    report_path: Path,
    prerequisite_status: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    if not report_path.is_file():
        return _missing_or_prerequisite("api", report_path, prerequisite_status)
    report, error = _read_json(report_path)
    if error or report is None:
        return _check("api", FAIL, [error or "API report read failed"], artifact=str(report_path))

    issues: list[str] = []
    if report.get("schema_version") != SCHEMA_VERSION:
        issues.append("API report has an unsupported schema_version")
    _, timestamp_error = _parse_timestamp(report.get("verified_at"), "API report verified_at")
    if timestamp_error:
        issues.append(timestamp_error)
    expected_status = config.get("report_status", "verified")
    if report.get("status") != expected_status:
        issues.append(
            f"API report status expected {expected_status!r}, observed {report.get('status')!r}"
        )
    manifest_page = manifest.get("page") if isinstance(manifest.get("page"), dict) else {}
    page_id = str(manifest_page.get("page_id") or "")
    if str(report.get("page_id") or "") != page_id:
        issues.append(f"API report page_id does not match manifest page_id {page_id!r}")

    operation_id = report.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id:
        issues.append("API report operation_id must be a non-empty string")
    elif operation_id != manifest.get("last_verified_operation_id"):
        issues.append("API report operation_id does not match the manifest verification lock")
    desired_digest = report.get("desired_state_sha256")
    if not isinstance(desired_digest, str) or _DIGEST_RE.fullmatch(desired_digest) is None:
        issues.append("API report desired_state_sha256 must be a SHA-256 digest")
    elif desired_digest != manifest.get("last_verified_desired_state_sha256"):
        issues.append("API report desired_state_sha256 does not match the manifest verification lock")
    remote_version = report.get("remote_version")
    if not isinstance(remote_version, int) or isinstance(remote_version, bool) or remote_version <= 0:
        issues.append("API report remote_version must be a positive integer")
    elif remote_version != manifest_page.get("version"):
        issues.append("API report remote_version does not match manifest page.version")

    evidence_paths, evidence_issues = _evidence_inventory(report_path, report, manifest)
    issues.extend(evidence_issues)
    derived_adf: dict[str, Any] = {}
    adf_path = evidence_paths.get("atlas_doc_format")
    if adf_path is not None:
        observation, adf_error = _adf_observation(adf_path)
        if adf_error or observation is None:
            issues.append(adf_error or "ADF evidence observation failed")
        else:
            derived_adf = observation

    summary = report.get("adf_summary")
    if not isinstance(summary, dict):
        issues.append("API report adf_summary must be an object")
        summary = {}
    if derived_adf:
        for field in ("nodes", "marks", "extensions", "urls", "media_ids"):
            if summary.get(field) != derived_adf.get(field):
                issues.append(f"API report adf_summary.{field} does not match hashed ADF evidence")
        summary = derived_adf
    issues.extend(_minimum_mapping_issues(summary.get("nodes"), config.get("nodes_min", {}), "nodes"))
    issues.extend(_minimum_mapping_issues(summary.get("marks"), config.get("marks_min", {}), "marks"))
    issues.extend(_required_values_issues(summary.get("urls"), config.get("urls", []), "urls"))
    if "extensions" in config:
        issues.extend(
            _required_values_issues(summary.get("extensions"), config["extensions"], "extensions")
        )

    media_ids = summary.get("media_ids")
    if not isinstance(media_ids, list) or any(
        not isinstance(media_id, str) or not media_id for media_id in media_ids
    ):
        issues.append("adf_summary.media_ids must be an array")
        media_count = -1
    else:
        media_count = len(set(media_ids))
    media_min = config.get("media_min", 0)
    if not isinstance(media_min, int) or isinstance(media_min, bool) or media_min < 0:
        issues.append("media_min must be a non-negative integer")
    elif media_count < media_min:
        issues.append(f"media count expected >= {media_min}, observed {media_count}")
    if "media_exact" in config:
        media_exact = config["media_exact"]
        if not isinstance(media_exact, int) or isinstance(media_exact, bool) or media_exact < 0:
            issues.append("media_exact must be a non-negative integer")
        elif media_count != media_exact:
            issues.append(f"media count expected exactly {media_exact}, observed {media_count}")

    if "adf_image_alternative_texts" in config:
        issues.extend(
            _required_values_issues(
                summary.get("image_alternative_texts"),
                config["adf_image_alternative_texts"],
                "adf_image_alternative_texts",
            )
        )

    if "view_contains" in config or "view_image_alternative_texts" in config:
        view_markers = config.get("view_contains", [])
        if not isinstance(view_markers, list) or not all(
            isinstance(marker, str) for marker in view_markers
        ):
            issues.append("view_contains expectation must be an array of strings")
        else:
            view_path = evidence_paths.get("view")
            if view_path is None:
                issues.append("API report has no rendered-view evidence record")
            else:
                rendered, rendered_error = _rendered_html_observation(view_path)
                if rendered_error or rendered is None:
                    issues.append(rendered_error or "rendered-view evidence cannot be parsed")
                else:
                    for marker in view_markers:
                        alt_match = re.fullmatch(r'alt="([^"]+)"', marker)
                        if alt_match:
                            if alt_match.group(1) not in rendered["image_alternative_texts"]:
                                issues.append(f"rendered-view image alt is missing {alt_match.group(1)!r}")
                        elif marker not in rendered["html"]:
                            issues.append(f"rendered-view evidence is missing {marker!r}")
                    issues.extend(
                        _required_values_issues(
                            rendered["image_alternative_texts"],
                            config.get("view_image_alternative_texts", []),
                            "view_image_alternative_texts",
                        )
                    )

    checks = report.get("checks")
    checks_by_name: dict[str, list[dict[str, Any]]] = {}
    if isinstance(checks, list):
        for item in checks:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                checks_by_name.setdefault(item["name"], []).append(item)
    required_checks, required_check_issues = _nonempty_unique_strings(
        config.get("required_checks"), "required_checks"
    )
    if required_check_issues:
        issues.extend(required_check_issues)
    else:
        for name in required_checks:
            matches = checks_by_name.get(name, [])
            if not matches:
                issues.append(f"API check is missing: {name!r}")
            elif len(matches) != 1:
                issues.append(f"API check appears more than once: {name!r}")
            elif matches[0].get("passed") is not True:
                issues.append(f"API check did not pass: {name!r}")

    return _check(
        "api",
        FAIL if issues else PASS,
        issues,
        artifact=str(report_path),
        remote_version=remote_version,
        media_count=media_count,
    )


def _noop_check(
    path: Path,
    prerequisite_status: str,
    manifest: dict[str, Any],
    report_path: Path,
) -> dict[str, Any]:
    if not path.is_file():
        return _missing_or_prerequisite("noop", path, prerequisite_status)
    artifact, error = _read_json(path)
    if error or artifact is None:
        return _check("noop", FAIL, [error or "dry-run artifact read failed"], artifact=str(path))
    issues: list[str] = []
    if artifact.get("status") != "dry-run":
        issues.append(f"dry-run status expected 'dry-run', observed {artifact.get('status')!r}")
    plan = artifact.get("plan")
    if not isinstance(plan, dict):
        issues.append("dry-run plan must be an object")
        plan = {}
    for field in ("page_update", "body_changed", "metadata_changed"):
        if plan.get(field) is not False:
            issues.append(f"dry-run plan.{field} must be false, observed {plan.get(field)!r}")
    if plan.get("attachments") != []:
        issues.append(f"dry-run plan.attachments must be empty, observed {plan.get('attachments')!r}")
    labels = plan.get("labels")
    if not isinstance(labels, dict):
        issues.append("dry-run plan.labels must be an object")
    else:
        for field in ("added", "removed"):
            if labels.get(field) != []:
                issues.append(
                    f"dry-run plan.labels.{field} must be empty, observed {labels.get(field)!r}"
                )
    if plan.get("content_state_changed") is not False:
        issues.append(
            "dry-run plan.content_state_changed must be false, observed "
            f"{plan.get('content_state_changed')!r}"
        )
    if plan.get("no_op") is not True:
        issues.append(f"dry-run plan.no_op must be true, observed {plan.get('no_op')!r}")
    report, report_error = _read_json(report_path)
    if report_error or report is None:
        issues.append(report_error or "dry-run cannot bind its API report")
        report = {}
    manifest_page = manifest.get("page") if isinstance(manifest.get("page"), dict) else {}
    expected_page_id = str(manifest_page.get("page_id") or "")
    if str(plan.get("page_id") or "") != expected_page_id:
        issues.append("dry-run plan.page_id does not match the manifest page")
    expected_version = report.get("remote_version")
    for field in ("current_version", "expected_version"):
        value = plan.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            issues.append(f"dry-run plan.{field} must be a positive integer")
        elif value != expected_version or value != manifest_page.get("version"):
            issues.append(f"dry-run plan.{field} does not match the verified remote version")
    desired_digest = plan.get("desired_state_sha256")
    if not isinstance(desired_digest, str) or _DIGEST_RE.fullmatch(desired_digest) is None:
        issues.append("dry-run plan.desired_state_sha256 must be a SHA-256 digest")
    elif desired_digest != report.get("desired_state_sha256") or desired_digest != manifest.get(
        "last_verified_desired_state_sha256"
    ):
        issues.append("dry-run plan.desired_state_sha256 does not match verified state")
    return _check("noop", FAIL if issues else PASS, issues, artifact=str(path))


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _browser_interaction_issues(
    workspace: Path,
    browser_path: Path,
    browser: dict[str, Any],
    api: dict[str, Any],
    config: dict[str, Any],
) -> list[str]:
    """Validate optional detailed browser observations bound to browser GT."""

    evidence_name = config.get("interaction_evidence")
    required = config.get("required_interaction_ids")
    if evidence_name is None and required is None:
        return []
    issues: list[str] = []
    if not isinstance(evidence_name, str) or not evidence_name.strip():
        return ["interaction_evidence must be a non-empty workspace-relative path"]
    required, id_issues = _nonempty_unique_strings(required, "required_interaction_ids")
    if id_issues:
        return id_issues
    expectations = config.get("interaction_expectations")
    if not isinstance(expectations, dict):
        return ["interaction_expectations must be an object keyed by required interaction ID"]
    missing_expectations = sorted(set(required) - set(expectations))
    if missing_expectations:
        return [
            "interaction_expectations is missing: " + ", ".join(missing_expectations)
        ]
    interaction_path, path_error = _inside(workspace, evidence_name)
    if path_error or interaction_path is None:
        return [f"browser interaction evidence {path_error or 'cannot be resolved'}"]
    if not interaction_path.is_file():
        return ["browser interaction evidence file is missing"]
    evidence, error = _read_json(interaction_path)
    if error or evidence is None:
        return [error or "browser interaction evidence cannot be read"]
    if evidence.get("schema_version") != SCHEMA_VERSION:
        issues.append("browser interaction evidence has an unsupported schema_version")
    if evidence.get("status") != "verified":
        issues.append("browser interaction evidence status must be 'verified'")
    if str(evidence.get("page_id") or "") != str(browser.get("page_id") or ""):
        issues.append("browser interaction evidence page_id does not match browser GT")
    if evidence.get("operation_id") != browser.get("operation_id"):
        issues.append("browser interaction evidence operation_id does not match browser GT")
    if evidence.get("browser_gt_sha256") != _digest(browser_path):
        issues.append("browser interaction evidence does not bind the current browser GT")
    observed_at, observed_error = _parse_timestamp(
        evidence.get("observed_at"), "browser interaction observed_at"
    )
    if observed_error:
        issues.append(observed_error)
    api_at, api_error = _parse_timestamp(api.get("verified_at"), "API report verified_at")
    browser_at, browser_error = _parse_timestamp(
        browser.get("verified_at"), "browser GT verified_at"
    )
    if api_error:
        issues.append(api_error)
    if browser_error:
        issues.append(browser_error)
    if observed_at is not None and api_at is not None and observed_at < api_at:
        issues.append("browser interaction evidence predates API verification")
    if observed_at is not None and browser_at is not None and observed_at > browser_at:
        issues.append("browser interaction evidence postdates the browser GT it is meant to bind")

    final_screenshots = browser.get("final_screenshots")
    screenshot_bindings: set[tuple[str, str]] = set()
    if isinstance(final_screenshots, list):
        for record in final_screenshots:
            if not isinstance(record, dict):
                continue
            record_path = record.get("path")
            record_digest = record.get("sha256")
            if isinstance(record_path, str) and isinstance(record_digest, str):
                screenshot_bindings.add((record_path, record_digest))
    checks = evidence.get("checks")
    by_id: dict[str, list[dict[str, Any]]] = {}
    if isinstance(checks, list):
        for item in checks:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                by_id.setdefault(item["id"], []).append(item)
    else:
        issues.append("browser interaction evidence checks must be an array")
    for check_id in required:
        matches = by_id.get(check_id, [])
        if not matches:
            issues.append(f"browser interaction check is missing: {check_id!r}")
            continue
        if len(matches) != 1:
            issues.append(f"browser interaction check appears more than once: {check_id!r}")
            continue
        item = matches[0]
        if item.get("passed") is not True:
            issues.append(f"browser interaction check did not pass: {check_id!r}")
        for field in ("method", "assertion"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                issues.append(f"browser interaction check {check_id!r} requires {field}")
        if "actual" not in item:
            issues.append(f"browser interaction check {check_id!r} requires actual evidence")
        expectation = expectations.get(check_id)
        if not isinstance(expectation, dict):
            issues.append(f"browser interaction expectation {check_id!r} must be an object")
        else:
            expected_method = expectation.get("method")
            if not isinstance(expected_method, str) or not expected_method:
                issues.append(f"browser interaction expectation {check_id!r} requires method")
            elif item.get("method") != expected_method:
                issues.append(f"browser interaction check {check_id!r} method is unexpected")
            if "actual_equals" not in expectation:
                issues.append(
                    f"browser interaction expectation {check_id!r} requires actual_equals"
                )
            elif item.get("actual") != expectation.get("actual_equals"):
                issues.append(
                    f"browser interaction check {check_id!r} actual evidence is unexpected"
                )
        screenshot = item.get("screenshot")
        if not isinstance(screenshot, dict):
            issues.append(f"browser interaction check {check_id!r} requires a screenshot record")
            continue
        relative = screenshot.get("path")
        screenshot_path, screenshot_error = _inside_from(
            workspace, interaction_path.parent, relative
        )
        if screenshot_error or screenshot_path is None:
            issues.append(
                f"browser interaction check {check_id!r} screenshot "
                f"{screenshot_error or 'cannot be resolved'}"
            )
            continue
        if not screenshot_path.is_file():
            issues.append(f"browser interaction check {check_id!r} screenshot is missing")
            continue
        digest = screenshot.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            issues.append(f"browser interaction check {check_id!r} screenshot digest is invalid")
        elif digest != _digest(screenshot_path):
            issues.append(f"browser interaction check {check_id!r} screenshot digest mismatch")
        else:
            try:
                decodable = bool(_roundtrip_module().screenshot_is_decodable(screenshot_path.read_bytes()))
            except (OSError, RuntimeError) as exc:
                issues.append(
                    f"browser interaction check {check_id!r} screenshot cannot be decoded: {exc}"
                )
            else:
                if not decodable:
                    issues.append(
                        f"browser interaction check {check_id!r} screenshot is not a decodable PNG or JPEG"
                    )
        if (relative, digest) not in screenshot_bindings:
            issues.append(
                f"browser interaction check {check_id!r} screenshot is not bound by browser GT"
            )
    return issues


def _browser_check(
    workspace: Path,
    config: dict[str, Any],
    path: Path,
    api_report_path: Path,
    prerequisite_status: str,
) -> dict[str, Any]:
    if not path.is_file():
        return _missing_or_prerequisite("browser", path, prerequisite_status)
    artifact, error = _read_json(path)
    if error or artifact is None:
        return _check("browser", FAIL, [error or "browser GT read failed"], artifact=str(path))
    issues: list[str] = []
    if artifact.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            f"browser GT schema_version expected {SCHEMA_VERSION!r}, "
            f"observed {artifact.get('schema_version')!r}"
        )
    if artifact.get("status") != "verified":
        issues.append(f"browser GT status expected 'verified', observed {artifact.get('status')!r}")
    browser_at, browser_time_error = _parse_timestamp(
        artifact.get("verified_at"), "browser GT verified_at"
    )
    if browser_time_error:
        issues.append(browser_time_error)
    page_id = _manifest_page_id(workspace)
    if page_id is not None and str(artifact.get("page_id")) != page_id:
        issues.append(f"browser GT page_id does not match manifest page_id {page_id!r}")

    api, api_error = _read_json(api_report_path)
    if api_error or api is None:
        issues.append(api_error or "browser GT cannot read its API report prerequisite")
        api = {}
    api_at, api_time_error = _parse_timestamp(api.get("verified_at"), "API report verified_at")
    if api_time_error:
        issues.append(api_time_error)
    if browser_at is not None and api_at is not None and browser_at < api_at:
        issues.append("browser GT predates API verification")
    operation_id = artifact.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id:
        issues.append("browser GT operation_id must be a non-empty string")
    elif operation_id != api.get("operation_id"):
        issues.append("browser GT operation_id does not match the API report")
    expected_api_digest = _digest(api_report_path) if api_report_path.is_file() else ""
    if artifact.get("api_report_sha256") != expected_api_digest:
        issues.append("browser GT api_report_sha256 does not bind the current API report")
    if artifact.get("desired_state_sha256") != api.get("desired_state_sha256"):
        issues.append("browser GT desired_state_sha256 does not match the API report")
    try:
        browser_version = int(artifact.get("remote_version") or 0)
        api_version = int(api.get("remote_version") or 0)
    except (TypeError, ValueError):
        browser_version = api_version = 0
    if browser_version <= 0 or browser_version != api_version:
        issues.append("browser GT remote_version does not match the API report")

    page_url = artifact.get("page_url")
    if not isinstance(page_url, str) or not page_url:
        issues.append("browser GT page_url must be a non-empty string")
    else:
        parsed = urlparse(page_url)
        if parsed.scheme != "https" or not parsed.netloc:
            issues.append("browser GT page_url must be an absolute HTTPS URL")
        if page_id is not None and not re.search(
            rf"(?:^|/)pages/{re.escape(page_id)}(?:/|$)", parsed.path.rstrip("/")
        ):
            issues.append("browser GT page_url does not identify the workspace page_id")
        manifest = _workspace_manifest(workspace)
        base_url = manifest.get("base_url")
        if isinstance(base_url, str) and base_url:
            base = urlparse(base_url)
            if parsed.netloc.lower() != base.netloc.lower():
                issues.append("browser GT page_url belongs to a different tenant")

    checks = artifact.get("checks")
    by_id: dict[str, list[dict[str, Any]]] = {}
    if isinstance(checks, list):
        for item in checks:
            if not isinstance(item, dict):
                continue
            check_id = item.get("id", item.get("name"))
            if isinstance(check_id, str):
                by_id.setdefault(check_id, []).append(item)
    required, required_issues = _nonempty_unique_strings(
        config.get("required_check_ids"), "required_check_ids"
    )
    if required_issues:
        issues.extend(required_issues)
    else:
        for check_id in required:
            matches = by_id.get(check_id, [])
            if not matches:
                issues.append(f"browser GT check is missing: {check_id!r}")
            elif len(matches) != 1:
                issues.append(f"browser GT check appears more than once: {check_id!r}")
            elif matches[0].get("passed") is not True:
                issues.append(f"browser GT check did not pass: {check_id!r}")

    issues.extend(_browser_interaction_issues(workspace, path, artifact, api, config))

    screenshots = artifact.get("final_screenshots")
    if config.get("require_screenshots", True):
        baseline = artifact.get("baseline")
        if not isinstance(baseline, dict):
            issues.append("browser GT requires a baseline screenshot")
            baseline = None
        if not isinstance(screenshots, list) or not screenshots:
            issues.append("browser GT requires at least one final screenshot")
            screenshots = []
        records: list[tuple[str, dict[str, Any]]] = []
        if baseline is not None:
            records.append(("baseline", baseline))
        records.extend(
            (f"final_screenshots[{index}]", screenshot)
            for index, screenshot in enumerate(screenshots)
        )
        identities: list[tuple[str, str, str]] = []
        for label, screenshot in records:
            if not isinstance(screenshot, dict):
                issues.append(f"{label} must be an object")
                continue
            screenshot_path, path_error = _inside_from(
                path.parent, path.parent, screenshot.get("path", "")
            )
            if path_error:
                issues.append(f"{label} {path_error}")
                continue
            if screenshot_path is None or not screenshot_path.is_file():
                issues.append(f"{label} file is missing")
                continue
            expected_digest = screenshot.get("sha256")
            if not isinstance(expected_digest, str) or not re.fullmatch(
                r"[0-9a-f]{64}", expected_digest
            ):
                issues.append(f"{label}.sha256 must be a lowercase SHA-256 digest")
                continue
            actual_digest = _digest(screenshot_path)
            if actual_digest != expected_digest:
                issues.append(f"{label} digest mismatch")
                continue
            try:
                decodable = bool(
                    _roundtrip_module().screenshot_is_decodable(screenshot_path.read_bytes())
                )
            except (OSError, RuntimeError) as exc:
                issues.append(f"{label} cannot be decoded: {exc}")
                continue
            if not decodable:
                issues.append(f"{label} is not a decodable PNG or JPEG")
                continue
            identities.append((label, str(screenshot_path), actual_digest))
        baseline_identities = [identity for identity in identities if identity[0] == "baseline"]
        final_identities = [identity for identity in identities if identity[0] != "baseline"]
        if baseline_identities:
            _, baseline_path, baseline_digest = baseline_identities[0]
            if any(
                final_path == baseline_path or final_digest == baseline_digest
                for _, final_path, final_digest in final_identities
            ):
                issues.append("browser GT baseline and final screenshots must be distinct")

    return _check("browser", FAIL if issues else PASS, issues, artifact=str(path))


def _aggregate_status(checks: list[dict[str, Any]]) -> str:
    statuses = [check["status"] for check in checks]
    if FAIL in statuses:
        return FAIL
    if statuses and all(status == PASS for status in statuses):
        return PASS
    if MISSING in statuses:
        return MISSING
    return PREREQUISITE


def _campaign_artifact_references(progress: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Collect every file reference that campaign progress claims as evidence."""

    references: list[str] = []
    issues: list[str] = []

    def visit(value: Any, location: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_location = f"{location}.{key}" if location else key
                if location == "" and key == "evidence_bindings":
                    continue
                if key in _CAMPAIGN_ARTIFACT_FIELDS:
                    if not isinstance(child, str) or not child.strip():
                        issues.append(f"campaign progress {child_location} must be a file path")
                    else:
                        references.append(child)
                elif isinstance(child, (dict, list)):
                    visit(child, child_location)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                if isinstance(child, (dict, list)):
                    visit(child, f"{location}[{index}]")

    visit(progress, "")
    return sorted(set(references)), issues


def _campaign_completion_issues(root: Path, progress: dict[str, Any]) -> list[str]:
    """Derive declared completion counts and lineage from their bound reports."""

    issues: list[str] = []

    def load(relative: Any, label: str) -> dict[str, Any] | None:
        candidate, path_error = _inside(root, relative)
        if path_error or candidate is None:
            issues.append(f"campaign progress {label} {path_error or 'cannot be resolved'}")
            return None
        payload, read_error = _read_json(candidate)
        if read_error or payload is None:
            issues.append(f"campaign progress {label} {read_error or 'cannot be read'}")
            return None
        return payload

    for section_name, section in progress.items():
        if not isinstance(section, dict) or section_name == "evidence_bindings":
            continue
        completion_path = section.get("completion_report")
        if completion_path is not None:
            report = load(completion_path, f"{section_name}.completion_report")
            if report is not None:
                if report.get("status") != "verified":
                    issues.append(
                        f"campaign progress {section_name} completion report is not verified"
                    )
                rows = report.get("pages")
                totals = {"api_checks": 0, "browser_checks": 0, "screenshots": 0}
                report_page_ids: list[str] = []
                if not isinstance(rows, list) or not rows:
                    issues.append(
                        f"campaign progress {section_name} completion report has no pages"
                    )
                else:
                    for index, row in enumerate(rows):
                        if not isinstance(row, dict) or row.get("status") != "verified":
                            issues.append(
                                f"campaign progress {section_name} completion page {index} "
                                "is not verified"
                            )
                            continue
                        page_id = row.get("page_id")
                        if isinstance(page_id, str):
                            report_page_ids.append(page_id)
                        completion = row.get("completion")
                        if not isinstance(completion, dict) or completion.get("status") != "verified":
                            issues.append(
                                f"campaign progress {section_name} completion page {index} "
                                "has no verified completion"
                            )
                            continue
                        for field in totals:
                            value = completion.get(field)
                            if (
                                not isinstance(value, int)
                                or isinstance(value, bool)
                                or value < 0
                            ):
                                issues.append(
                                    f"campaign progress {section_name} completion page {index} "
                                    f"has invalid {field}"
                                )
                            else:
                                totals[field] += value
                declared_counts = section.get("completion")
                if not isinstance(declared_counts, dict):
                    declared_counts = section
                for field, expected in totals.items():
                    if declared_counts.get(field) != expected:
                        issues.append(
                            f"campaign progress {section_name}.{field} expected {expected}, "
                            f"observed {declared_counts.get(field)!r}"
                        )
                if (
                    "batch_id" in section
                    and "batch_id" in report
                    and section.get("batch_id") != report.get("batch_id")
                ):
                    issues.append(
                        f"campaign progress {section_name}.batch_id does not match completion report"
                    )
                if (
                    "dependency_order" in section
                    and section.get("dependency_order") != report.get("dependency_order")
                ):
                    issues.append(
                        f"campaign progress {section_name}.dependency_order does not match "
                        "completion report"
                    )
                if "page_ids" in section and section.get("page_ids") != report_page_ids:
                    issues.append(
                        f"campaign progress {section_name}.page_ids does not match completion report"
                    )

        manifest_path = section.get("manifest")
        if manifest_path is not None and "batch_id" in section:
            batch_manifest = load(manifest_path, f"{section_name}.manifest")
            if (
                batch_manifest is not None
                and section.get("batch_id") != batch_manifest.get("batch_id")
            ):
                issues.append(
                    f"campaign progress {section_name}.batch_id does not match batch manifest"
                )

        api_path = section.get("api_report")
        browser_path = section.get("browser_evidence")
        declared_counts = section.get("completion")
        if api_path is None or completion_path is not None:
            continue
        if not isinstance(declared_counts, dict):
            issues.append(
                f"campaign progress {section_name} requires completion counts for direct reports"
            )
            continue
        if api_path is None or browser_path is None:
            issues.append(
                f"campaign progress {section_name} requires both API and browser reports"
            )
            continue
        api = load(api_path, f"{section_name}.api_report")
        browser = load(browser_path, f"{section_name}.browser_evidence")
        if api is None or browser is None:
            continue
        api_checks = api.get("checks")
        if (
            api.get("status") != "verified"
            or not isinstance(api_checks, list)
            or any(not isinstance(check, dict) or check.get("passed") is not True for check in api_checks)
        ):
            issues.append(f"campaign progress {section_name} API report is not fully verified")
            api_count = 0
        else:
            api_count = len(api_checks)
        browser_checks = browser.get("checks")
        if (
            browser.get("status") != "verified"
            or not isinstance(browser_checks, list)
            or any(
                not isinstance(check, dict) or check.get("passed") is not True
                for check in browser_checks
            )
        ):
            issues.append(f"campaign progress {section_name} browser report is not fully verified")
            browser_count = 0
        else:
            browser_count = len(browser_checks)
        baseline_count = 1 if isinstance(browser.get("baseline"), dict) else 0
        final_screenshots = browser.get("final_screenshots")
        if not isinstance(final_screenshots, list):
            issues.append(
                f"campaign progress {section_name} browser final_screenshots must be an array"
            )
            screenshot_count = baseline_count
        else:
            screenshot_count = baseline_count + len(final_screenshots)
        for field, expected in {
            "api_checks": api_count,
            "browser_checks": browser_count,
            "screenshots": screenshot_count,
        }.items():
            if declared_counts.get(field) != expected:
                issues.append(
                    f"campaign progress {section_name}.completion.{field} expected {expected}, "
                    f"observed {declared_counts.get(field)!r}"
                )
        for field, report_field in (
            ("page_id", "page_id"),
            ("remote_version", "remote_version"),
            ("operation_id", "operation_id"),
        ):
            if field in section and section.get(field) != api.get(report_field):
                issues.append(
                    f"campaign progress {section_name}.{field} does not match API report"
                )
        for field in ("page_id", "remote_version", "operation_id"):
            if field in section and section.get(field) != browser.get(field):
                issues.append(
                    f"campaign progress {section_name}.{field} does not match browser report"
                )
    return issues


def _campaign_progress_check(
    root: Path,
    expectations: dict[str, Any],
    declared_workspaces: list[Any],
    counts: Counter[str],
    capabilities_complete: bool,
) -> dict[str, Any]:
    """Bind the campaign ledger to current workspaces and immutable evidence bytes."""

    configured_path = expectations.get("campaign_progress")
    if configured_path is None:
        return _check("campaign-progress", PASS, [], configured=False)
    path, path_error = _inside(root, configured_path)
    if path_error or path is None:
        return _check(
            "campaign-progress",
            FAIL,
            [path_error or "campaign progress path cannot be resolved"],
        )
    progress, read_error = _read_json(path)
    if read_error or progress is None:
        return _check(
            "campaign-progress",
            FAIL,
            [read_error or "campaign progress cannot be read"],
            artifact=str(path),
        )

    issues: list[str] = []
    if progress.get("schema_version") != SCHEMA_VERSION:
        issues.append("campaign progress schema_version is unsupported")
    if progress.get("campaign_id") != expectations.get("campaign_id"):
        issues.append("campaign progress campaign_id does not match expectations")
    campaign_status = progress.get("status")
    if campaign_status not in {"in-progress", "complete"}:
        issues.append("campaign progress status must be 'in-progress' or 'complete'")

    started_at, started_error = _parse_timestamp(
        progress.get("started_at"), "campaign progress started_at"
    )
    minimum_end_at, minimum_error = _parse_timestamp(
        progress.get("minimum_end_at"), "campaign progress minimum_end_at"
    )
    last_updated_at, updated_error = _parse_timestamp(
        progress.get("last_updated_at"), "campaign progress last_updated_at"
    )
    issues.extend(
        error for error in (started_error, minimum_error, updated_error) if error is not None
    )
    if started_at is not None and minimum_end_at is not None:
        if (minimum_end_at - started_at).total_seconds() < 8 * 60 * 60:
            issues.append("campaign progress minimum duration must be at least eight hours")
    if started_at is not None and last_updated_at is not None and last_updated_at < started_at:
        issues.append("campaign progress last_updated_at predates started_at")
    if (
        campaign_status == "complete"
        and minimum_end_at is not None
        and last_updated_at is not None
        and last_updated_at < minimum_end_at
    ):
        issues.append("campaign progress cannot be complete before minimum_end_at")
    if campaign_status == "complete" and not capabilities_complete:
        issues.append("campaign progress cannot be complete while capabilities are incomplete")

    expected_live_status = (
        "complete"
        if capabilities_complete
        else ("failed" if counts[FAIL] else "in-progress")
    )
    live_result = progress.get("live_capability_result")
    expected_live = {
        "status": expected_live_status,
        "passed": counts[PASS],
        "failed": counts[FAIL],
        "missing": counts[MISSING],
        "prerequisite": counts[PREREQUISITE],
    }
    if not isinstance(live_result, dict):
        issues.append("campaign progress live_capability_result must be an object")
    else:
        for field, expected in expected_live.items():
            if live_result.get(field) != expected:
                issues.append(
                    f"campaign progress live_capability_result.{field} expected "
                    f"{expected!r}, observed {live_result.get(field)!r}"
                )

    expected_pages: dict[str, dict[str, Any]] = {}
    tenant_values: set[str] = set()
    space_values: set[str] = set()
    latest_workspace_verification: datetime | None = None
    for workspace_config in declared_workspaces:
        if not isinstance(workspace_config, dict):
            continue
        workspace_id = workspace_config.get("id")
        workspace_relative = workspace_config.get("path")
        if not isinstance(workspace_id, str) or not workspace_id:
            continue
        workspace, workspace_error = _inside(root, workspace_relative)
        if workspace_error or workspace is None:
            issues.append(
                f"campaign progress workspace {workspace_id!r} cannot be resolved: "
                f"{workspace_error or 'invalid path'}"
            )
            continue
        manifest, manifest_error = _read_json(workspace / "manifest.json")
        if manifest_error or manifest is None:
            issues.append(
                f"campaign progress workspace {workspace_id!r} manifest is invalid: "
                f"{manifest_error or 'read failed'}"
            )
            continue
        page = manifest.get("page")
        if not isinstance(page, dict):
            issues.append(f"campaign progress workspace {workspace_id!r} manifest has no page")
            continue
        page_id = page.get("page_id")
        if not isinstance(page_id, str) or _PAGE_ID_RE.fullmatch(page_id) is None:
            issues.append(
                f"campaign progress workspace {workspace_id!r} manifest has invalid page_id"
            )
            continue
        if page_id in expected_pages:
            issues.append(f"campaign progress workspaces duplicate page_id {page_id!r}")
            continue
        expected_pages[page_id] = {
            "workspace": workspace_relative,
            "workspace_id": workspace_id,
            "title": page.get("title"),
            "remote_version": page.get("version"),
            "operation_id": manifest.get("last_verified_operation_id"),
        }
        base_url = manifest.get("base_url")
        if isinstance(base_url, str) and base_url:
            tenant_values.add(base_url.rstrip("/"))
        else:
            issues.append(f"campaign progress workspace {workspace_id!r} has no tenant URL")
        space_id = page.get("space_id")
        if isinstance(space_id, str) and space_id:
            space_values.add(space_id)
        else:
            issues.append(f"campaign progress workspace {workspace_id!r} has no space_id")
        verified_at, verified_error = _parse_timestamp(
            manifest.get("last_verified_at"),
            f"campaign progress workspace {workspace_id!r} last_verified_at",
        )
        if verified_error:
            issues.append(verified_error)
        elif verified_at is not None and (
            latest_workspace_verification is None or verified_at > latest_workspace_verification
        ):
            latest_workspace_verification = verified_at

    if len(tenant_values) != 1:
        issues.append("campaign progress workspaces must share exactly one tenant")
    else:
        tenant = next(iter(tenant_values))
        progress_tenant = progress.get("tenant")
        if not isinstance(progress_tenant, str) or progress_tenant.rstrip("/") != tenant:
            issues.append("campaign progress tenant does not match workspace manifests")
    if len(space_values) != 1:
        issues.append("campaign progress workspaces must share exactly one space")
    elif str(progress.get("space_id") or "") != next(iter(space_values)):
        issues.append("campaign progress space_id does not match workspace manifests")
    if (
        latest_workspace_verification is not None
        and last_updated_at is not None
        and last_updated_at < latest_workspace_verification
    ):
        issues.append("campaign progress last_updated_at predates workspace verification")

    progress_pages = progress.get("pages")
    observed_pages: dict[str, dict[str, Any]] = {}
    if not isinstance(progress_pages, list):
        issues.append("campaign progress pages must be an array")
    else:
        for index, item in enumerate(progress_pages):
            if not isinstance(item, dict):
                issues.append(f"campaign progress pages[{index}] must be an object")
                continue
            page_id = item.get("page_id")
            if not isinstance(page_id, str) or _PAGE_ID_RE.fullmatch(page_id) is None:
                issues.append(f"campaign progress pages[{index}].page_id is invalid")
                continue
            if page_id in observed_pages:
                issues.append(f"campaign progress pages duplicate page_id {page_id!r}")
                continue
            observed_pages[page_id] = item
    missing_pages = sorted(set(expected_pages) - set(observed_pages), key=int)
    extra_pages = sorted(set(observed_pages) - set(expected_pages), key=int)
    if missing_pages:
        issues.append("campaign progress pages are missing: " + ", ".join(missing_pages))
    if extra_pages:
        issues.append("campaign progress pages are undeclared: " + ", ".join(extra_pages))
    for page_id in sorted(set(expected_pages) & set(observed_pages), key=int):
        expected = expected_pages[page_id]
        observed = observed_pages[page_id]
        for field in ("workspace", "workspace_id", "title", "remote_version", "operation_id"):
            if observed.get(field) != expected[field]:
                issues.append(
                    f"campaign progress page {page_id} {field} expected "
                    f"{expected[field]!r}, observed {observed.get(field)!r}"
                )
        if observed.get("phase") != "verified":
            issues.append(f"campaign progress page {page_id} phase must be 'verified'")

    references, reference_issues = _campaign_artifact_references(progress)
    issues.extend(reference_issues)
    if not references:
        issues.append("campaign progress must reference at least one evidence artifact")
    bindings = progress.get("evidence_bindings")
    if not isinstance(bindings, dict):
        issues.append("campaign progress evidence_bindings must be an object")
        bindings = {}
    invalid_binding_keys = [
        key for key in bindings if not isinstance(key, str) or not key.strip()
    ]
    if invalid_binding_keys:
        issues.append("campaign progress evidence_bindings keys must be non-empty paths")
    valid_binding_keys = {key for key in bindings if isinstance(key, str) and key.strip()}
    missing_bindings = sorted(set(references) - valid_binding_keys)
    extra_bindings = sorted(valid_binding_keys - set(references))
    if missing_bindings:
        issues.append(
            "campaign progress evidence bindings are missing: " + ", ".join(missing_bindings)
        )
    if extra_bindings:
        issues.append(
            "campaign progress evidence bindings are unreferenced: " + ", ".join(extra_bindings)
        )
    for relative in references:
        candidate, evidence_error = _inside(root, relative)
        if evidence_error or candidate is None:
            issues.append(
                f"campaign progress evidence {relative!r} cannot be resolved: "
                f"{evidence_error or 'invalid path'}"
            )
            continue
        expected_digest = bindings.get(relative)
        if not isinstance(expected_digest, str) or _DIGEST_RE.fullmatch(expected_digest) is None:
            issues.append(f"campaign progress evidence {relative!r} has an invalid SHA-256 binding")
            continue
        if not candidate.is_file():
            issues.append(f"campaign progress evidence {relative!r} is not a file")
            continue
        try:
            actual_digest = _digest(candidate)
        except OSError as exc:
            issues.append(f"cannot hash campaign progress evidence {relative!r}: {exc}")
            continue
        if actual_digest != expected_digest:
            issues.append(f"campaign progress evidence {relative!r} digest mismatch")

    issues.extend(_campaign_completion_issues(root, progress))

    return _check(
        "campaign-progress",
        FAIL if issues else PASS,
        issues,
        artifact=str(path),
        evidence_references=references,
        page_ids=sorted(expected_pages, key=int),
    )


def _mutation_receipt_issues(
    workspace: Path,
    workspace_config: dict[str, Any],
    manifest: dict[str, Any],
    api_report_path: Path,
) -> list[str]:
    """Validate optional historical mutation evidence followed by final verification."""

    config = workspace_config.get("mutation_receipt")
    if config is None:
        return []
    if not isinstance(config, dict):
        return ["workspace mutation_receipt must be an object"]
    receipt_path, path_error = _inside(workspace, config.get("path"))
    if path_error or receipt_path is None:
        return [f"mutation receipt {path_error or 'cannot be resolved'}"]
    if not receipt_path.is_file():
        return ["mutation receipt file is missing"]
    receipt, error = _read_json(receipt_path)
    if error or receipt is None:
        return [error or "mutation receipt cannot be read"]
    api, api_error = _read_json(api_report_path)
    if api_error or api is None:
        return [api_error or "mutation receipt cannot bind final API report"]

    issues: list[str] = []
    allowed_statuses = config.get("allowed_statuses", ["uploaded"])
    if not isinstance(allowed_statuses, list) or not allowed_statuses or any(
        not isinstance(status, str) or not status for status in allowed_statuses
    ):
        issues.append("mutation_receipt.allowed_statuses must be a non-empty string array")
        allowed_statuses = []
    if receipt.get("status") not in allowed_statuses:
        issues.append(f"mutation receipt status is not accepted: {receipt.get('status')!r}")
    page = manifest.get("page") if isinstance(manifest.get("page"), dict) else {}
    page_id = str(page.get("page_id") or "")
    if str(receipt.get("page_id") or "") != page_id:
        issues.append("mutation receipt page_id does not match the workspace")
    receipt_operation = receipt.get("operation_id")
    if not isinstance(receipt_operation, str) or not receipt_operation:
        issues.append("mutation receipt operation_id must be a non-empty string")

    required_page_update = config.get("page_updated")
    if required_page_update is not None and receipt.get("page_updated") is not required_page_update:
        issues.append(
            f"mutation receipt page_updated expected {required_page_update!r}, "
            f"observed {receipt.get('page_updated')!r}"
        )
    attachments = receipt.get("attachments")
    by_filename: dict[str, list[dict[str, Any]]] = {}
    if isinstance(attachments, list):
        for item in attachments:
            if isinstance(item, dict) and isinstance(item.get("filename"), str):
                by_filename.setdefault(item["filename"], []).append(item)
    else:
        issues.append("mutation receipt attachments must be an array")
    required_actions = config.get("attachment_actions", {})
    if not isinstance(required_actions, dict):
        issues.append("mutation_receipt.attachment_actions must be an object")
    else:
        for filename, action in required_actions.items():
            matches = by_filename.get(filename, [])
            if len(matches) != 1 or matches[0].get("action") != action:
                issues.append(
                    f"mutation receipt does not prove attachment action {filename!r}: {action!r}"
                )

    preflight_config = config.get("remote_render_preflight")
    if preflight_config is not None:
        if not isinstance(preflight_config, dict):
            issues.append("mutation_receipt.remote_render_preflight must be an object")
        else:
            preflight = receipt.get("remote_render_preflight")
            if not isinstance(preflight, dict):
                issues.append("mutation receipt requires remote_render_preflight evidence")
                preflight = {}
            expected_preflight_status = preflight_config.get("status", "completed")
            if preflight.get("status") != expected_preflight_status:
                issues.append("mutation receipt remote_render_preflight status is unexpected")
            for field, minimum_key in (
                ("polls", "polls_min"),
                ("rendered_bytes", "rendered_bytes_min"),
            ):
                minimum = preflight_config.get(minimum_key, 1)
                value = preflight.get(field)
                if (
                    not isinstance(minimum, int)
                    or isinstance(minimum, bool)
                    or minimum < 1
                    or not isinstance(value, int)
                    or isinstance(value, bool)
                    or value < minimum
                ):
                    issues.append(
                        f"mutation receipt remote_render_preflight.{field} must be >= {minimum!r}"
                    )
            rendered_digest = preflight.get("rendered_sha256")
            if not isinstance(rendered_digest, str) or _DIGEST_RE.fullmatch(rendered_digest) is None:
                issues.append(
                    "mutation receipt remote_render_preflight.rendered_sha256 must be a SHA-256 digest"
                )

    nested = receipt.get("verification")
    if not isinstance(nested, dict):
        issues.append("mutation receipt requires a nested verification report")
        nested = {}
    if str(nested.get("page_id") or "") != page_id:
        issues.append("mutation receipt verification page_id does not match the workspace")
    if receipt_operation and nested.get("operation_id") != receipt_operation:
        issues.append("mutation receipt verification operation_id does not match the receipt")
    nested_status = nested.get("status")
    allow_failed = config.get("allow_reconciled_verification_failure") is True
    if nested_status != "verified" and not (allow_failed and nested_status == "failed"):
        issues.append(f"mutation receipt verification status is not accepted: {nested_status!r}")
    nested_version = nested.get("remote_version")
    final_version = api.get("remote_version")
    if not isinstance(nested_version, int) or isinstance(nested_version, bool) or nested_version <= 0:
        issues.append("mutation receipt verification remote_version must be positive")
    elif not isinstance(final_version, int) or nested_version > final_version:
        issues.append("mutation receipt verification version is newer than final API evidence")
    nested_at, nested_time_error = _parse_timestamp(
        nested.get("verified_at"), "mutation receipt verification verified_at"
    )
    final_at, final_time_error = _parse_timestamp(api.get("verified_at"), "final API verified_at")
    if nested_time_error:
        issues.append(nested_time_error)
    if final_time_error:
        issues.append(final_time_error)
    if nested_at is not None and final_at is not None and final_at < nested_at:
        issues.append("final API verification predates the mutation receipt")
    return issues


def _contract_check(
    workspace: Path,
    workspace_config: dict[str, Any],
    manifest: dict[str, Any],
    api_report_path: Path,
    prerequisite_status: str,
) -> dict[str, Any]:
    """Apply the authoritative skill completion gate plus mutation lineage."""

    if prerequisite_status != PASS:
        return _check(
            "contract",
            PREREQUISITE,
            ["operation-bound contract awaits passing evidence layers"],
            prerequisite_status=prerequisite_status,
        )
    issues: list[str] = []
    try:
        completion = _roundtrip_module().validate_completion_gate(workspace)
    except Exception as exc:  # Convert a contract-loader/runtime failure into evidence failure.
        completion = {"status": "failed", "errors": [str(exc)]}
    if completion.get("status") != "verified":
        raw_errors = completion.get("errors")
        if isinstance(raw_errors, list) and raw_errors:
            issues.extend(f"completion gate: {error}" for error in raw_errors)
        else:
            issues.append("authoritative completion gate did not verify the workspace")
    issues.extend(_mutation_receipt_issues(workspace, workspace_config, manifest, api_report_path))
    return _check(
        "contract",
        FAIL if issues else PASS,
        issues,
        completion=completion,
    )


def _capability_result(
    workspace: Path,
    workspace_config: dict[str, Any],
    capability: dict[str, Any],
) -> dict[str, Any]:
    artifacts = workspace_config.get("artifacts")
    if not isinstance(artifacts, dict):
        return {
            "id": capability.get("id"),
            "status": FAIL,
            "checks": [_check("configuration", FAIL, ["workspace artifacts must be an object"])],
        }

    resolved: dict[str, Path] = {}
    path_issues: list[str] = []
    for name, default in (
        ("storage", "page.storage.xml"),
        ("api_report", "verification/report.json"),
        ("noop_dry_run", "verification/noop-dry-run.json"),
        ("browser_gt", "verification/browser-ground-truth.json"),
    ):
        candidate, error = _inside(workspace, artifacts.get(name, default))
        if error or candidate is None:
            path_issues.append(f"{name}: {error or 'cannot resolve artifact'}")
        else:
            resolved[name] = candidate
    if path_issues:
        return {
            "id": capability.get("id"),
            "status": FAIL,
            "checks": [_check("configuration", FAIL, path_issues)],
        }

    local_config = capability.get("local", {})
    api_config = capability.get("api", {})
    browser_config = capability.get("browser", {})
    if not all(isinstance(item, dict) for item in (local_config, api_config, browser_config)):
        return {
            "id": capability.get("id"),
            "status": FAIL,
            "checks": [_check("configuration", FAIL, ["local, api, and browser must be objects"])],
        }
    browser_config = dict(browser_config)
    workspace_interaction_expectations = workspace_config.get("interaction_expectations")
    if workspace_interaction_expectations is not None:
        if "interaction_expectations" in browser_config:
            return {
                "id": capability.get("id"),
                "status": FAIL,
                "checks": [
                    _check(
                        "configuration",
                        FAIL,
                        [
                            "interaction_expectations must be declared at either workspace or capability level, not both"
                        ],
                    )
                ],
            }
        browser_config["interaction_expectations"] = workspace_interaction_expectations

    manifest, identity = _identity_check(workspace)
    local = _local_check(workspace, local_config, resolved["storage"])
    api = _api_check(
        workspace,
        api_config,
        resolved["api_report"],
        local["status"],
        manifest,
    )
    noop = _noop_check(
        resolved["noop_dry_run"],
        api["status"],
        manifest,
        resolved["api_report"],
    )
    browser = _browser_check(
        workspace,
        browser_config,
        resolved["browser_gt"],
        resolved["api_report"],
        api["status"],
    )
    primary_checks = [local, api, noop, browser, identity]
    contract = _contract_check(
        workspace,
        workspace_config,
        manifest,
        resolved["api_report"],
        _aggregate_status(primary_checks),
    )
    checks = [*primary_checks, contract]
    return {
        "id": capability.get("id"),
        "description": capability.get("description", ""),
        "status": _aggregate_status(checks),
        "checks": checks,
    }


def validate_capabilities(expectations_path: Path, campaign_root: Path | None = None) -> dict[str, Any]:
    """Validate every declared capability without treating missing in-progress evidence as complete."""

    expectations_path = expectations_path.resolve()
    expectations, error = _read_json(expectations_path)
    if error or expectations is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "failed",
            "campaign_complete": False,
            "errors": [error or "expectations read failed"],
            "workspaces": [],
        }
    errors: list[str] = []
    if expectations.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"expectations schema_version must be {SCHEMA_VERSION!r}, observed "
            f"{expectations.get('schema_version')!r}"
        )
    root = (campaign_root or expectations_path.parent).resolve()
    declared = expectations.get("workspaces")
    if not isinstance(declared, list) or not declared:
        errors.append("expectations.workspaces must be a non-empty array")
        declared = []

    workspace_results: list[dict[str, Any]] = []
    seen_workspace_ids: set[str] = set()
    seen_capability_ids: set[str] = set()
    for workspace_config in declared:
        if not isinstance(workspace_config, dict):
            errors.append("each workspace expectation must be an object")
            continue
        workspace_id = workspace_config.get("id")
        if not isinstance(workspace_id, str) or not workspace_id:
            errors.append("each workspace requires a non-empty string id")
            continue
        if workspace_id in seen_workspace_ids:
            errors.append(f"duplicate workspace id: {workspace_id!r}")
            continue
        seen_workspace_ids.add(workspace_id)
        workspace, path_error = _inside(root, workspace_config.get("path", ""))
        if path_error or workspace is None:
            errors.append(f"workspace {workspace_id!r}: {path_error or 'invalid path'}")
            continue
        capabilities = workspace_config.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            errors.append(f"workspace {workspace_id!r} capabilities must be a non-empty array")
            continue
        results: list[dict[str, Any]] = []
        for capability in capabilities:
            if (
                not isinstance(capability, dict)
                or not isinstance(capability.get("id"), str)
                or not capability["id"].strip()
            ):
                errors.append(
                    f"workspace {workspace_id!r} has a capability without a non-empty string id"
                )
                continue
            capability_id = capability["id"].strip()
            if capability_id in seen_capability_ids:
                errors.append(f"duplicate capability id across campaign: {capability_id!r}")
                continue
            seen_capability_ids.add(capability_id)
            results.append(_capability_result(workspace, workspace_config, capability))
        workspace_status = _aggregate_status(results) if results else FAIL
        workspace_results.append(
            {
                "id": workspace_id,
                "path": str(workspace),
                "status": workspace_status,
                "capabilities": results,
            }
        )

    capability_results = [
        capability
        for workspace in workspace_results
        for capability in workspace["capabilities"]
    ]
    counts = Counter(capability["status"] for capability in capability_results)
    for status in VALID_CHECK_STATUSES:
        counts.setdefault(status, 0)
    capabilities_complete = bool(capability_results) and not errors and all(
        capability["status"] == PASS for capability in capability_results
    )
    campaign_progress = _campaign_progress_check(
        root,
        expectations,
        declared,
        counts,
        capabilities_complete,
    )
    any_failed = bool(errors) or counts[FAIL] > 0 or campaign_progress["status"] == FAIL
    campaign_complete = capabilities_complete and campaign_progress["status"] == PASS
    status = "failed" if any_failed else ("complete" if campaign_complete else "in-progress")
    return {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": expectations.get("campaign_id"),
        "status": status,
        "campaign_complete": campaign_complete,
        "counts": {name: counts[name] for name in sorted(VALID_CHECK_STATUSES)},
        "errors": errors,
        "campaign_progress": campaign_progress,
        "workspaces": workspace_results,
    }


def _write_text_atomic(path: Path, payload: str) -> None:
    """Write UTF-8 text through a same-directory temporary file and atomic replace."""

    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    """Run the capability validator and emit a machine-readable report."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expectations",
        type=Path,
        default=Path(__file__).with_name("capability-expectations.json"),
        help="Declarative capability expectation file.",
    )
    parser.add_argument(
        "--campaign-root",
        type=Path,
        help="Override the root used to resolve workspace paths.",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return exit code 3 while valid campaign evidence is still in progress.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the same validation report to an atomic UTF-8 JSON artifact.",
    )
    args = parser.parse_args(argv)
    result = validate_capabilities(args.expectations, args.campaign_root)
    payload = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output is not None:
        _write_text_atomic(args.output, payload)
    sys.stdout.write(payload)
    if result["status"] == "failed":
        return 2
    if args.require_complete and not result["campaign_complete"]:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
