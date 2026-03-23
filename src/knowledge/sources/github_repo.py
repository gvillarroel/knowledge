from __future__ import annotations

import subprocess
from pathlib import Path

from .base import SourceAdapter


TEXT_SUFFIXES = {
    ".c",
    ".cc",
    ".cfg",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


class GitHubRepoSource(SourceAdapter):
    def sync(self) -> dict[str, object]:
        repo_url = self.config["repo_url"]
        branches = self.source.get("_sync_branches") or self.config.get("branches", ["HEAD"])
        cache_repo = self.cache_dir / "repo.git"

        if cache_repo.exists():
            self._git(["fetch", "--all", "--prune"], cwd=cache_repo)
        else:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._git(["clone", "--mirror", repo_url, str(cache_repo)], cwd=self.cache_dir)

        count = 0
        for branch in branches:
            tree_root = self.raw_dir / branch
            tree_root.mkdir(parents=True, exist_ok=True)
            files = self._git_output(["ls-tree", "-r", "--name-only", branch], cwd=cache_repo).splitlines()
            for file_name in files:
                rel_path = Path(file_name)
                if rel_path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                output_path = tree_root / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                content = self._git_output(["show", f"{branch}:{file_name}"], cwd=cache_repo)
                output_path.write_text(content, encoding="utf-8", errors="replace")
                count += 1

        return self.finalize_sync(
            {
                "branches": branches,
                "files": count,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _git(self, args: list[str], cwd: Path) -> None:
        subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def _git_output(self, args: list[str], cwd: Path) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout
