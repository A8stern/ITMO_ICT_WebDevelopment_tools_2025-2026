from dataclasses import dataclass
from html.parser import HTMLParser
from time import perf_counter

import requests


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


@dataclass
class ParsedTitle:
    url: str
    title: str
    elapsed_seconds: float
    status_code: int


def extract_title(html: str) -> str:
    parser = TitleParser()
    parser.feed(html)
    return parser.title or "Untitled page"


def parse_url(url: str, timeout: int = 15) -> ParsedTitle:
    started_at = perf_counter()
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "Lab3FinanceParser/1.0"},
    )
    response.raise_for_status()
    title = extract_title(response.text)
    return ParsedTitle(
        url=url,
        title=title,
        elapsed_seconds=perf_counter() - started_at,
        status_code=response.status_code,
    )
