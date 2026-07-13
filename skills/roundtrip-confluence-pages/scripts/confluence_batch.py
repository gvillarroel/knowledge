#!/usr/bin/env python3
"""Scan, explore, edit, and safely process batches of Confluence page workspaces."""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import ModuleType
from typing import Any
from urllib.parse import parse_qsl, quote, urljoin, urlparse
from xml.etree import ElementTree


BATCH_SCHEMA_VERSION = "1.0"
INVENTORY_KIND = "confluence-space-inventory"
MANIFEST_KIND = "confluence-page-batch"
INVENTORY_NAME = "space-inventory.json"
BATCH_MANIFEST_NAME = "batch-manifest.json"
BATCH_VALIDATE_REPORT_NAME = "batch-validation-report.json"
BATCH_PLAN_NAME = "batch-plan.json"
BATCH_UPLOAD_REPORT_NAME = "batch-upload-report.json"
BATCH_VERIFY_REPORT_NAME = "batch-verify-report.json"
BATCH_COMPLETION_REPORT_NAME = "batch-completion-report.json"


def _load_core() -> ModuleType:
    """Load the sibling standalone round-trip implementation."""

    path = Path(__file__).resolve().with_name("confluence_roundtrip.py")
    module_name = "roundtrip_confluence_pages_core_" + sha256(
        str(path).encode("utf-8")
    ).hexdigest()[:12]
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling round-trip script: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


core = _load_core()


def _is_rate_limited(error: BaseException | str) -> bool:
    return "HTTP 429" in str(error).upper()


def _file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _canonical_json_sha256(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def _is_link_like(path: Path) -> bool:
    """Return whether a path is a symbolic link or Windows junction."""

    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _absolute_unlinked_path(path: Path, field: str) -> Path:
    """Resolve a path only after rejecting link-like existing components."""

    candidate = path if path.is_absolute() else Path.cwd() / path
    current = Path(candidate.anchor)
    for part in candidate.parts[1:]:
        current /= part
        if _is_link_like(current):
            raise core.ValidationError(f"{field} must not traverse a symbolic link or junction: {current}")
    return candidate.resolve()


def _relative_file(root: Path, value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise core.ValidationError(f"{field} must be a non-empty relative path")
    relative = Path(value)
    if relative.is_absolute():
        raise core.ValidationError(f"{field} must be relative")
    if ".." in relative.parts:
        raise core.ValidationError(f"{field} must not contain parent traversal")
    candidate = root / relative
    current = root
    for part in relative.parts:
        current /= part
        if _is_link_like(current):
            raise core.ValidationError(
                f"{field} must not traverse a symbolic link or junction: {current}"
            )
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root):
        raise core.ValidationError(f"{field} escapes the batch directory")
    return resolved


def _validated_sha256(value: Any, field: str) -> str:
    """Return a lowercase SHA-256 digest or reject malformed evidence."""

    digest = str(value or "")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise core.ValidationError(f"{field} must be a lowercase SHA-256 digest")
    return digest


def _load_inventory(path: Path, *, require_complete: bool = False) -> dict[str, Any]:
    path = _absolute_unlinked_path(path, "inventory path")
    payload = core.load_json(path)
    if not isinstance(payload, dict) or payload.get("schema_version") != BATCH_SCHEMA_VERSION:
        raise core.ValidationError("inventory has an unsupported schema")
    if payload.get("kind") != INVENTORY_KIND:
        raise core.ValidationError("inventory has an unsupported kind")
    if require_complete and payload.get("status") != "verified":
        raise core.ValidationError("batch download requires a verified, complete inventory")
    pages = payload.get("pages")
    if not isinstance(pages, list):
        raise core.ValidationError("inventory pages must be an array")
    seen: set[str] = set()
    for item in pages:
        if not isinstance(item, dict) or not item.get("page_id"):
            raise core.ValidationError("inventory contains an invalid page record")
        page_id = core.validate_page_id(item["page_id"])
        if page_id in seen:
            raise core.ValidationError(f"inventory contains duplicate page ID: {page_id}")
        seen.add(page_id)
    return payload


def _load_inventory_snapshot(
    path: Path, *, require_complete: bool = False
) -> tuple[dict[str, Any], Path, str]:
    """Load one inventory whose bytes remain unchanged across parsing."""

    resolved = _absolute_unlinked_path(path, "inventory path")
    before = _file_sha256(resolved)
    payload = _load_inventory(resolved, require_complete=require_complete)
    after = _file_sha256(resolved)
    if before != after:
        raise core.ConflictError("inventory changed while it was being loaded")
    return payload, resolved, before


def _validate_workspace_identity(
    item: dict[str, Any], workspace: Path, *, base_url: str, space_id: str
) -> None:
    """Cross-check an existing workspace against its batch identity."""

    if not workspace.exists():
        return
    if not workspace.is_dir():
        raise core.ValidationError(f"batch workspace is not a directory: {workspace}")
    meta_path = workspace / core.META_NAME
    page_manifest_path = workspace / core.MANIFEST_NAME
    if not meta_path.is_file() or not page_manifest_path.is_file():
        return
    meta = core.load_json(meta_path)
    page_manifest = core.load_json(page_manifest_path)
    if not isinstance(meta, dict) or not isinstance(page_manifest, dict):
        raise core.ValidationError(f"batch workspace identity is invalid: {workspace}")
    page_record = page_manifest.get("page")
    if not isinstance(page_record, dict):
        raise core.ValidationError(f"batch workspace page manifest is invalid: {workspace}")
    item_page_id = core.validate_page_id(item.get("page_id"))
    workspace_page_id = core.validate_page_id(meta.get("page_id"))
    manifest_page_id = core.validate_page_id(page_record.get("page_id"))
    if item_page_id != workspace_page_id or workspace_page_id != manifest_page_id:
        raise core.ValidationError(
            f"batch page {item_page_id} does not match workspace page identity {workspace_page_id}"
        )
    workspace_base_url = core.normalize_base_url(str(page_manifest.get("base_url") or ""))
    if workspace_base_url != base_url:
        raise core.ValidationError(
            f"batch page {item_page_id} workspace belongs to a different Confluence tenant"
        )
    workspace_space_id = core.validate_page_id(meta.get("space_id"))
    manifest_space_id = core.validate_page_id(page_record.get("space_id"))
    if workspace_space_id != space_id or manifest_space_id != space_id:
        raise core.ValidationError(
            f"batch page {item_page_id} workspace belongs to space {workspace_space_id}, not {space_id}"
        )


def _load_batch_manifest(path: Path) -> tuple[dict[str, Any], Path, list[tuple[dict[str, Any], Path]]]:
    path = _absolute_unlinked_path(path, "batch manifest path")
    manifest = core.load_json(path)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != BATCH_SCHEMA_VERSION:
        raise core.ValidationError("batch manifest has an unsupported schema")
    if manifest.get("kind") != MANIFEST_KIND:
        raise core.ValidationError("batch manifest has an unsupported kind")
    base_url = core.normalize_base_url(str(manifest.get("base_url") or ""))
    space_id = core.validate_page_id(manifest.get("space_id"))
    inventory_digest = _validated_sha256(
        manifest.get("inventory_sha256"), "batch manifest inventory_sha256"
    )
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        raise core.ValidationError("batch manifest must contain at least one page")
    root = path.parent.resolve()
    records: list[tuple[dict[str, Any], Path]] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, item in enumerate(pages):
        if not isinstance(item, dict) or not item.get("page_id"):
            raise core.ValidationError(f"batch manifest page {index} is invalid")
        page_id = core.validate_page_id(item["page_id"])
        if page_id in seen_ids:
            raise core.ValidationError(f"batch manifest contains duplicate page ID: {page_id}")
        workspace = _relative_file(root, item.get("workspace"), f"pages[{index}].workspace")
        folded = str(workspace).casefold()
        if folded in seen_paths:
            raise core.ValidationError("batch manifest contains duplicate workspace paths")
        seen_ids.add(page_id)
        seen_paths.add(folded)
        _validate_workspace_identity(
            item, workspace, base_url=base_url, space_id=space_id
        )
        records.append((item, workspace))
    selection = manifest.get("selection")
    if selection is None:
        # Schema 1.0 manifests created before selection evidence was added
        # derive their pinned order from the original page records.
        selected_page_ids = [str(item["page_id"]) for item, _workspace in records]
    elif isinstance(selection, dict) and isinstance(selection.get("page_ids"), list):
        selected_page_ids = [core.validate_page_id(value) for value in selection["page_ids"]]
    else:
        raise core.ValidationError("batch manifest selection.page_ids must be an array")
    if len(selected_page_ids) != len(set(selected_page_ids)):
        raise core.ValidationError("batch manifest selection contains duplicate page IDs")
    if set(selected_page_ids) != seen_ids:
        raise core.ValidationError(
            "batch manifest page records do not match the pinned selection page set"
        )
    expected_batch_id = _canonical_json_sha256(
        {
            "base_url": base_url,
            "space_id": space_id,
            "page_ids": selected_page_ids,
            "inventory_sha256": inventory_digest,
        }
    )[:20]
    if manifest.get("batch_id") != expected_batch_id:
        raise core.ValidationError(
            "batch manifest identity fields do not match its batch_id"
        )
    _dependency_order(records, infer_storage=False)
    return manifest, root, records


def _load_batch_manifest_snapshot(
    path: Path,
) -> tuple[dict[str, Any], Path, list[tuple[dict[str, Any], Path]], str]:
    """Load one batch manifest whose bytes remain stable across parsing."""

    resolved = _absolute_unlinked_path(path, "batch manifest path")
    before = _file_sha256(resolved)
    manifest, root, records = _load_batch_manifest(resolved)
    after = _file_sha256(resolved)
    if before != after:
        raise core.ConflictError("batch manifest changed while it was being loaded")
    return manifest, root, records, before


def _explicit_dependencies(
    records: list[tuple[dict[str, Any], Path]],
) -> dict[str, set[str]]:
    """Validate and return manifest-authored dependency edges."""

    known_ids = {str(item["page_id"]) for item, _workspace in records}
    dependencies = {page_id: set() for page_id in known_ids}
    for index, (item, _workspace) in enumerate(records):
        page_id = str(item["page_id"])
        values = item.get("depends_on", [])
        if not isinstance(values, list):
            raise core.ValidationError(f"pages[{index}].depends_on must be an array of page IDs")
        normalized: list[str] = []
        for dependency in values:
            if not isinstance(dependency, (str, int)) or not str(dependency).strip():
                raise core.ValidationError(
                    f"pages[{index}].depends_on must contain non-empty page IDs"
                )
            normalized.append(str(dependency).strip())
        if len(normalized) != len(set(normalized)):
            raise core.ValidationError(
                f"pages[{index}].depends_on contains duplicate page IDs"
            )
        for dependency in normalized:
            if dependency not in known_ids:
                raise core.ValidationError(
                    f"page {page_id} depends on unknown batch page ID: {dependency}"
                )
            if dependency == page_id:
                raise core.ValidationError(f"page {page_id} cannot depend on itself")
            dependencies[page_id].add(dependency)
    return dependencies


def _title_targets(
    records: list[tuple[dict[str, Any], Path]],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Index manifest and desired workspace titles for storage-link resolution."""

    exact: dict[str, set[str]] = {}
    folded: dict[str, set[str]] = {}
    for item, workspace in records:
        page_id = str(item["page_id"])
        titles = {str(item.get("title") or "").strip()}
        meta_path = workspace / core.META_NAME
        if meta_path.is_file():
            meta = core.load_json(meta_path)
            if isinstance(meta, dict):
                titles.add(str(meta.get("title") or "").strip())
        for title in titles - {""}:
            exact.setdefault(title, set()).add(page_id)
            folded.setdefault(title.casefold(), set()).add(page_id)
    return exact, folded


def _resolve_title_dependency(
    title: str,
    *,
    exact: dict[str, set[str]],
    folded: dict[str, set[str]],
) -> str | None:
    """Resolve one storage content-title only when it identifies one batch page."""

    matches = exact.get(title)
    if matches is None:
        matches = folded.get(title.casefold())
    if not matches:
        return None
    if len(matches) != 1:
        raise core.ValidationError(
            f"internal page reference has ambiguous batch content-title: {title}"
        )
    return next(iter(matches))


def _inferred_dependencies(
    records: list[tuple[dict[str, Any], Path]],
) -> dict[str, set[str]]:
    """Infer source-page dependencies from real ri:page storage elements."""

    known_ids = {str(item["page_id"]) for item, _workspace in records}
    exact_titles, folded_titles = _title_targets(records)
    dependencies = {page_id: set() for page_id in known_ids}
    page_tag = f"{{{core.RI_NS}}}page"
    content_id_attribute = f"{{{core.RI_NS}}}content-id"
    content_title_attribute = f"{{{core.RI_NS}}}content-title"
    space_key_attribute = f"{{{core.RI_NS}}}space-key"
    for item, workspace in records:
        page_id = str(item["page_id"])
        storage_path = workspace / core.STORAGE_NAME
        if not storage_path.is_file():
            continue
        canonical = core.canonical_storage(storage_path.read_text(encoding="utf-8"))
        root = ElementTree.fromstring(canonical)
        for element in root.iter(page_tag):
            resolved: set[str] = set()
            content_id = str(element.get(content_id_attribute) or "").strip()
            content_title = str(element.get(content_title_attribute) or "").strip()
            space_key = str(element.get(space_key_attribute) or "").strip()
            if content_id:
                if content_id not in known_ids:
                    # A concrete non-batch content ID is authoritative. Do not
                    # reinterpret its title as a link to a different batch page.
                    continue
                resolved.add(content_id)
            if content_title and (content_id or space_key in {"", "@self"}):
                title_target = _resolve_title_dependency(
                    content_title,
                    exact=exact_titles,
                    folded=folded_titles,
                )
                if title_target is not None:
                    resolved.add(title_target)
            if len(resolved) > 1:
                raise core.ValidationError(
                    f"page {page_id} has an internal page reference whose content-id and "
                    "content-title resolve to different batch pages"
                )
            for dependency in resolved:
                if dependency == page_id:
                    raise core.ValidationError(
                        f"page {page_id} has an internal reference to itself"
                    )
                dependencies[page_id].add(dependency)
    return dependencies


def _dependency_order(
    records: list[tuple[dict[str, Any], Path]],
    *,
    infer_storage: bool = True,
) -> tuple[list[tuple[dict[str, Any], Path]], dict[str, list[str]]]:
    """Return one stable source-before-consumer topological order."""

    dependencies = _explicit_dependencies(records)
    if infer_storage:
        inferred = _inferred_dependencies(records)
        for page_id, page_dependencies in inferred.items():
            dependencies[page_id].update(page_dependencies)

    by_id = {str(item["page_id"]): (item, workspace) for item, workspace in records}
    position = {str(item["page_id"]): index for index, (item, _workspace) in enumerate(records)}
    consumers: dict[str, set[str]] = {page_id: set() for page_id in by_id}
    remaining = {page_id: len(page_dependencies) for page_id, page_dependencies in dependencies.items()}
    for consumer, sources in dependencies.items():
        for source in sources:
            consumers[source].add(consumer)

    ready = sorted(
        (page_id for page_id, count in remaining.items() if count == 0),
        key=position.__getitem__,
    )
    ordered_ids: list[str] = []
    while ready:
        page_id = ready.pop(0)
        ordered_ids.append(page_id)
        for consumer in sorted(consumers[page_id], key=position.__getitem__):
            remaining[consumer] -= 1
            if remaining[consumer] == 0:
                ready.append(consumer)
                ready.sort(key=position.__getitem__)
    if len(ordered_ids) != len(records):
        cycle_ids = sorted(
            (page_id for page_id, count in remaining.items() if count > 0),
            key=position.__getitem__,
        )
        raise core.ValidationError(
            "batch dependency cycle detected among page IDs: " + ", ".join(cycle_ids)
        )
    normalized = {
        page_id: sorted(page_dependencies, key=position.__getitem__)
        for page_id, page_dependencies in dependencies.items()
    }
    return [by_id[page_id] for page_id in ordered_ids], normalized


def _dependency_report(
    records: list[tuple[dict[str, Any], Path]],
    dependencies: dict[str, list[str]],
) -> dict[str, Any]:
    """Build shared auditable ordering metadata for batch reports."""

    order = [str(item["page_id"]) for item, _workspace in records]
    return {
        "dependency_order": order,
        "dependencies": {page_id: dependencies[page_id] for page_id in order},
    }


def _batch_output_path(
    root: Path,
    output: Path | None,
    default_name: str,
) -> Path:
    """Return an isolated batch report path outside page workspaces."""

    default = (root / default_name).resolve()
    target = _absolute_unlinked_path(
        output if output is not None else default,
        "batch report output",
    )
    workspaces_root = (root / "workspaces").resolve()
    if target == workspaces_root or target.is_relative_to(workspaces_root):
        raise core.ValidationError(
            "batch report output must stay outside page workspaces"
        )
    reserved = {
        (root / name).resolve()
        for name in (
            BATCH_MANIFEST_NAME,
            BATCH_VALIDATE_REPORT_NAME,
            BATCH_PLAN_NAME,
            BATCH_UPLOAD_REPORT_NAME,
            BATCH_VERIFY_REPORT_NAME,
            BATCH_COMPLETION_REPORT_NAME,
        )
    }
    if target in reserved and target != default:
        raise core.ValidationError(
            "batch report output must not overwrite another batch artifact"
        )
    return target


def _preflight_reference(root: Path) -> dict[str, Any]:
    """Bind upload evidence to the exact persisted all-page plan."""

    path = root / BATCH_PLAN_NAME
    if not path.is_file():
        raise core.ValidationError("verified batch preflight artifact is missing")
    return {
        "status": "verified",
        "path": str(path),
        "sha256": _file_sha256(path),
    }


def _validated_next_pages_path(
    client: Any, value: Any, seen: set[str], space_id: str
) -> str | None:
    """Validate a page-list cursor without allowing its scan filters to change."""

    if value is None or value == "":
        return None
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise core.ValidationError("page-list next link must be a non-empty URL")
    resolved = urljoin(client.base_url.rstrip("/") + "/", value.lstrip("/"))
    parsed = urlparse(resolved)
    base = urlparse(core.normalize_base_url(client.base_url))
    try:
        port = parsed.port or 443
    except ValueError as error:
        raise core.ValidationError("page-list next link has an invalid port") from error
    if (
        parsed.scheme.lower() != "https"
        or parsed.hostname is None
        or parsed.hostname.lower() != str(base.hostname).lower()
        or port != (base.port or 443)
    ):
        raise core.ValidationError(
            "page-list next link must stay on the configured Confluence origin"
        )
    if parsed.username is not None or parsed.password is not None or parsed.fragment:
        raise core.ValidationError("page-list next link contains unsafe URL components")
    if parsed.path != "/wiki/api/v2/pages":
        raise core.ValidationError(
            "page-list next link must remain on /wiki/api/v2/pages"
        )
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    allowed_keys = {"cursor", "limit", "space-id", "status", "subtype"}
    unexpected_keys = sorted({key for key, _value in pairs} - allowed_keys)
    if unexpected_keys:
        raise core.ValidationError(
            "page-list next link contains unexpected query fields: "
            + ", ".join(unexpected_keys)
        )
    values: dict[str, list[str]] = {}
    for key, item in pairs:
        values.setdefault(key, []).append(item)
    required = {
        "space-id": str(space_id),
        "status": "current",
        "subtype": "page",
    }
    for key, expected in required.items():
        if values.get(key) != [expected]:
            raise core.ValidationError(
                f"page-list next link must preserve {key}={expected}"
            )
    cursor_values = values.get("cursor")
    if cursor_values is None or len(cursor_values) != 1 or not cursor_values[0]:
        raise core.ValidationError("page-list next link must contain one non-empty cursor")
    limit_values = values.get("limit")
    if limit_values is not None and (
        len(limit_values) != 1
        or not limit_values[0].isascii()
        or not limit_values[0].isdigit()
        or not 1 <= int(limit_values[0]) <= 250
    ):
        raise core.ValidationError("page-list next link contains an invalid limit")
    identity = cursor_values[0]
    if identity in seen:
        raise core.ValidationError("page-list pagination cursor repeated")
    seen.add(identity)
    return value


def _inventory_domains(storage: dict[str, Any], adf: dict[str, Any]) -> list[str]:
    domains: set[str] = set()
    for value in list(storage.get("hrefs") or []) + list(adf.get("urls") or []):
        parsed = urlparse(str(value))
        if parsed.hostname:
            domains.add(parsed.hostname.lower())
    return sorted(domains)


def _inventory_page(client: Any, page_id: str) -> dict[str, Any]:
    storage_page = client.page(page_id, "storage")
    core.validate_supported_page(storage_page, page_id)
    adf_page = client.page(page_id, "atlas_doc_format")
    view_page = client.page(page_id, "view")
    version = core.validate_representation_snapshot(
        {"storage": storage_page, "atlas_doc_format": adf_page, "view": view_page}, page_id
    )
    storage = core.body_value(storage_page, "storage")
    adf_payload = core.normalize_adf(core.body_value(adf_page, "atlas_doc_format"))
    view = core.body_value(view_page, "view")
    storage_inventory = core.storage_summary(storage)
    adf_inventory = core.adf_summary(adf_payload)
    attachments = client.attachments(page_id)
    meta = core.page_meta(storage_page)
    return {
        **meta,
        "version": version,
        "web_url": str((storage_page.get("_links") or {}).get("webui") or ""),
        "labels": client.labels(page_id),
        "visible_text": core.visible_text(view),
        "macros": sorted(storage_inventory.get("macros") or {}),
        "adf_nodes": sorted(adf_inventory.get("nodes") or {}),
        "domains": _inventory_domains(storage_inventory, adf_inventory),
        "attachments": sorted(
            str(item.get("title"))
            for item in attachments
            if isinstance(item, dict) and item.get("title")
        ),
    }


def scan_space(client: Any, space_id: str, output: Path) -> dict[str, Any]:
    """Persist a complete searchable inventory for current pages in one space."""

    space_id = core.validate_page_id(space_id)
    output = _absolute_unlinked_path(output, "inventory output")
    output.parent.mkdir(parents=True, exist_ok=True)
    pages: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    path: str | None = "/wiki/api/v2/pages"
    params: dict[str, Any] | None = {
        "space-id": str(space_id),
        "status": "current",
        "subtype": "page",
        "limit": 250,
    }
    seen_page_ids: set[str] = set()
    seen_cursors: set[str] = set()
    while path:
        try:
            listing = client.json("GET", path, params=params)
        except (core.RoundTripError, OSError, ValueError) as error:
            errors.append(
                {
                    "stage": "list-pages",
                    "error": str(error),
                    "rate_limited": _is_rate_limited(error),
                }
            )
            break
        results = listing.get("results")
        if not isinstance(results, list):
            errors.append(
                {
                    "stage": "list-pages",
                    "error": "Confluence page listing results must be an array",
                    "rate_limited": False,
                }
            )
            break
        for item in results:
            page_id = str(item.get("id") or "") if isinstance(item, dict) else ""
            try:
                if not isinstance(item, dict):
                    raise core.ValidationError(
                        "Confluence page listing entries must be objects"
                    )
                page_id = core.validate_page_id(page_id)
                listed_subtype = item.get("subtype")
                if listed_subtype is not None and listed_subtype != "page":
                    raise core.ValidationError(
                        f"unsupported Confluence page-list subtype: {listed_subtype!r}"
                    )
                if page_id in seen_page_ids:
                    raise core.ValidationError(
                        f"page listing repeated page ID across pagination: {page_id}"
                    )
                seen_page_ids.add(page_id)
                inventory_page = _inventory_page(client, page_id)
                if str(inventory_page.get("space_id") or "") != space_id:
                    raise core.ValidationError(
                        f"page {page_id} belongs to space {inventory_page.get('space_id')!r}, "
                        f"not requested space {space_id}"
                    )
                pages.append(inventory_page)
            except (core.RoundTripError, OSError, ValueError) as error:
                errors.append(
                    {
                        "stage": "inventory-page",
                        "page_id": page_id,
                        "error": str(error),
                        "rate_limited": _is_rate_limited(error),
                    }
                )
                if _is_rate_limited(error):
                    path = None
                    break
        else:
            links = listing.get("_links")
            if links is None:
                links = {}
            if not isinstance(links, dict):
                errors.append(
                    {
                        "stage": "list-pages",
                        "error": "Confluence page listing _links must be an object",
                        "rate_limited": False,
                    }
                )
                break
            try:
                path = _validated_next_pages_path(
                    client, links.get("next"), seen_cursors, space_id
                )
            except (core.RoundTripError, OSError, ValueError) as error:
                errors.append(
                    {
                        "stage": "list-pages",
                        "error": str(error),
                        "rate_limited": _is_rate_limited(error),
                    }
                )
                break
            params = None
            continue
        break
    pages.sort(key=lambda item: (str(item.get("title") or "").casefold(), str(item["page_id"])))
    inventory = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "kind": INVENTORY_KIND,
        "generated_at": core.utc_now(),
        "status": "verified" if not errors else "partial",
        "base_url": client.base_url,
        "space_id": str(space_id),
        "pages": pages,
        "errors": errors,
        "rate_limited": any(error.get("rate_limited") for error in errors),
    }
    core.write_json(output, inventory)
    return {**inventory, "inventory": str(output)}


def _match_values(actual: list[str], expected: list[str], *, substring: bool = False) -> bool:
    folded = [value.casefold() for value in actual]
    for query in expected:
        needle = query.casefold()
        if substring:
            if not any(needle in value for value in folded):
                return False
        elif needle not in folded:
            return False
    return True


def filter_inventory(
    inventory: dict[str, Any],
    *,
    text: list[str] | None = None,
    macro: list[str] | None = None,
    adf_node: list[str] | None = None,
    label: list[str] | None = None,
    domain: list[str] | None = None,
    attachment: list[str] | None = None,
    page_id: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return inventory pages matching every supplied local filter."""

    filters = {
        "text": text or [],
        "macro": macro or [],
        "adf_node": adf_node or [],
        "label": label or [],
        "domain": domain or [],
        "attachment": attachment or [],
        "page_id": page_id or [],
    }
    selected_page_ids = {core.validate_page_id(value) for value in filters["page_id"]}
    inventory_page_ids = {
        core.validate_page_id(item.get("page_id"))
        for item in inventory.get("pages", [])
        if isinstance(item, dict)
    }
    missing_page_ids = sorted(selected_page_ids - inventory_page_ids, key=int)
    if missing_page_ids:
        raise core.ValidationError(
            "explicit page IDs are absent from the inventory: "
            + ", ".join(missing_page_ids)
        )
    pages: list[dict[str, Any]] = []
    for item in inventory.get("pages", []):
        if selected_page_ids and str(item.get("page_id") or "") not in selected_page_ids:
            continue
        haystack = " ".join((str(item.get("title") or ""), str(item.get("visible_text") or "")))
        if not all(query.casefold() in haystack.casefold() for query in filters["text"]):
            continue
        if not _match_values(list(item.get("macros") or []), filters["macro"]):
            continue
        if not _match_values(list(item.get("adf_nodes") or []), filters["adf_node"]):
            continue
        if not _match_values(list(item.get("labels") or []), filters["label"]):
            continue
        if not _match_values(list(item.get("domains") or []), filters["domain"]):
            continue
        if not _match_values(
            list(item.get("attachments") or []), filters["attachment"], substring=True
        ):
            continue
        pages.append(item)
    return sorted(pages, key=lambda item: (str(item.get("title") or "").casefold(), str(item["page_id"])))


def explore_inventory(
    inventory_path: Path,
    *,
    output: Path | None = None,
    **filters: list[str] | None,
) -> dict[str, Any]:
    """Query a persisted inventory without contacting Confluence."""

    inventory = _load_inventory(inventory_path)
    pages = filter_inventory(inventory, **filters)
    result = {
        "status": "queried" if inventory.get("status") == "verified" else "partial",
        "inventory_status": inventory.get("status"),
        "filters": {key: value or [] for key, value in filters.items()},
        "count": len(pages),
        "pages": pages,
        "errors": list(inventory.get("errors") or []),
    }
    if output is not None:
        target = _absolute_unlinked_path(output, "explore output")
        inventory_resolved = _absolute_unlinked_path(inventory_path, "inventory path")
        if target == inventory_resolved:
            raise core.ValidationError("explore output must not overwrite its inventory")
        core.write_json(target, result)
    return result


def _batch_manifest_digest(path: Path) -> str:
    return _file_sha256(path.resolve())


def batch_download(
    client: Any,
    inventory_path: Path,
    batch_root: Path,
    *,
    resume: bool = False,
    filters: dict[str, list[str] | None] | None = None,
) -> dict[str, Any]:
    """Download selected inventory pages into a persisted batch manifest."""

    inventory, inventory_path, inventory_digest = _load_inventory_snapshot(
        inventory_path, require_complete=True
    )
    inventory_base_url = core.normalize_base_url(str(inventory.get("base_url") or ""))
    inventory_space_id = core.validate_page_id(inventory.get("space_id"))
    if inventory_base_url != core.normalize_base_url(client.base_url):
        raise core.ValidationError("inventory belongs to a different Confluence tenant")
    selected = filter_inventory(inventory, **(filters or {}))
    if not selected:
        raise core.ValidationError("batch filters selected no pages")
    batch_root = _absolute_unlinked_path(batch_root, "batch directory")
    manifest_path = batch_root / BATCH_MANIFEST_NAME
    selected_ids = [str(item["page_id"]) for item in selected]
    if resume:
        manifest, _, records, _manifest_digest = _load_batch_manifest_snapshot(manifest_path)
        if manifest.get("inventory_sha256") != inventory_digest:
            raise core.ValidationError("inventory changed since the batch manifest was created")
        if [str(item["page_id"]) for item, _ in records] != selected_ids:
            raise core.ValidationError("batch filters no longer select the manifest page set")
    else:
        if manifest_path.exists() or (batch_root.exists() and any(batch_root.iterdir())):
            raise core.ValidationError("batch directory is not empty; pass --resume for its manifest")
        batch_root.mkdir(parents=True, exist_ok=True)
        manifest = {
            "schema_version": BATCH_SCHEMA_VERSION,
            "kind": MANIFEST_KIND,
            "batch_id": _canonical_json_sha256(
                {
                    "base_url": inventory_base_url,
                    "space_id": inventory_space_id,
                    "page_ids": selected_ids,
                    "inventory_sha256": inventory_digest,
                }
            )[:20],
            "created_at": core.utc_now(),
            "updated_at": core.utc_now(),
            "status": "pending",
            "base_url": inventory_base_url,
            "space_id": inventory_space_id,
            "inventory": str(inventory_path),
            "inventory_sha256": inventory_digest,
            "selection": {
                "filters": {
                    key: list(value or []) for key, value in (filters or {}).items()
                },
                "page_ids": selected_ids,
            },
            "pages": [
                {
                    "page_id": str(item["page_id"]),
                    "title": str(item.get("title") or "Untitled"),
                    "workspace": f"workspaces/{item['page_id']}",
                    "status": "pending",
                }
                for item in selected
            ],
            "errors": [],
        }
        core.write_json(manifest_path, manifest)
        manifest, _, records = _load_batch_manifest(manifest_path)

    errors: list[dict[str, Any]] = []
    for item, workspace in records:
        if item.get("status") == "downloaded" and workspace.is_dir():
            try:
                core.validate_workspace(workspace)
                continue
            except (core.RoundTripError, OSError, ValueError):
                pass
        if workspace.exists():
            error = "existing workspace is not a valid resumable download"
            item.update({"status": "failed", "error": error})
            errors.append({"page_id": str(item["page_id"]), "error": error, "rate_limited": False})
            continue
        try:
            result = core.download_page(client, str(item["page_id"]), workspace)
            item.update({"status": "downloaded", "download": result})
            item.pop("error", None)
        except (core.RoundTripError, OSError, ValueError) as error:
            record = {
                "page_id": str(item["page_id"]),
                "error": str(error),
                "rate_limited": _is_rate_limited(error),
            }
            errors.append(record)
            item.update({"status": "failed", "error": str(error)})
            if record["rate_limited"]:
                break
        finally:
            manifest["updated_at"] = core.utc_now()
            manifest["errors"] = errors
            manifest["status"] = (
                "verified"
                if all(page.get("status") == "downloaded" for page in manifest["pages"])
                else "partial"
            )
            core.write_json(manifest_path, manifest)
    return {**manifest, "manifest": str(manifest_path)}


def batch_edit(
    manifest_path: Path,
    *,
    append_storage: str | None = None,
    add_labels: list[str] | None = None,
    remove_labels: list[str] | None = None,
    title_prefix: str | None = None,
    title_suffix: str | None = None,
) -> dict[str, Any]:
    """Prevalidate, then apply deterministic local edits to every workspace."""

    _, _, records = _load_batch_manifest(manifest_path)
    add_labels = add_labels or []
    remove_labels = remove_labels or []
    if not any(
        (
            append_storage is not None,
            add_labels,
            remove_labels,
            title_prefix is not None,
            title_suffix is not None,
        )
    ):
        raise core.ValidationError("batch edit requires at least one edit operation")
    if append_storage is not None:
        if not append_storage:
            raise core.ValidationError("append-storage cannot be empty")
        core.canonical_storage(append_storage)
    for field, values in (("add-label", add_labels), ("remove-label", remove_labels)):
        if any(not isinstance(value, str) or not value for value in values):
            raise core.ValidationError(f"{field} values must be non-empty strings")
        if len(values) != len({value.casefold() for value in values}):
            raise core.ValidationError(f"{field} values contain case-insensitive duplicates")
    add_folded = {value.casefold() for value in add_labels}
    remove_folded = {value.casefold() for value in remove_labels}
    if add_folded & remove_folded:
        raise core.ValidationError("the same label cannot be added and removed in one batch edit")

    candidates: list[dict[str, Any]] = []
    for item, workspace in records:
        core.validate_workspace(workspace)
        storage = (workspace / core.STORAGE_NAME).read_text(encoding="utf-8")
        candidate_storage = storage + (append_storage or "")
        core.canonical_storage(candidate_storage)
        labels = core.load_json(workspace / core.LABELS_NAME)
        remaining = [value for value in labels if value.casefold() not in remove_folded]
        existing_folded = {value.casefold() for value in remaining}
        remaining.extend(value for value in add_labels if value.casefold() not in existing_folded)
        candidate_labels = sorted(set(remaining), key=lambda value: (value.casefold(), value))
        meta = core.load_json(workspace / core.META_NAME)
        candidate_title = f"{title_prefix or ''}{meta['title']}{title_suffix or ''}"
        if not candidate_title.strip():
            raise core.ValidationError(f"batch edit would empty the title for page {item['page_id']}")
        candidates.append(
            {
                "page_id": str(item["page_id"]),
                "workspace": workspace,
                "storage": candidate_storage,
                "labels": candidate_labels,
                "meta": {**meta, "title": candidate_title},
            }
        )

    results: list[dict[str, Any]] = []
    for candidate in candidates:
        workspace = candidate["workspace"]
        core.write_text(workspace / core.STORAGE_NAME, candidate["storage"])
        core.write_json(workspace / core.LABELS_NAME, candidate["labels"])
        core.write_json(workspace / core.META_NAME, candidate["meta"])
        core.capture_ground_truth(workspace)
        results.append(
            {
                "page_id": candidate["page_id"],
                "workspace": str(workspace),
                "status": "edited",
            }
        )
    return {
        "status": "edited",
        "atomic": False,
        "note": "All candidates were prevalidated; filesystem failures can still leave partial local edits.",
        "pages": results,
    }


def batch_validate(manifest_path: Path, *, output: Path | None = None) -> dict[str, Any]:
    """Validate every workspace and aggregate all local errors."""

    manifest, root, records, manifest_digest = _load_batch_manifest_snapshot(manifest_path)
    pages: list[dict[str, Any]] = []
    for item, workspace in records:
        try:
            validation = core.validate_workspace(workspace)
            pages.append({"page_id": str(item["page_id"]), "status": "valid", "validation": validation})
        except (core.RoundTripError, OSError, ValueError) as error:
            pages.append({"page_id": str(item["page_id"]), "status": "failed", "error": str(error)})
    ordered_records, dependencies = _dependency_order(records, infer_storage=False)
    by_id = {page["page_id"]: page for page in pages}
    pages = [by_id[str(item["page_id"])] for item, _workspace in ordered_records]
    dependency_errors: list[str] = []
    if all(page["status"] == "valid" for page in pages):
        try:
            ordered_records, dependencies = _dependency_order(records)
            pages = [by_id[str(item["page_id"])] for item, _workspace in ordered_records]
        except (core.RoundTripError, OSError, ValueError) as error:
            dependency_errors.append(str(error))
    if _batch_manifest_digest(manifest_path) != manifest_digest:
        dependency_errors.append("batch manifest changed during local validation")
    result = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "batch_id": manifest.get("batch_id"),
        "batch_manifest_sha256": manifest_digest,
        "status": (
            "verified"
            if all(page["status"] == "valid" for page in pages) and not dependency_errors
            else "failed"
        ),
        "validated_at": core.utc_now(),
        "pages": pages,
        "errors": dependency_errors,
        **_dependency_report(ordered_records, dependencies),
    }
    if output is not None:
        core.write_json(_batch_output_path(root, output, BATCH_VALIDATE_REPORT_NAME), result)
    return result


def _complete_page_plan(client: Any, item: dict[str, Any], workspace: Path) -> dict[str, Any]:
    """Build one complete no-force plan from one coherent remote preflight."""

    page_id = core.validate_page_id(item.get("page_id"))
    plan, context, _ = core.upload_plan(client, workspace, force=False)
    if str(plan.get("page_id") or "") != page_id:
        raise core.ValidationError(
            f"batch page {page_id} plan refers to page {plan.get('page_id')!r}"
        )
    desired_labels = list(core.load_json(workspace / core.LABELS_NAME))
    current_labels = list(context["current_labels"])
    label_plan = {
        "added": sorted(set(desired_labels) - set(current_labels)),
        "removed": sorted(set(current_labels) - set(desired_labels)),
    }
    desired_state = core.load_json(workspace / core.STATE_NAME)
    current_state = context["current_state"]
    state_changed = not core.states_equivalent(desired_state, current_state)
    plan["labels"] = label_plan
    plan["content_state_changed"] = state_changed
    plan["no_op"] = not any(
        (
            plan["page_update"],
            plan["attachments"],
            label_plan["added"],
            label_plan["removed"],
            state_changed,
        )
    )
    return plan


def _assert_preflight_current(
    manifest_path: Path,
    preflight: dict[str, Any],
    *,
    verified_rows: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], Path, list[tuple[dict[str, Any], Path]]]:
    """Require the exact manifest, dependencies, and desired states that were planned."""

    manifest, root, records, digest = _load_batch_manifest_snapshot(manifest_path)
    if preflight.get("batch_manifest_sha256") != digest:
        raise core.ConflictError("batch manifest changed after preflight")
    ordered, dependencies = _dependency_order(records)
    dependency_report = _dependency_report(ordered, dependencies)
    if (
        preflight.get("dependency_order") != dependency_report["dependency_order"]
        or preflight.get("dependencies") != dependency_report["dependencies"]
    ):
        raise core.ConflictError("batch dependencies changed after preflight")
    planned = {
        str(page.get("page_id")): page.get("plan")
        for page in preflight.get("pages", [])
        if isinstance(page, dict) and page.get("status") == "planned"
    }
    for item, workspace in ordered:
        page_id = str(item["page_id"])
        verified_row = (verified_rows or {}).get(page_id)
        if isinstance(verified_row, dict) and verified_row.get("status") == "verified":
            if verified_row.get("verification_binding") != _verified_api_binding(workspace):
                raise core.ConflictError(
                    f"batch page {page_id} verification binding changed after upload"
                )
            continue
        plan = planned.get(page_id)
        if not isinstance(plan, dict):
            raise core.ValidationError(f"batch preflight has no plan for page {page_id}")
        if plan.get("desired_state_sha256") != core.desired_state_sha256(workspace):
            raise core.ConflictError(
                f"batch page {page_id} desired state changed after preflight"
            )
    return manifest, root, ordered


def batch_plan(client: Any, manifest_path: Path, *, output: Path | None = None) -> dict[str, Any]:
    """Plan every page with no force and make no remote mutations."""

    validation = batch_validate(manifest_path)
    manifest, root, records, manifest_digest = _load_batch_manifest_snapshot(manifest_path)
    target = _batch_output_path(root, output, BATCH_PLAN_NAME)
    if (
        validation["status"] != "verified"
        or validation.get("batch_manifest_sha256") != manifest_digest
    ):
        result = {
            "schema_version": BATCH_SCHEMA_VERSION,
            "status": "failed",
            "planned_at": core.utc_now(),
            "batch_id": manifest.get("batch_id"),
            "batch_manifest_sha256": manifest_digest,
            "prevalidated": False,
            "mutation_attempted": False,
            "pages": validation["pages"],
            "errors": list(validation.get("errors") or [])
            + ["local batch validation failed; no remote plan was attempted"],
            "dependency_order": validation["dependency_order"],
            "dependencies": validation["dependencies"],
        }
        core.write_json(target, result)
        return result
    records, dependencies = _dependency_order(records)
    dependency_report = _dependency_report(records, dependencies)
    pages: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for item, workspace in records:
        try:
            plan = _complete_page_plan(client, item, workspace)
            pages.append({"page_id": str(item["page_id"]), "status": "planned", "plan": plan})
        except (core.RoundTripError, OSError, ValueError) as error:
            record = {
                "page_id": str(item["page_id"]),
                "error": str(error),
                "rate_limited": _is_rate_limited(error),
            }
            errors.append(record)
            pages.append({"page_id": str(item["page_id"]), "status": "failed", **record})
            if record["rate_limited"]:
                break
    planned_ids = {page["page_id"] for page in pages}
    pages.extend(
        {"page_id": str(item["page_id"]), "status": "pending"}
        for item, _ in records
        if str(item["page_id"]) not in planned_ids
    )
    status = "verified" if len(pages) == len(records) and all(
        page["status"] == "planned" for page in pages
    ) else "partial"
    result = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "status": status,
        "planned_at": core.utc_now(),
        "batch_id": manifest.get("batch_id"),
        "batch_manifest_sha256": manifest_digest,
        "prevalidated": True,
        "mutation_attempted": False,
        "forced": False,
        "pages": pages,
        "errors": errors,
        "rate_limited": any(error["rate_limited"] for error in errors),
        **dependency_report,
    }
    if result["status"] == "verified":
        try:
            _assert_preflight_current(manifest_path, result)
        except (core.RoundTripError, OSError, ValueError) as error:
            result["status"] = "failed"
            result["errors"].append(
                {
                    "stage": "preflight-snapshot",
                    "error": str(error),
                    "rate_limited": False,
                }
            )
    core.write_json(target, result)
    return result


def _ordered_report_pages(
    records: list[tuple[dict[str, Any], Path]],
    by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    return [by_id.get(str(item["page_id"]), {"page_id": str(item["page_id"]), "status": "pending"}) for item, _ in records]


def _records_from_report_order(
    records: list[tuple[dict[str, Any], Path]],
    order: list[Any],
) -> list[tuple[dict[str, Any], Path]]:
    """Reorder records by dependency metadata already produced by preflight."""

    by_id = {str(item["page_id"]): (item, workspace) for item, workspace in records}
    normalized = [str(page_id) for page_id in order]
    if set(normalized) != set(by_id) or len(normalized) != len(by_id):
        raise core.ValidationError("preflight dependency order does not match the batch page set")
    return [by_id[page_id] for page_id in normalized]


def _verified_api_binding(workspace: Path) -> dict[str, Any]:
    """Bind a batch row to the exact current per-page API verification evidence."""

    report_path = workspace / core.VERIFY_DIR / core.REPORT_NAME
    if not report_path.is_file():
        raise core.ValidationError("verified batch row has no current API report")
    report = core.load_json(report_path)
    manifest = core.load_json(workspace / core.MANIFEST_NAME)
    meta = core.load_json(workspace / core.META_NAME)
    if not isinstance(report, dict) or report.get("status") != "verified":
        raise core.ValidationError("verified batch row requires a verified API report")
    operation_id = str(report.get("operation_id") or "")
    desired_digest = str(report.get("desired_state_sha256") or "")
    page_id = core.validate_page_id(meta.get("page_id"))
    try:
        remote_version = int(report.get("remote_version") or 0)
        manifest_version = int((manifest.get("page") or {}).get("version") or 0)
    except (TypeError, ValueError) as error:
        raise core.ValidationError("verified batch row has an invalid remote version") from error
    current_digest = core.desired_state_sha256(workspace)
    if (
        not operation_id
        or not desired_digest
        or str(report.get("page_id") or "") != page_id
        or str((manifest.get("page") or {}).get("page_id") or "") != page_id
        or remote_version <= 0
        or desired_digest != current_digest
        or manifest_version != remote_version
        or manifest.get("last_verified_operation_id") != operation_id
        or manifest.get("last_verified_desired_state_sha256") != desired_digest
    ):
        raise core.ConflictError(
            "per-page API verification no longer matches the workspace or manifest lock"
        )
    return {
        "page_id": page_id,
        "desired_state_sha256": desired_digest,
        "operation_id": operation_id,
        "remote_version": remote_version,
        "api_report_sha256": _file_sha256(report_path),
    }


def _verified_batch_row_is_current(
    client: Any,
    item: dict[str, Any],
    row: dict[str, Any],
    workspace: Path,
    preflight_page: dict[str, Any] | None,
) -> bool:
    """Return whether a resumable verified row still proves a live no-op."""

    if row.get("status") != "verified":
        return False
    plan = (preflight_page or {}).get("plan")
    if not isinstance(plan, dict) or plan.get("no_op") is not True:
        return False
    binding = row.get("verification_binding")
    if not isinstance(binding, dict):
        return False
    try:
        if binding != _verified_api_binding(workspace):
            return False
        fresh_plan = _complete_page_plan(client, item, workspace)
        return (
            fresh_plan.get("no_op") is True
            and fresh_plan.get("desired_state_sha256")
            == plan.get("desired_state_sha256")
        )
    except (core.RoundTripError, OSError, ValueError):
        return False


def batch_upload(
    client: Any,
    manifest_path: Path,
    *,
    message: str,
    resume: bool = False,
    output: Path | None = None,
) -> dict[str, Any]:
    """Preflight all pages, then upload sequentially with persisted resume state."""

    manifest_path = _absolute_unlinked_path(manifest_path, "batch manifest path")
    manifest, root, records, digest = _load_batch_manifest_snapshot(manifest_path)
    target = _batch_output_path(root, output, BATCH_UPLOAD_REPORT_NAME)
    if target.exists() and not resume:
        raise core.ValidationError("batch upload report exists; pass --resume to continue it")
    previous: dict[str, Any] = {}
    if resume:
        if not target.is_file():
            raise core.ValidationError("cannot resume without an existing batch upload report")
        previous = core.load_json(target)
        if not isinstance(previous, dict) or previous.get("schema_version") != BATCH_SCHEMA_VERSION:
            raise core.ValidationError("batch upload report has an unsupported schema")
        if previous.get("batch_id") != manifest.get("batch_id"):
            raise core.ValidationError("batch upload report belongs to a different batch")
        if previous.get("batch_manifest_sha256") != digest:
            raise core.ValidationError("batch manifest changed since the upload report was created")
    by_id = {
        str(item.get("page_id")): item
        for item in previous.get("pages", [])
        if isinstance(item, dict) and item.get("page_id")
    }
    created_at = previous.get("created_at") or core.utc_now()
    history = list(previous.get("history") or [])
    if resume:
        history.append(
            {
                "resumed_at": core.utc_now(),
                "previous_status": previous.get("status"),
                "previous_errors": list(previous.get("errors") or []),
            }
        )

    preflight = batch_plan(client, manifest_path)
    if preflight.get("batch_manifest_sha256") != digest:
        preflight = {
            **preflight,
            "status": "failed",
            "errors": list(preflight.get("errors") or [])
            + ["batch manifest changed between upload initialization and preflight"],
        }
    records = _records_from_report_order(records, list(preflight.get("dependency_order") or []))
    preflight_by_id = {
        str(page.get("page_id")): page
        for page in preflight.get("pages", [])
        if isinstance(page, dict) and page.get("page_id")
    }
    dependency_report = {
        "dependency_order": list(preflight["dependency_order"]),
        "dependencies": dict(preflight["dependencies"]),
    }
    if preflight["status"] != "verified":
        result = {
            "schema_version": BATCH_SCHEMA_VERSION,
            "status": "partial",
            "created_at": created_at,
            "updated_at": core.utc_now(),
            "batch_id": manifest.get("batch_id"),
            "batch_manifest_sha256": digest,
            "atomic": False,
            "rollback_attempted": False,
            "preflight": preflight,
            "pages": _ordered_report_pages(records, by_id),
            "errors": ["batch preflight failed; no new upload was started"],
            "rate_limited": bool(preflight.get("rate_limited")),
            "resumed": resume,
            "history": history,
            **dependency_report,
        }
        core.write_json(target, result)
        return result

    preflight_reference = _preflight_reference(root)
    errors: list[dict[str, Any]] = []
    for item, workspace in records:
        page_id = str(item["page_id"])
        row = by_id.get(page_id) or {}
        if row.get("status") == "verified" and not _verified_batch_row_is_current(
            client, item, row, workspace, preflight_by_id.get(page_id)
        ):
            by_id[page_id] = {
                "page_id": page_id,
                "status": "pending",
                "resume_reason": "prior verified binding is stale; page will be reprocessed",
            }
    snapshot_error: dict[str, Any] | None = None
    try:
        _manifest, _root, records = _assert_preflight_current(
            manifest_path,
            preflight,
            verified_rows=by_id,
        )
    except (core.RoundTripError, OSError, ValueError) as error:
        snapshot_error = {
            "error": str(error),
            "rate_limited": _is_rate_limited(error),
        }
    initial_pages = _ordered_report_pages(records, by_id)
    core.write_json(
        target,
        {
            "schema_version": BATCH_SCHEMA_VERSION,
            "status": (
                "verified"
                if snapshot_error is None
                and all(page["status"] == "verified" for page in initial_pages)
                else "partial"
            ),
            "created_at": created_at,
            "updated_at": core.utc_now(),
            "batch_id": manifest.get("batch_id"),
            "batch_manifest_sha256": digest,
            "atomic": False,
            "rollback_attempted": False,
            "preflight": preflight_reference,
            "pages": initial_pages,
            "errors": [snapshot_error] if snapshot_error else [],
            "rate_limited": bool(snapshot_error and snapshot_error["rate_limited"]),
            "resumed": resume,
            "history": history,
            **dependency_report,
        },
    )
    if snapshot_error is not None:
        return core.load_json(target)
    for item, workspace in records:
        page_id = str(item["page_id"])
        if (by_id.get(page_id) or {}).get("status") == "verified":
            continue
        mutation_started = False
        try:
            _manifest, _root, current_records = _assert_preflight_current(
                manifest_path,
                preflight,
                verified_rows=by_id,
            )
            current_by_id = {
                str(current_item["page_id"]): (current_item, current_workspace)
                for current_item, current_workspace in current_records
            }
            item, workspace = current_by_id[page_id]
            expected_plan = (preflight_by_id.get(page_id) or {}).get("plan") or {}
            expected_digest = str(expected_plan.get("desired_state_sha256") or "")
            if not expected_digest:
                raise core.ValidationError(
                    f"batch preflight has no desired-state digest for page {page_id}"
                )
            mutation_started = True
            uploaded = core.upload_workspace(
                client,
                workspace,
                message=message,
                force=False,
                dry_run=False,
                verify=True,
                expected_desired_state_sha256=expected_digest,
            )
            verified = uploaded.get("status") == "uploaded" and (
                uploaded.get("verification") or {}
            ).get("status") == "verified" and str(uploaded.get("page_id") or "") == page_id
            by_id[page_id] = {
                "page_id": page_id,
                "status": "verified" if verified else "failed",
                "result": uploaded,
            }
            if verified:
                by_id[page_id]["verification_binding"] = _verified_api_binding(workspace)
            if not verified:
                upload_error = uploaded.get("error")
                if isinstance(upload_error, dict):
                    error_message = str(upload_error.get("message") or "page upload failed")
                else:
                    error_message = "page upload did not pass API verification"
                rate_limited = _is_rate_limited(error_message)
                by_id[page_id].update(
                    {
                        "error": error_message,
                        "mutation_state": "unknown-partial",
                        "rate_limited": rate_limited,
                    }
                )
                errors.append(
                    {
                        "page_id": page_id,
                        "error": error_message,
                        "rate_limited": rate_limited,
                    }
                )
                break
        except (core.RoundTripError, OSError, ValueError) as error:
            record = {
                "page_id": page_id,
                "error": str(error),
                "rate_limited": _is_rate_limited(error),
            }
            errors.append(record)
            by_id[page_id] = {
                "page_id": page_id,
                "status": "failed",
                "error": str(error),
                "mutation_state": "unknown-partial" if mutation_started else "not-started",
                "rate_limited": record["rate_limited"],
            }
            break
        finally:
            interim_pages = _ordered_report_pages(records, by_id)
            interim = {
                "schema_version": BATCH_SCHEMA_VERSION,
                "status": "verified" if all(page["status"] == "verified" for page in interim_pages) else "partial",
                "created_at": created_at,
                "updated_at": core.utc_now(),
                "batch_id": manifest.get("batch_id"),
                "batch_manifest_sha256": digest,
                "atomic": False,
                "rollback_attempted": False,
                "preflight": preflight_reference,
                "pages": interim_pages,
                "errors": errors,
                "rate_limited": any(error["rate_limited"] for error in errors),
                "resumed": resume,
                "history": history,
                **dependency_report,
            }
            core.write_json(target, interim)
    return core.load_json(target)


def batch_verify(client: Any, manifest_path: Path, *, output: Path | None = None) -> dict[str, Any]:
    """Run API verification for every downloaded page workspace."""

    manifest, root, records, manifest_digest = _load_batch_manifest_snapshot(manifest_path)
    target = _batch_output_path(root, output, BATCH_VERIFY_REPORT_NAME)
    validation = batch_validate(manifest_path)
    if validation["status"] != "verified":
        result = {
            "schema_version": BATCH_SCHEMA_VERSION,
            "status": "failed",
            "verified_at": core.utc_now(),
            "batch_id": manifest.get("batch_id"),
            "batch_manifest_sha256": manifest_digest,
            "pages": validation["pages"],
            "errors": list(validation.get("errors") or [])
            + ["local batch validation failed; remote verification was not attempted"],
            "dependency_order": validation["dependency_order"],
            "dependencies": validation["dependencies"],
        }
        core.write_json(target, result)
        return result
    records, dependencies = _dependency_order(records)
    dependency_report = _dependency_report(records, dependencies)
    pages: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for item, workspace in records:
        page_id = str(item["page_id"])
        page_record: dict[str, Any]
        try:
            verification = core.verify_workspace(client, workspace)
            status = (
                "verified"
                if verification.get("status") == "verified"
                and str(verification.get("page_id") or "") == page_id
                else "failed"
            )
            page_record = {
                "page_id": page_id,
                "status": status,
                "verification": verification,
            }
            if status != "verified":
                errors.append({"page_id": page_id, "error": "API verification failed", "rate_limited": False})
        except (core.RoundTripError, OSError, ValueError) as error:
            record = {
                "page_id": page_id,
                "error": str(error),
                "rate_limited": _is_rate_limited(error),
            }
            errors.append(record)
            page_record = {"page_id": page_id, "status": "failed", **record}
        pages.append(page_record)
        if page_record.get("rate_limited"):
            break
    processed = {page["page_id"] for page in pages}
    pages.extend(
        {"page_id": str(item["page_id"]), "status": "pending"}
        for item, _ in records
        if str(item["page_id"]) not in processed
    )
    if _batch_manifest_digest(manifest_path) != manifest_digest:
        errors.append(
            {
                "error": "batch manifest changed during API verification",
                "rate_limited": False,
            }
        )
    result = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "status": (
            "verified"
            if all(page["status"] == "verified" for page in pages) and not errors
            else "partial"
        ),
        "verified_at": core.utc_now(),
        "batch_id": manifest.get("batch_id"),
        "batch_manifest_sha256": manifest_digest,
        "pages": pages,
        "errors": errors,
        "rate_limited": any(error["rate_limited"] for error in errors),
        **dependency_report,
    }
    core.write_json(target, result)
    return result


def batch_completion_gate(manifest_path: Path, *, output: Path | None = None) -> dict[str, Any]:
    """Require the per-page API and authenticated-browser completion gate for all pages."""

    manifest, root, records, manifest_digest = _load_batch_manifest_snapshot(manifest_path)
    records, dependencies = _dependency_order(records)
    target = _batch_output_path(root, output, BATCH_COMPLETION_REPORT_NAME)
    pages: list[dict[str, Any]] = []
    for item, workspace in records:
        completion = core.validate_completion_gate(workspace)
        page_id = str(item["page_id"])
        passed = completion.get("status") == "verified" and str(
            completion.get("page_id") or ""
        ) == page_id
        pages.append(
            {
                "page_id": page_id,
                "status": "verified" if passed else "failed",
                "completion": completion,
            }
        )
    errors: list[str] = []
    if _batch_manifest_digest(manifest_path) != manifest_digest:
        errors.append("batch manifest changed during completion validation")
    result = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "status": (
            "verified"
            if all(page["status"] == "verified" for page in pages) and not errors
            else "failed"
        ),
        "completed_at": core.utc_now(),
        "batch_id": manifest.get("batch_id"),
        "batch_manifest_sha256": manifest_digest,
        "pages": pages,
        "errors": errors,
        **_dependency_report(records, dependencies),
    }
    core.write_json(target, result)
    return result


def _add_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", action="append", default=[])
    parser.add_argument("--macro", action="append", default=[])
    parser.add_argument("--adf-node", action="append", default=[])
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--domain", action="append", default=[])
    parser.add_argument("--attachment", action="append", default=[])
    parser.add_argument("--page-id", action="append", default=[])


def _filters(args: argparse.Namespace) -> dict[str, list[str] | None]:
    return {
        "text": args.text,
        "macro": args.macro,
        "adf_node": args.adf_node,
        "label": args.label,
        "domain": args.domain,
        "attachment": args.attachment,
        "page_id": args.page_id,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the standalone batch command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="Site root; prefer CONFLUENCE_BASE_URL")
    parser.add_argument("--username", help="Account email; prefer CONFLUENCE_USERNAME")
    parser.add_argument("--env-file", type=Path, help="Dotenv file containing Confluence credentials")
    parser.add_argument("--timeout", type=int, default=60)
    commands = parser.add_subparsers(dest="command", required=True)

    scan = commands.add_parser("scan-space", help="Persist a searchable inventory of a space")
    scan.add_argument("space_id")
    scan.add_argument("output", type=Path)

    explore = commands.add_parser("explore", help="Query an inventory locally")
    explore.add_argument("inventory", type=Path)
    explore.add_argument("--output", type=Path, help="Persist the filtered local result as JSON")
    _add_filters(explore)

    download = commands.add_parser("batch-download", help="Download selected pages and write a batch manifest")
    download.add_argument("inventory", type=Path)
    download.add_argument("batch_root", type=Path)
    download.add_argument("--resume", action="store_true")
    _add_filters(download)

    edit = commands.add_parser("batch-edit", help="Apply deterministic edits after all-page prevalidation")
    edit.add_argument("manifest", type=Path)
    append_group = edit.add_mutually_exclusive_group()
    append_group.add_argument("--append-storage")
    append_group.add_argument("--append-storage-file", type=Path)
    edit.add_argument("--add-label", action="append", default=[])
    edit.add_argument("--remove-label", action="append", default=[])
    edit.add_argument("--title-prefix")
    edit.add_argument("--title-suffix")

    validate = commands.add_parser("batch-validate", help="Validate every local workspace")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--output", type=Path)

    plan = commands.add_parser("batch-plan", help="Plan every workspace before any mutation")
    plan.add_argument("manifest", type=Path)
    plan.add_argument("--output", type=Path)

    upload = commands.add_parser("batch-upload", help="Upload sequentially with partial/resume reporting")
    upload.add_argument("manifest", type=Path)
    upload.add_argument("--message", default="Updated through roundtrip-confluence-pages batch workflow")
    upload.add_argument("--resume", action="store_true")
    upload.add_argument("--output", type=Path)

    verify = commands.add_parser("batch-verify", help="Run API verification for every workspace")
    verify.add_argument("manifest", type=Path)
    verify.add_argument("--output", type=Path)

    complete = commands.add_parser("batch-completion-gate", help="Require every per-page completion gate")
    complete.add_argument("manifest", type=Path)
    complete.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the batch CLI and emit one machine-readable JSON result."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "explore":
            result = explore_inventory(args.inventory, output=args.output, **_filters(args))
        elif args.command == "batch-edit":
            fragment = args.append_storage
            if args.append_storage_file is not None:
                fragment = args.append_storage_file.read_text(encoding="utf-8")
            result = batch_edit(
                args.manifest,
                append_storage=fragment,
                add_labels=args.add_label,
                remove_labels=args.remove_label,
                title_prefix=args.title_prefix,
                title_suffix=args.title_suffix,
            )
        elif args.command == "batch-validate":
            result = batch_validate(args.manifest, output=args.output)
        elif args.command == "batch-completion-gate":
            result = batch_completion_gate(args.manifest, output=args.output)
        else:
            base_url, username, token = core.credentials_from_args(args)
            client = core.ConfluenceClient(base_url, username, token, timeout=args.timeout)
            if args.command == "scan-space":
                result = scan_space(client, args.space_id, args.output)
            elif args.command == "batch-download":
                result = batch_download(
                    client,
                    args.inventory,
                    args.batch_root,
                    resume=args.resume,
                    filters=_filters(args),
                )
            elif args.command == "batch-plan":
                result = batch_plan(client, args.manifest, output=args.output)
            elif args.command == "batch-upload":
                result = batch_upload(
                    client,
                    args.manifest,
                    message=args.message,
                    resume=args.resume,
                    output=args.output,
                )
            elif args.command == "batch-verify":
                result = batch_verify(client, args.manifest, output=args.output)
            else:
                parser.error(f"unknown command: {args.command}")
                return 2
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result.get("status") not in {"failed", "partial", "verification-failed"} else 2
    except (core.RoundTripError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error), "type": type(error).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
