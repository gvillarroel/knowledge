from __future__ import annotations

from .sources.aha import AhaSource
from .sources.arxiv import ArxivSource
from .sources.base import SourceAdapter
from .sources.confluence import ConfluenceSource
from .sources.crawl4ai_site import SiteSource
from .sources.github_repo import GitHubRepoSource
from .sources.google_releases import GoogleReleasesSource
from .sources.jira import JiraSource
from .sources.television import TelevisionSource
from .sources.video import VideoSource


SOURCE_TYPES: dict[str, type[SourceAdapter]] = {
    "aha": AhaSource,
    "arxiv": ArxivSource,
    "confluence": ConfluenceSource,
    "github": GitHubRepoSource,
    "google_releases": GoogleReleasesSource,
    "jira": JiraSource,
    "site": SiteSource,
    "television": TelevisionSource,
    "video": VideoSource,
}


def create_source_adapter(source: dict, store) -> SourceAdapter:
    """Instantiate the correct :class:`SourceAdapter` for *source*."""
    source_type = source["type"]
    try:
        adapter_type = SOURCE_TYPES[source_type]
    except KeyError as exc:
        supported = ", ".join(sorted(SOURCE_TYPES))
        raise ValueError(f"unsupported source type '{source_type}'. Supported: {supported}") from exc
    return adapter_type(source, store)
