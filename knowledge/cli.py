"""Main CLI entry point for the knowledge base tool."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.table import Table

from . import store
from .sources.base import BaseSource

# Import source modules so they register in the registry
from .sources import web, confluence, jira, aha, github  # noqa: F401

console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """Knowledge base manager — store, update and export knowledge from multiple sources."""


# ---------------------------------------------------------------------------
# knowledge add
# ---------------------------------------------------------------------------


@main.command("add")
@click.argument("key")
@click.argument("url")
@click.option(
    "--type",
    "source_type",
    default="web",
    show_default=True,
    type=click.Choice(["web", "confluence", "jira", "aha", "github"], case_sensitive=False),
    help="Source type.",
)
@click.option("--branches", default="main", show_default=True, help="Comma-separated branches (github only).")
@click.option("--space", default="", help="Space key (confluence only).")
@click.option("--project", default="", help="Project key (jira only).")
@click.option("--product-id", default="", help="Product ID (aha only).")
@click.option("--subdomain", default="", help="Account subdomain (aha only).")
@click.option("--username", default="", envvar="KNOWLEDGE_USERNAME", help="Username / email.")
@click.option("--token", default="", envvar="KNOWLEDGE_TOKEN", help="API token or password.")
@click.option("--max-pages", default=50, show_default=True, type=int, help="Max pages/items to fetch.")
@click.option("--no-code", is_flag=True, default=False, help="Skip code files (github only).")
def cmd_add(
    key: str,
    url: str,
    source_type: str,
    branches: str,
    space: str,
    project: str,
    product_id: str,
    subdomain: str,
    username: str,
    token: str,
    max_pages: int,
    no_code: bool,
) -> None:
    """Add a new source KEY with the given URL."""
    source_type = source_type.lower()

    config: dict[str, Any] = {"url": url}

    if source_type == "web":
        config["max_pages"] = max_pages
    elif source_type == "confluence":
        _require("--space", space)
        _require("--username", username)
        _require("--token", token)
        config.update({"username": username, "token": token, "space": space, "max_pages": max_pages})
    elif source_type == "jira":
        _require("--project", project)
        _require("--username", username)
        _require("--token", token)
        config.update({"username": username, "token": token, "project": project, "max_issues": max_pages})
    elif source_type == "aha":
        _require("--subdomain", subdomain)
        _require("--product-id", product_id)
        _require("--token", token)
        config = {
            "subdomain": subdomain,
            "token": token,
            "product_id": product_id,
            "max_items": max_pages,
        }
    elif source_type == "github":
        branch_list = [b.strip() for b in branches.split(",") if b.strip()]
        config.update(
            {
                "branches": branch_list,
                "include_code": not no_code,
                "max_file_size_kb": 500,
            }
        )
        if token:
            config["token"] = token

    entry: dict[str, Any] = {"key": key, "type": source_type, **config}
    store.add_source(entry)
    console.print(f"[green]✓[/green] Added source [bold]{key}[/bold] (type: {source_type})")


# ---------------------------------------------------------------------------
# knowledge update
# ---------------------------------------------------------------------------


@main.command("update")
@click.argument("key", required=False, default=None)
def cmd_update(key: str | None) -> None:
    """Update one or all sources (download / refresh content)."""
    sources = store.list_sources()
    if not sources:
        console.print("[yellow]No sources registered. Use 'knowledge add' first.[/yellow]")
        return

    targets = [s for s in sources if key is None or s["key"] == key]
    if not targets:
        console.print(f"[red]Source {key!r} not found.[/red]")
        sys.exit(1)

    for entry in targets:
        k = entry["key"]
        console.print(f"Updating [bold]{k}[/bold] …")
        try:
            source_obj = BaseSource.from_entry(entry)
            output_dir = store.source_data_dir(k)
            paths = source_obj.fetch(output_dir)
            console.print(f"  [green]✓[/green] {len(paths)} file(s) written to {output_dir}")
        except Exception as exc:
            console.print(f"  [red]✗ Error updating {k!r}: {exc}[/red]")


# ---------------------------------------------------------------------------
# knowledge list
# ---------------------------------------------------------------------------


@main.command("list")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def cmd_list(as_json: bool) -> None:
    """List all registered sources."""
    sources = store.list_sources()
    if not sources:
        console.print("[yellow]No sources registered.[/yellow]")
        return

    if as_json:
        import json

        click.echo(json.dumps(sources, indent=2, default=str))
        return

    table = Table(title="Knowledge Sources", show_lines=True)
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("URL / Location")
    table.add_column("Added At", style="dim")

    for s in sources:
        url = s.get("url") or s.get("subdomain", "")
        table.add_row(s["key"], s.get("type", "?"), url, str(s.get("added_at", "")))

    console.print(table)


# ---------------------------------------------------------------------------
# knowledge show
# ---------------------------------------------------------------------------


@main.command("show")
@click.argument("key")
def cmd_show(key: str) -> None:
    """Show details of a single source."""
    entry = store.get_source(key)
    if entry is None:
        console.print(f"[red]Source {key!r} not found.[/red]")
        sys.exit(1)
    console.print(yaml.dump(entry, default_flow_style=False, allow_unicode=True))


# ---------------------------------------------------------------------------
# knowledge remove
# ---------------------------------------------------------------------------


@main.command("remove")
@click.argument("key")
@click.option("--yes", is_flag=True, default=False, help="Skip confirmation prompt.")
def cmd_remove(key: str, yes: bool) -> None:
    """Remove a source from the registry."""
    if not yes:
        click.confirm(f"Remove source {key!r}?", abort=True)
    removed = store.remove_source(key)
    if removed:
        console.print(f"[green]✓[/green] Removed source [bold]{key}[/bold]")
    else:
        console.print(f"[red]Source {key!r} not found.[/red]")
        sys.exit(1)


# ---------------------------------------------------------------------------
# knowledge export
# ---------------------------------------------------------------------------


@main.command("export")
@click.argument("key", required=False, default=None)
@click.option(
    "--output",
    "-o",
    default=".",
    show_default=True,
    type=click.Path(file_okay=False, writable=True),
    help="Output directory.",
)
def cmd_export(key: str | None, output: str) -> None:
    """Export stored Markdown files to OUTPUT directory.

    If KEY is omitted, all sources are exported.
    """
    sources = store.list_sources()
    if not sources:
        console.print("[yellow]No sources registered.[/yellow]")
        return

    targets = [s for s in sources if key is None or s["key"] == key]
    if not targets:
        console.print(f"[red]Source {key!r} not found.[/red]")
        sys.exit(1)

    import shutil

    out_root = Path(output)
    out_root.mkdir(parents=True, exist_ok=True)

    for entry in targets:
        k = entry["key"]
        src_dir = store.DATA_DIR / k
        if not src_dir.exists():
            console.print(f"  [yellow]No data for {k!r} — run 'knowledge update {k}' first.[/yellow]")
            continue
        dest = out_root / k
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src_dir, dest)
        count = sum(1 for _ in dest.rglob("*.md"))
        console.print(f"  [green]✓[/green] {k}: {count} file(s) exported to {dest}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _require(option: str, value: str) -> None:
    if not value:
        raise click.UsageError(f"{option} is required for this source type.")
