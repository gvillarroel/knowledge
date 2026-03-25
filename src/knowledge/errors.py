"""User-facing error types for the knowledge CLI."""

from __future__ import annotations


class KnowledgeError(Exception):
    """Base error for all knowledge CLI operations."""


class CredentialNotFoundError(KnowledgeError):
    """Raised when a credential reference cannot be resolved."""

    def __init__(self, reference: str) -> None:
        self.reference = reference
        super().__init__(f"credential '{reference}' not found")


class SourceNotFoundError(KnowledgeError):
    """Raised when a source id does not exist on the given key."""

    def __init__(self, key_name: str, source_id: str) -> None:
        self.key_name = key_name
        self.source_id = source_id
        super().__init__(f"source '{source_id}' not found on key '{key_name}'")


class KeyAlreadyExistsError(KnowledgeError):
    """Raised when trying to create a key that already exists."""

    def __init__(self, key_name: str) -> None:
        self.key_name = key_name
        super().__init__(f"key '{key_name}' already exists")


class SourceAlreadyExistsError(KnowledgeError):
    """Raised when trying to register a source that is already attached."""

    def __init__(self, key_name: str, source_id: str) -> None:
        self.key_name = key_name
        self.source_id = source_id
        super().__init__(f"source '{source_id}' already exists on key '{key_name}'")


class InvalidURLError(KnowledgeError):
    """Raised when a URL argument fails basic validation."""

    def __init__(self, url: str, reason: str = "invalid URL") -> None:
        self.url = url
        super().__init__(f"{reason}: {url}")


class SyncError(KnowledgeError):
    """Raised when a source sync operation fails."""

    def __init__(self, key_name: str, source_id: str, reason: str) -> None:
        self.key_name = key_name
        self.source_id = source_id
        super().__init__(f"sync failed for source '{source_id}' on key '{key_name}': {reason}")
