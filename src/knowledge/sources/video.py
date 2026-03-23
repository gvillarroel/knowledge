from __future__ import annotations

from dataclasses import asdict, dataclass
from urllib.parse import parse_qs, urlparse

import requests
import yaml
from youtube_transcript_api import YouTubeTranscriptApi

from .base import SourceAdapter


YOUTUBE_OEMBED_URL = "https://www.youtube.com/oembed"


@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float


class VideoSource(SourceAdapter):
    def sync(self) -> dict[str, object]:
        video_url = self.config["url"]
        video_id = extract_video_id(video_url)

        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=self.config.get("languages", ["en"]))
        segments = [
            TranscriptSegment(
                text=snippet.text.strip(),
                start=float(snippet.start),
                duration=float(snippet.duration),
            )
            for snippet in transcript
        ]

        metadata = self._fetch_metadata(video_url, video_id)
        raw_payload = {
            "video_id": video_id,
            "url": video_url,
            "title": metadata.get("title"),
            "author_name": metadata.get("author_name"),
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "segments": [asdict(segment) for segment in segments],
        }

        self._clear_raw_dir()
        self.write_text(self.raw_dir / "transcript.md", _markdown_transcript(raw_payload, metadata))

        return self.finalize_sync(
            {
                "video_id": video_id,
                "segments": len(segments),
                "language_code": transcript.language_code,
                "raw_dir": str(self.raw_dir),
            }
        )

    def _fetch_metadata(self, video_url: str, video_id: str) -> dict[str, object]:
        response = requests.get(
            YOUTUBE_OEMBED_URL,
            params={"url": video_url, "format": "json"},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        payload.setdefault("video_id", video_id)
        payload.setdefault("url", video_url)
        return payload

    def _clear_raw_dir(self) -> None:
        for path in sorted(self.raw_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()


def extract_video_id(value: str) -> str:
    parsed = urlparse(value)
    if parsed.netloc in {"youtu.be", "www.youtu.be"}:
        return parsed.path.strip("/")
    query_id = parse_qs(parsed.query).get("v")
    if query_id:
        return query_id[0]
    if parsed.path.startswith("/shorts/"):
        return parsed.path.split("/shorts/", 1)[1].split("/", 1)[0]
    candidate = parsed.path.strip("/").split("/")[-1]
    if candidate:
        return candidate
    raise ValueError(f"could not extract video id from '{value}'")


def _markdown_transcript(payload: dict[str, object], metadata: dict[str, object]) -> str:
    title = payload.get("title") or payload["video_id"]
    author_name = payload.get("author_name") or "Unknown"
    segments = payload.get("segments", [])
    frontmatter = {
        "title": title,
        "video_id": payload["video_id"],
        "url": payload["url"],
        "author_name": author_name,
        "language": payload.get("language"),
        "language_code": payload.get("language_code"),
        "is_generated": payload.get("is_generated"),
        "segment_count": len(segments),
        "source_metadata": metadata,
    }
    lines = [
        "---",
        yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=False).strip(),
        "---",
        "",
        f"# {title}",
        "",
        f"- Author: {author_name}",
        f"- Language: {payload.get('language')} ({payload.get('language_code')})",
        f"- Auto-generated: {payload.get('is_generated')}",
        "",
        "## Transcript",
        "",
    ]
    for segment in segments:
        item = segment if isinstance(segment, dict) else asdict(segment)
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        lines.append(f"[{_format_timestamp(float(item.get('start', 0.0)))}] {text}")
    return "\n".join(lines).rstrip() + "\n"


def _format_timestamp(seconds: float) -> str:
    whole = int(seconds)
    hours, remainder = divmod(whole, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
