import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_LIMIT = 10_000_000_000_000
DEFAULT_WORKERS = max(2, min(8, os.cpu_count() or 2))
DEFAULT_DB_URL = "sqlite:////private/tmp/lab2_finance_lab1_compatible.db"


def get_limit() -> int:
    return int(os.getenv("LAB2_SUM_LIMIT", str(DEFAULT_LIMIT)))


def get_workers() -> int:
    return int(os.getenv("LAB2_WORKERS", str(DEFAULT_WORKERS)))


def get_db_url() -> str:
    return os.getenv("LAB2_DB_URL", DEFAULT_DB_URL)


def get_public_urls() -> list[str]:
    urls_file = BASE_DIR / "urls.txt"
    return [
        line.strip()
        for line in urls_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def get_local_urls() -> list[str]:
    pages_dir = BASE_DIR / "sample_pages"
    return [
        page.resolve().as_uri()
        for page in sorted(pages_dir.glob("*.html"))
    ]
