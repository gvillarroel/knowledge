"""GitHub source — clones/pulls a repository and converts files to Markdown.

Supports fetching multiple branches simultaneously.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from .base import BaseSource
from ..transform.markdown import build_frontmatter, write_markdown_page, _slugify

_MARKDOWN_EXTENSIONS = {".md", ".markdown", ".rst", ".txt"}
_CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".go", ".java", ".c", ".cpp", ".h", ".hpp",
    ".rs", ".rb", ".php", ".cs", ".sh", ".yaml", ".yml", ".json", ".toml",
    ".html", ".css", ".sql",
}


class GitHubSource(BaseSource):
    """Clone a GitHub repository (one or more branches) and write Markdown files.

    Configuration keys
    ------------------
    url : str
        HTTPS or SSH URL of the repository.
    branches : list[str], optional
        List of branch names to fetch (default: ``["main"]``).
    token : str, optional
        Personal access token for private repos (HTTPS URLs only).
    include_code : bool, optional
        Whether to wrap non-Markdown source files in fenced code blocks
        (default: ``True``).
    max_file_size_kb : int, optional
        Skip files larger than this limit in KB (default: 500).
    """

    source_type = "github"

    def __init__(self, key: str, config: dict[str, Any]) -> None:
        super().__init__(key, config)
        self.repo_url: str = config["url"]
        self.branches: list[str] = config.get("branches", ["main"])
        self.token: str | None = config.get("token")
        self.include_code: bool = bool(config.get("include_code", True))
        self.max_file_size_kb: int = int(config.get("max_file_size_kb", 500))

    # ------------------------------------------------------------------

    def fetch(self, output_dir: Path) -> list[Path]:
        try:
            import git  # GitPython
        except ImportError as exc:
            raise RuntimeError(
                "gitpython is required for the 'github' source. "
                "Install it with: pip install gitpython"
            ) from exc

        written: list[Path] = []
        clone_url = self._authenticated_url()

        with tempfile.TemporaryDirectory(prefix="knowledge_github_") as tmpdir:
            repo_dir = Path(tmpdir) / "repo"
            repo = git.Repo.clone_from(clone_url, str(repo_dir), no_single_branch=True)
            remote_branches = {ref.remote_head for ref in repo.remotes["origin"].refs}

            for branch in self.branches:
                if branch not in remote_branches:
                    continue
                repo.git.checkout(branch)
                branch_out = output_dir / _slugify(branch)
                written.extend(self._process_tree(repo_dir, branch_out, branch))

        return written

    def _authenticated_url(self) -> str:
        """Inject token into HTTPS URL when a token is provided."""
        url = self.repo_url
        if self.token and url.startswith("https://"):
            url = url.replace("https://", f"https://{self.token}@", 1)
        return url

    def _process_tree(
        self, repo_dir: Path, output_dir: Path, branch: str
    ) -> list[Path]:
        written: list[Path] = []
        for src_file in sorted(repo_dir.rglob("*")):
            if not src_file.is_file():
                continue
            # Skip hidden directories / .git
            if any(part.startswith(".") for part in src_file.relative_to(repo_dir).parts):
                continue
            if src_file.stat().st_size > self.max_file_size_kb * 1024:
                continue

            ext = src_file.suffix.lower()
            rel = src_file.relative_to(repo_dir)
            sub_dir = output_dir / rel.parent if rel.parent != Path(".") else output_dir

            if ext in _MARKDOWN_EXTENSIONS:
                content = src_file.read_text(encoding="utf-8", errors="replace")
                # Prepend frontmatter if not already present
                if not content.startswith("---"):
                    meta = {
                        "source": self.repo_url,
                        "key": self.key,
                        "type": self.source_type,
                        "branch": branch,
                        "file": str(rel),
                    }
                    content = build_frontmatter(meta) + "\n" + content
                sub_dir.mkdir(parents=True, exist_ok=True)
                out = sub_dir / src_file.name
                out.write_text(content, encoding="utf-8")
                written.append(out)

            elif self.include_code and ext in _CODE_EXTENSIONS:
                lang = ext.lstrip(".")
                body = f"```{lang}\n{src_file.read_text(encoding='utf-8', errors='replace')}\n```"
                meta = {
                    "source": self.repo_url,
                    "key": self.key,
                    "type": self.source_type,
                    "branch": branch,
                    "file": str(rel),
                }
                path = write_markdown_page(
                    output_dir=sub_dir,
                    title=src_file.name,
                    body=body,
                    meta=meta,
                    filename=src_file.name + ".md",
                )
                written.append(path)

        return written

