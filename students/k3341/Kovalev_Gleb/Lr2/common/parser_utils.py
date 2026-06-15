import asyncio
from html.parser import HTMLParser
from pathlib import Path
from time import perf_counter
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import aiohttp


class TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.parts.append(data.strip())

    @property
    def title(self) -> str:
        return " ".join(part for part in self.parts if part).strip()


def extract_title(html: str) -> str:
    parser = TitleParser()
    parser.feed(html)
    return parser.title or "Untitled page"


def fetch_sync(url: str, timeout: int = 10) -> str:
    request = Request(url, headers={"User-Agent": "Lab2FinanceParser/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


async def fetch_async(url: str, session: aiohttp.ClientSession, timeout: int = 10) -> str:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return await asyncio.to_thread(Path(parsed.path).read_text, encoding="utf-8")
    async with session.get(url, timeout=timeout) as response:
        response.raise_for_status()
        return await response.text(errors="ignore")


def split_items(items: list[str], workers: int) -> list[list[str]]:
    chunks = [[] for _ in range(workers)]
    for index, item in enumerate(items):
        chunks[index % workers].append(item)
    return [chunk for chunk in chunks if chunk]


def timed_title_from_html(html: str) -> tuple[str, float]:
    started_at = perf_counter()
    title = extract_title(html)
    return title, perf_counter() - started_at
