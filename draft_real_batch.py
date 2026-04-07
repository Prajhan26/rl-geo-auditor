from __future__ import annotations

import json
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import Request, urlopen

from inference import build_issue_candidates
from server.models import PageData


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.h1 = ""
        self.headers: List[str] = []
        self.paragraphs: List[str] = []
        self._active_tag: str | None = None
        self._buffer: List[str] = []
        self._script_type = ""
        self._script_buffer: List[str] = []
        self.schema_payloads: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        if tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.meta_description = (attrs_dict.get("content") or "").strip()

        if tag in {"title", "h1", "h2", "h3", "p"}:
            self._active_tag = tag
            self._buffer = []

        if tag == "script":
            self._script_type = (attrs_dict.get("type") or "").lower()
            self._script_buffer = []

    def handle_data(self, data: str) -> None:
        if self._active_tag is not None:
            self._buffer.append(data)
        if self._script_type == "application/ld+json":
            self._script_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._active_tag:
            text = clean_text("".join(self._buffer))
            if tag == "title" and text:
                self.title = text
            elif tag == "h1" and text and not self.h1:
                self.h1 = text
            elif tag in {"h2", "h3"} and text:
                self.headers.append(f"{tag.upper()}: {text}")
            elif tag == "p" and text:
                self.paragraphs.append(text)
            self._active_tag = None
            self._buffer = []

        if tag == "script" and self._script_type == "application/ld+json":
            payload = clean_text("".join(self._script_buffer))
            if payload:
                self.schema_payloads.append(payload)
            self._script_type = ""
            self._script_buffer = []


def clean_text(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:  # noqa: S310 - user-provided URLs are intentional here
        return response.read().decode("utf-8", errors="ignore")


def collect_schema_types(payloads: List[str]) -> List[str]:
    schema_types = set()
    for payload in payloads:
        for match in re.findall(r'"@type"\s*:\s*"([^"]+)"', payload):
            schema_types.add(match)
        for match in re.findall(r'"@type"\s*:\s*\[([^\]]+)\]', payload):
            for item in re.findall(r'"([^"]+)"', match):
                schema_types.add(item)
    return sorted(schema_types)


def detect_author(html: str) -> bool:
    lowered = html.lower()
    return any(
        marker in lowered
        for marker in (
            'rel="author"',
            "author",
            "datepublished",
            "byauthor",
            "article:author",
        )
    )


def detect_date(html: str) -> bool:
    lowered = html.lower()
    return any(
        marker in lowered
        for marker in ("datepublished", "datemodified", "<time", "published", "updated")
    )


def detect_sources(html: str, headers: List[str]) -> tuple[bool, int]:
    lowered = html.lower()
    source_section = any(
        marker in lowered for marker in ("references", "further reading", "sources", "citations")
    ) or any(
        any(marker in header.lower() for marker in ("references", "further reading", "sources"))
        for header in headers
    )

    anchors = re.findall(r"<a\s[^>]*href=", lowered)
    if source_section:
        # Use a conservative cap because global anchors include nav/footer links.
        return True, min(max(len(anchors) // 20, 1), 8)

    return False, 0


def pick_first_paragraph(paragraphs: List[str]) -> str:
    for paragraph in paragraphs:
        if len(paragraph.split()) >= 8:
            return paragraph
    return paragraphs[0] if paragraphs else ""


def estimate_word_count(paragraphs: List[str], headers: List[str]) -> int:
    text = " ".join(paragraphs + headers)
    return len(text.split())


def draft_row(seed: Dict[str, Any]) -> Dict[str, Any]:
    html = fetch_html(seed["url"])
    parser = PageParser()
    parser.feed(html)

    first_paragraph = pick_first_paragraph(parser.paragraphs)
    headers = parser.headers[:12]
    schema_types = collect_schema_types(parser.schema_payloads)
    has_author = detect_author(html)
    has_date = detect_date(html)
    has_sources, source_count = detect_sources(html, headers)
    word_count = estimate_word_count(parser.paragraphs, headers)

    page = PageData(
        url=seed["url"],
        target_query=seed["target_query"],
        title_tag=parser.title,
        meta_description=parser.meta_description,
        h1=parser.h1,
        first_paragraph=first_paragraph,
        word_count=word_count,
        headers=headers,
        schema_types=schema_types,
        has_author=has_author,
        has_date=has_date,
        has_sources=has_sources,
        source_count=source_count,
    )

    issues = [
        {"type": candidate.issue_type, "severity": candidate.severity}
        for candidate in build_issue_candidates(page)
    ]

    return {
        "page_id": seed["page_id"],
        "difficulty": seed.get("difficulty", ""),
        "url": seed["url"],
        "target_query": seed["target_query"],
        "title_tag": page.title_tag,
        "meta_description": page.meta_description,
        "h1": page.h1,
        "first_paragraph": page.first_paragraph,
        "word_count": page.word_count,
        "headers": page.headers,
        "schema_types": page.schema_types,
        "has_author": page.has_author,
        "has_date": page.has_date,
        "has_sources": page.has_sources,
        "source_count": page.source_count,
        "issues": issues,
        "review_notes": [
            "Draft generated automatically from live HTML.",
            "Review author/date/source detection manually.",
            "Review schema-based issue labels manually.",
        ],
    }


def failed_row(seed: Dict[str, Any], error: Exception) -> Dict[str, Any]:
    return {
        "page_id": seed["page_id"],
        "difficulty": seed.get("difficulty", ""),
        "url": seed["url"],
        "target_query": seed["target_query"],
        "fetch_error": str(error),
        "review_notes": [
            "Automatic draft failed for this URL.",
            "Check whether the URL is valid, blocked, or too dynamic for the current parser.",
            "Replace or retry this candidate after manual review.",
        ],
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3 draft_real_batch.py <seed_file.json> <output_file.json>"
        )

    seed_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    seeds = json.loads(seed_path.read_text(encoding="utf-8"))
    rows = []
    for seed in seeds:
        print(f"[FETCH] {seed['url']}")
        try:
            rows.append(draft_row(seed))
        except Exception as error:  # noqa: BLE001 - keep batch collection moving
            print(f"[SKIP] {seed['url']} -> {error}")
            rows.append(failed_row(seed, error))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"[SAVED] {output_path}")


if __name__ == "__main__":
    main()
