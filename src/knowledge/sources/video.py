from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from urllib.parse import parse_qs, urlparse

import requests
from youtube_transcript_api import YouTubeTranscriptApi

from .base import SourceAdapter


YOUTUBE_OEMBED_URL = "https://www.youtube.com/oembed"


@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float


class VideoSource(SourceAdapter):
    """Adapter that fetches YouTube transcripts via the Transcript API."""

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

        title = raw_payload.get("title") or raw_payload.get("video_id") or self.source["id"]
        author_name = raw_payload.get("author_name") or "Unknown"
        frontmatter = {
            "title": title,
            "knowledge_key": self.source["key"],
            "source_id": self.source["id"],
            "source_type": self.source["type"],
            "video_id": raw_payload.get("video_id"),
            "url": raw_payload.get("url"),
            "author_name": author_name,
            "language": raw_payload.get("language"),
            "language_code": raw_payload.get("language_code"),
            "is_generated": raw_payload.get("is_generated"),
            "segment_count": len(segments),
            "source_metadata": metadata,
        }
        lines = [
            f"# {title}",
            "",
            f"- Author: {author_name}",
            f"- Language: {raw_payload.get('language')} ({raw_payload.get('language_code')})",
            f"- Auto-generated: {raw_payload.get('is_generated')}",
            "",
            "## Transcript",
            "",
        ]
        for segment in raw_payload["segments"]:
            text = str(segment.get("text", "")).strip()
            if not text:
                continue
            lines.append(f"[{_format_timestamp(float(segment.get('start', 0.0)))}] {text}")

        self.clear_source_dir()
        self.write_markdown(self.raw_dir / "transcript.md", frontmatter, "\n".join(lines).rstrip())

        return self.finalize_sync(
            {
                "video_id": video_id,
                "segments": len(segments),
                "language_code": transcript.language_code,
                "documents": 1,
                "library_dir": str(self.raw_dir),
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


def _format_timestamp(seconds: float) -> str:
    whole = int(seconds)
    hours, remainder = divmod(whole, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
