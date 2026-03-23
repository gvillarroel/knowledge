from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import shutil
from typing import Any, Iterable
from urllib.parse import urlparse
from zipfile import ZipFile

import yaml


KEY_DIRS = ("raw", "library")
TEMP_ROOT = Path("/tmp").resolve()


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass
class KnowledgeStore:
    root_override: Path | None = None

    def __post_init__(self) -> None:
        self.root = (
            self.root_override.expanduser().resolve()
            if self.root_override
            else (Path.home() / ".knowledge").resolve()
        )
        self.temp_root = TEMP_ROOT
        self.config_path = self.root / "config.yaml"
        self.keys_path = self.root / "keys.yaml"
        self.exports_dir = self.root / "exports"

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.temp_root.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self._write_yaml(
                self.config_path,
                {
                    "version": 1,
                    "created_at": utc_now(),
                    "paths": {"exports": "exports", "tmp": str(self.temp_root)},
                },
            )
        else:
            config = self._read_yaml(self.config_path, default={})
            paths = config.setdefault("paths", {})
            changed = False
            if paths.get("exports") != "exports":
                paths["exports"] = "exports"
                changed = True
            if paths.get("tmp") != str(self.temp_root):
                paths["tmp"] = str(self.temp_root)
                changed = True
            if changed:
                self._write_yaml(self.config_path, config)
        if not self.keys_path.exists():
            self._write_yaml(self.keys_path, {"keys": {}})

    @property
    def keys(self) -> dict[str, str]:
        payload = self._read_yaml(self.keys_path, default={"keys": {}})
        return payload.get("keys", {})

    def set_key(self, name: str, value: str) -> None:
        payload = self._read_yaml(self.keys_path, default={"keys": {}})
        payload.setdefault("keys", {})[name] = value
        self._write_yaml(self.keys_path, payload)

    def create_collection_key(self, name: str) -> dict[str, Any]:
        key_dir = self.key_dir(name)
        metadata_path = key_dir / "metadata.yaml"
        if metadata_path.exists():
            raise FileExistsError(f"key '{name}' already exists")

        key_dir.mkdir(parents=True, exist_ok=False)
        for directory_name in KEY_DIRS:
            (key_dir / directory_name).mkdir(parents=True, exist_ok=True)

        timestamp = utc_now()
        payload = {
            "version": 1,
            "name": name,
            "created_at": timestamp,
            "updated_at": timestamp,
            "commands": {
                "list_sources": f"know list sources --key {name}",
                "sync": f"know sync --key {name}",
                "export": f"know export --key {name}",
            },
            "sources": [],
        }
        self._write_yaml(metadata_path, payload)
        return payload

    def list_collection_keys(self) -> list[str]:
        keys: list[str] = []
        for path in sorted(self.root.iterdir()):
            if path.is_dir() and (path / "metadata.yaml").exists():
                keys.append(path.name)
        return keys

    def get_collection_metadata(self, name: str) -> dict[str, Any]:
        path = self.key_dir(name) / "metadata.yaml"
        if not path.exists():
            raise FileNotFoundError(f"key '{name}' not found")
        metadata = self._read_yaml(path, default={})
        metadata["name"] = name
        metadata.setdefault("sources", [])
        metadata.setdefault("commands", {})
        return metadata

    def save_collection_metadata(self, name: str, metadata: dict[str, Any]) -> None:
        metadata["updated_at"] = utc_now()
        self._write_yaml(self.key_dir(name) / "metadata.yaml", metadata)

    def add_collection_source(
        self,
        key_name: str,
        source_type: str,
        *,
        source_id: str | None = None,
        title: str,
        config: dict[str, Any],
        update_command: str,
        delete_command: str,
    ) -> dict[str, Any]:
        metadata = self.get_collection_metadata(key_name)
        source_id = source_id or self._source_id(source_type, title)
        sources = metadata.setdefault("sources", [])
        if any(source.get("id") == source_id for source in sources):
            raise FileExistsError(f"source '{source_id}' already exists on key '{key_name}'")

        timestamp = utc_now()
        source_record = {
            "type": source_type,
            "id": source_id,
            "title": title,
            "created_at": timestamp,
            "updated_at": timestamp,
            "update_command": update_command,
            "delete_command": delete_command,
            "config": config,
        }
        sources.append(source_record)
        self.save_collection_metadata(key_name, metadata)
        self._delete_legacy_source_record(key_name, source_type, source_id)
        return {"key": key_name, **source_record}

    def delete_collection_source(self, key_name: str, source_id: str) -> dict[str, Any]:
        metadata = self.get_collection_metadata(key_name)
        sources = metadata.get("sources", [])
        match = next((source for source in sources if source.get("id") == source_id), None)
        if match is None:
            raise FileNotFoundError(f"source '{source_id}' not found on key '{key_name}'")

        metadata["sources"] = [source for source in sources if source.get("id") != source_id]
        self.save_collection_metadata(key_name, metadata)
        self._delete_legacy_source_record(key_name, match["type"], source_id)
        self._delete_source_dirs(key_name, match["type"], source_id)
        return {"key": key_name, "id": source_id, "type": match["type"]}

    def list_collection_sources(
        self,
        key_name: str | None = None,
        source_type: str | None = None,
    ) -> list[dict[str, Any]]:
        key_names = [key_name] if key_name else self.list_collection_keys()
        matches: list[dict[str, Any]] = []
        for name in key_names:
            metadata = self.get_collection_metadata(name)
            for source in metadata.get("sources", []):
                if source_type and source.get("type") != source_type:
                    continue
                matches.append({"key": name, **source})
        return matches

    def update_collection_source(self, source: dict[str, Any]) -> None:
        key_name = source["key"]
        metadata = self.get_collection_metadata(key_name)
        updated_sources: list[dict[str, Any]] = []
        for current in metadata.get("sources", []):
            if current.get("id") == source["id"]:
                replacement = {k: v for k, v in source.items() if k != "key"}
                replacement["updated_at"] = utc_now()
                updated_sources.append(replacement)
            else:
                updated_sources.append(current)
        metadata["sources"] = updated_sources
        self.save_collection_metadata(key_name, metadata)
        self._delete_legacy_source_record(key_name, source["type"], source["id"])

    def source_raw_dir(self, source: dict[str, Any]) -> Path:
        path = self.key_dir(source["key"]) / "raw" / source["type"] / source["id"]
        path.mkdir(parents=True, exist_ok=True)
        return path

    def source_library_dir(self, source: dict[str, Any]) -> Path:
        path = self.key_dir(source["key"]) / "library" / source["type"] / source["id"]
        path.mkdir(parents=True, exist_ok=True)
        return path

    def source_cache_dir(self, source: dict[str, Any]) -> Path:
        path = (
            self.temp_root
            / "knowledge-cache"
            / source["key"]
            / source["type"]
            / source["id"]
        )
        path.mkdir(parents=True, exist_ok=True)
        return path

    def archive_keys(self, key_names: Iterable[str]) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        archive_path = self.exports_dir / f"knowledge-export-{timestamp}.zip"
        with ZipFile(archive_path, "w") as archive:
            for key_name in key_names:
                key_dir = self.key_dir(key_name)
                if not key_dir.exists():
                    raise FileNotFoundError(f"key '{key_name}' not found")
                for path in sorted(key_dir.rglob("*")):
                    if path.is_file():
                        archive.write(path, arcname=str(path.relative_to(self.root)).replace("\\", "/"))
        return archive_path

    def import_archive(self, archive_path: Path) -> dict[str, Any]:
        archive_path = archive_path.expanduser().resolve()
        if not archive_path.exists():
            raise FileNotFoundError(f"archive '{archive_path}' not found")

        imported_keys: set[str] = set()
        merged_sources = 0
        with ZipFile(archive_path) as archive:
            for member in archive.namelist():
                target = self.root / member
                target.parent.mkdir(parents=True, exist_ok=True)
                if member.endswith("/"):
                    continue
                if member.endswith("metadata.yaml") and len(Path(member).parts) >= 2:
                    key_name = Path(member).parts[0]
                    imported_keys.add(key_name)
                    incoming = yaml.safe_load(archive.read(member).decode("utf-8")) or {}
                    if target.exists():
                        current = self._read_yaml(target, default={})
                        merged, new_count = self._merge_metadata(current, incoming)
                        merged_sources += new_count
                        self._write_yaml(target, merged)
                    else:
                        merged_sources += len(incoming.get("sources", []))
                        target.write_text(
                            yaml.safe_dump(incoming, sort_keys=False, allow_unicode=False),
                            encoding="utf-8",
                        )
                    self._ensure_key_dirs(key_name)
                    continue

                with archive.open(member) as source_handle:
                    target.write_bytes(source_handle.read())
                if len(Path(member).parts) >= 2:
                    imported_keys.add(Path(member).parts[0])

        for key_name in imported_keys:
            self.cleanup_legacy_source_records(key_name)
            self.cleanup_orphan_source_dirs(key_name)

        return {
            "archive": str(archive_path),
            "imported_keys": sorted(imported_keys),
            "merged_sources": merged_sources,
        }

    def resolve_key(self, value: str) -> str:
        if value.startswith("$"):
            key_name = value[1:]
            if key_name not in self.keys:
                raise KeyError(f"missing key '{key_name}'")
            return self.keys[key_name]
        return value

    def key_dir(self, key_name: str) -> Path:
        return self.root / key_name

    def _ensure_key_dirs(self, key_name: str) -> None:
        key_dir = self.key_dir(key_name)
        key_dir.mkdir(parents=True, exist_ok=True)
        for directory_name in KEY_DIRS:
            (key_dir / directory_name).mkdir(parents=True, exist_ok=True)

    def cleanup_legacy_source_records(self, key_name: str | None = None) -> dict[str, int]:
        key_names = [key_name] if key_name else self.list_collection_keys()
        removed = 0
        for current_key in key_names:
            metadata = self.get_collection_metadata(current_key)
            for source in metadata.get("sources", []):
                source_type = source.get("type")
                source_id = source.get("id")
                if not source_type or not source_id:
                    continue
                record_path = self.key_dir(current_key) / source_type / f"{source_id}.yaml"
                if record_path.exists():
                    removed += 1
                self._delete_legacy_source_record(current_key, source_type, source_id)
        return {"keys": len(key_names), "removed": removed}

    def cleanup_orphan_source_dirs(self, key_name: str | None = None) -> dict[str, int]:
        key_names = [key_name] if key_name else self.list_collection_keys()
        removed = 0
        for current_key in key_names:
            metadata = self.get_collection_metadata(current_key)
            expected = {
                (source.get("type"), source.get("id"))
                for source in metadata.get("sources", [])
                if source.get("type") and source.get("id")
            }
            for bucket in ("raw", "library"):
                base_dir = self.key_dir(current_key) / bucket
                if not base_dir.exists():
                    continue
                for type_dir in [path for path in base_dir.iterdir() if path.is_dir()]:
                    for source_dir in [path for path in type_dir.iterdir() if path.is_dir()]:
                        if (type_dir.name, source_dir.name) not in expected:
                            shutil.rmtree(source_dir)
                            removed += 1
                    if not any(type_dir.iterdir()):
                        type_dir.rmdir()
        return {"keys": len(key_names), "removed": removed}

    def _delete_legacy_source_record(self, key_name: str, source_type: str, source_id: str) -> None:
        source_dir = self.key_dir(key_name) / source_type
        record_path = source_dir / f"{source_id}.yaml"
        if record_path.exists():
            record_path.unlink()
        if source_dir.exists() and not any(source_dir.iterdir()):
            source_dir.rmdir()

    def _delete_source_dirs(self, key_name: str, source_type: str, source_id: str) -> None:
        for bucket in KEY_DIRS:
            type_dir = self.key_dir(key_name) / bucket / source_type
            source_dir = type_dir / source_id
            if source_dir.exists():
                shutil.rmtree(source_dir)
            if type_dir.exists() and not any(type_dir.iterdir()):
                type_dir.rmdir()

    def _merge_metadata(self, current: dict[str, Any], incoming: dict[str, Any]) -> tuple[dict[str, Any], int]:
        merged = dict(current)
        merged["version"] = max(int(current.get("version", 1)), int(incoming.get("version", 1)))
        merged["name"] = incoming.get("name") or current.get("name")
        merged["created_at"] = current.get("created_at") or incoming.get("created_at") or utc_now()
        merged["updated_at"] = utc_now()
        merged["commands"] = {
            **(current.get("commands", {}) if isinstance(current.get("commands"), dict) else {}),
            **(incoming.get("commands", {}) if isinstance(incoming.get("commands"), dict) else {}),
        }

        existing_sources = current.get("sources", []) if isinstance(current.get("sources"), list) else []
        incoming_sources = incoming.get("sources", []) if isinstance(incoming.get("sources"), list) else []
        by_id: dict[str, dict[str, Any]] = {source["id"]: source for source in existing_sources if "id" in source}
        new_count = 0
        for source in incoming_sources:
            source_id = source.get("id")
            if not source_id:
                continue
            if source_id not in by_id:
                new_count += 1
            by_id[source_id] = source
        merged["sources"] = list(by_id.values())
        return merged, new_count

    def _read_yaml(self, path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            return default
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else default

    def _write_yaml(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )

    def _source_id(self, source_type: str, title: str) -> str:
        parsed = urlparse(title)
        candidate = parsed.path.rsplit("/", 1)[-1] if parsed.scheme else title
        safe = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in candidate).strip("-")
        if not safe:
            safe = "source"
        return f"{source_type}-{safe.lower()}"
