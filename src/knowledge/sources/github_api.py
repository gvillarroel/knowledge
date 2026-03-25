"""GitHub REST API client for browsing repos, issues, PRs, and discussions.

Requires a ``GITHUB_TOKEN`` environment variable or a credential stored via
``know set credential github_token <TOKEN>``.
"""

from __future__ import annotations

from typing import Any

import requests


_API_BASE = "https://api.github.com"
_ACCEPT = "application/vnd.github+json"
_API_VERSION = "2022-11-28"


def _headers(token: str) -> dict[str, str]:
    return {
        "Accept": _ACCEPT,
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": _API_VERSION,
    }


# ── Repos ────────────────────────────────────────────────────────────────

def list_user_repos(
    token: str,
    *,
    sort: str = "updated",
    direction: str = "desc",
    per_page: int = 50,
    page: int = 1,
    affiliation: str = "owner,collaborator,organization_member",
) -> list[dict[str, Any]]:
    """List repositories the authenticated user has interacted with."""
    response = requests.get(
        f"{_API_BASE}/user/repos",
        headers=_headers(token),
        params={
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page,
            "affiliation": affiliation,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# ── Issues & PRs ─────────────────────────────────────────────────────────

def list_repo_issues(
    token: str,
    owner: str,
    repo: str,
    *,
    state: str = "open",
    per_page: int = 50,
    page: int = 1,
) -> list[dict[str, Any]]:
    """List issues for a repository (includes PRs unless filtered)."""
    response = requests.get(
        f"{_API_BASE}/repos/{owner}/{repo}/issues",
        headers=_headers(token),
        params={"state": state, "per_page": per_page, "page": page},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def list_repo_pulls(
    token: str,
    owner: str,
    repo: str,
    *,
    state: str = "open",
    per_page: int = 50,
    page: int = 1,
) -> list[dict[str, Any]]:
    """List pull requests for a repository."""
    response = requests.get(
        f"{_API_BASE}/repos/{owner}/{repo}/pulls",
        headers=_headers(token),
        params={"state": state, "per_page": per_page, "page": page},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def list_repo_discussions(
    token: str,
    owner: str,
    repo: str,
    *,
    per_page: int = 20,
) -> list[dict[str, Any]]:
    """List discussions for a repository via GitHub GraphQL API."""
    query = """
    query($owner: String!, $repo: String!, $first: Int!) {
      repository(owner: $owner, name: $repo) {
        discussions(first: $first, orderBy: {field: UPDATED_AT, direction: DESC}) {
          nodes {
            number
            title
            body
            url
            createdAt
            updatedAt
            author { login }
            category { name }
            comments(first: 10) {
              nodes {
                body
                createdAt
                author { login }
              }
            }
          }
        }
      }
    }
    """
    response = requests.post(
        "https://api.github.com/graphql",
        headers=_headers(token),
        json={
            "query": query,
            "variables": {"owner": owner, "repo": repo, "first": per_page},
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    repo_data = (data.get("data") or {}).get("repository") or {}
    discussions = (repo_data.get("discussions") or {}).get("nodes") or []
    return discussions


def get_issue_comments(
    token: str,
    owner: str,
    repo: str,
    issue_number: int,
    *,
    per_page: int = 50,
) -> list[dict[str, Any]]:
    """Get comments on an issue or PR."""
    response = requests.get(
        f"{_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/comments",
        headers=_headers(token),
        params={"per_page": per_page},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_pr_detail(
    token: str,
    owner: str,
    repo: str,
    pr_number: int,
) -> dict[str, Any]:
    """Get detailed information about a pull request."""
    response = requests.get(
        f"{_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}",
        headers=_headers(token),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# ── Activity helpers ─────────────────────────────────────────────────────

def list_repo_activity(
    token: str,
    owner: str,
    repo: str,
    *,
    state: str = "open",
    per_page: int = 30,
    include_discussions: bool = True,
) -> list[dict[str, Any]]:
    """Return a unified list of issues, PRs, and discussions for a repo.

    Each item includes a ``kind`` field: ``issue``, ``pull_request``, or
    ``discussion``.
    """
    items: list[dict[str, Any]] = []

    # Issues (includes PRs on GitHub API)
    raw_issues = list_repo_issues(token, owner, repo, state=state, per_page=per_page)
    for issue in raw_issues:
        kind = "pull_request" if issue.get("pull_request") else "issue"
        items.append({
            "kind": kind,
            "number": issue["number"],
            "title": issue.get("title", ""),
            "state": issue.get("state", "open"),
            "user": (issue.get("user") or {}).get("login", ""),
            "created_at": issue.get("created_at", ""),
            "updated_at": issue.get("updated_at", ""),
            "body": issue.get("body") or "",
            "labels": [l.get("name", "") for l in issue.get("labels", [])],
            "url": issue.get("html_url", ""),
            "comments_count": issue.get("comments", 0),
        })

    # Discussions
    if include_discussions:
        try:
            discussions = list_repo_discussions(token, owner, repo, per_page=per_page)
            for disc in discussions:
                items.append({
                    "kind": "discussion",
                    "number": disc.get("number", 0),
                    "title": disc.get("title", ""),
                    "state": "open",
                    "user": (disc.get("author") or {}).get("login", ""),
                    "created_at": disc.get("createdAt", ""),
                    "updated_at": disc.get("updatedAt", ""),
                    "body": disc.get("body") or "",
                    "labels": [],
                    "url": disc.get("url", ""),
                    "comments_count": len((disc.get("comments") or {}).get("nodes") or []),
                    "category": (disc.get("category") or {}).get("name", ""),
                    "_discussion_comments": (disc.get("comments") or {}).get("nodes") or [],
                })
        except Exception:
            pass  # Discussions API may not be available for all repos

    return items


def render_issue_thread_markdown(
    token: str,
    owner: str,
    repo: str,
    item: dict[str, Any],
) -> str:
    """Render a full issue/PR/discussion thread as Markdown."""
    kind = item.get("kind", "issue")
    number = item.get("number", 0)
    title = item.get("title", "Untitled")
    body = item.get("body") or ""
    user = item.get("user", "unknown")
    created = item.get("created_at", "")
    labels = item.get("labels", [])

    kind_label = {"issue": "Issue", "pull_request": "Pull Request", "discussion": "Discussion"}.get(kind, kind)

    lines = [
        f"# [{kind_label} #{number}] {title}",
        "",
        f"- Author: @{user}",
        f"- Created: {created}",
        f"- State: {item.get('state', 'open')}",
    ]
    if labels:
        lines.append(f"- Labels: {', '.join(labels)}")
    if item.get("url"):
        lines.append(f"- URL: {item['url']}")

    if body.strip():
        lines.extend(["", "## Description", "", body.strip()])

    # Fetch and render comments
    if kind == "discussion":
        comments = item.get("_discussion_comments", [])
        if comments:
            lines.extend(["", "## Comments", ""])
            for comment in comments:
                author = (comment.get("author") or {}).get("login", "unknown")
                date = comment.get("createdAt", "")
                cbody = comment.get("body") or ""
                lines.extend([
                    f"### @{author} ({date})",
                    "",
                    cbody.strip(),
                    "",
                ])
    else:
        try:
            comments = get_issue_comments(token, owner, repo, number, per_page=30)
            if comments:
                lines.extend(["", "## Comments", ""])
                for comment in comments:
                    author = (comment.get("user") or {}).get("login", "unknown")
                    date = comment.get("created_at", "")
                    cbody = comment.get("body") or ""
                    lines.extend([
                        f"### @{author} ({date})",
                        "",
                        cbody.strip(),
                        "",
                    ])
        except Exception:
            lines.extend(["", "_Could not load comments._"])

    return "\n".join(lines).rstrip() + "\n"
