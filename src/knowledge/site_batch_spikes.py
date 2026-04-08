from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .site_spikes import SpikeReport, run_spikes


@dataclass
class BatchTargetReport:
    url: str
    best_strategy: str
    best_status: str
    useful_pages: int
    blocked_pages: int
    elapsed_seconds: float
    report_path: str


@dataclass
class BatchSpikeReport:
    generated_at: str
    target_count: int
    max_pages: int
    max_depth: int
    cdp_url: str | None
    targets: list[BatchTargetReport]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run site spikes across multiple documentation targets.")
    parser.add_argument("urls", nargs="*", help="Documentation URLs to evaluate")
    parser.add_argument("--urls-file", type=Path, help="Optional text file with one URL per line")
    parser.add_argument("--max-pages", type=int, default=12, help="Maximum pages per target strategy")
    parser.add_argument("--max-depth", type=int, default=1, help="Maximum crawl depth per target strategy")
    parser.add_argument("--cdp-url", default=None, help="Chrome DevTools URL used by browser-based strategies")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluation") / "site_spikes" / "batch",
        help="Directory where aggregated and per-target reports will be written",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    urls = _load_urls(args.urls, args.urls_file)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    targets: list[BatchTargetReport] = []
    for index, url in enumerate(urls, start=1):
        target_dir = args.output_dir / f"{index:02d}-{_safe_slug(url)}"
        report = run_spikes(
            url,
            max_pages=max(args.max_pages, 1),
            max_depth=max(args.max_depth, 0),
            cdp_url=args.cdp_url,
        )
        report_json = target_dir / "report.json"
        report_md = target_dir / "report.md"
        target_dir.mkdir(parents=True, exist_ok=True)
        report_json.write_text(json.dumps(_report_to_dict(report), indent=2), encoding="utf-8")
        report_md.write_text(_render_target_markdown(report), encoding="utf-8")
        best = report.strategies[0]
        targets.append(
            BatchTargetReport(
                url=url,
                best_strategy=best.name,
                best_status=best.status,
                useful_pages=best.useful_pages,
                blocked_pages=best.blocked_pages,
                elapsed_seconds=best.elapsed_seconds,
                report_path=str(report_md),
            )
        )

    batch_report = BatchSpikeReport(
        generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        target_count=len(targets),
        max_pages=max(args.max_pages, 1),
        max_depth=max(args.max_depth, 0),
        cdp_url=args.cdp_url,
        targets=targets,
    )
    json_path = args.output_dir / "report.json"
    markdown_path = args.output_dir / "report.md"
    json_path.write_text(json.dumps(asdict(batch_report), indent=2), encoding="utf-8")
    markdown_path.write_text(_render_batch_markdown(batch_report), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "markdown": str(markdown_path)}, indent=2))
    return 0


def _load_urls(raw_urls: list[str], urls_file: Path | None) -> list[str]:
    urls = [url.strip() for url in raw_urls if url.strip()]
    if urls_file:
        urls.extend(
            line.strip()
            for line in urls_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    if not deduped:
        raise SystemExit("at least one URL is required")
    return deduped


def _safe_slug(url: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in url)[:120] or "target"


def _render_target_markdown(report: SpikeReport) -> str:
    lines = [
        f"# {report.url}",
        "",
        "| Rank | Strategy | Status | Useful | Blocked | Seconds |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for index, strategy in enumerate(report.strategies, start=1):
        lines.append(
            f"| {index} | {strategy.name} | {strategy.status} | {strategy.useful_pages} | {strategy.blocked_pages} | {strategy.elapsed_seconds:.2f} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_batch_markdown(report: BatchSpikeReport) -> str:
    lines = [
        "# Site Batch Spike Report",
        "",
        f"- Generated at: `{report.generated_at}`",
        f"- Target count: `{report.target_count}`",
        f"- Max pages: `{report.max_pages}`",
        f"- Max depth: `{report.max_depth}`",
        f"- CDP URL: `{report.cdp_url or 'not set'}`",
        "",
        "| URL | Best strategy | Status | Useful | Blocked | Seconds | Report |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for target in report.targets:
        lines.append(
            f"| `{target.url}` | {target.best_strategy} | {target.best_status} | {target.useful_pages} | {target.blocked_pages} | {target.elapsed_seconds:.2f} | `{target.report_path}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _report_to_dict(report: SpikeReport) -> dict:
    return {
        "url": report.url,
        "generated_at": report.generated_at,
        "max_pages": report.max_pages,
        "max_depth": report.max_depth,
        "cdp_url": report.cdp_url,
        "python_version": report.python_version,
        "platform": report.platform,
        "strategies": [asdict(strategy) for strategy in report.strategies],
    }


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
