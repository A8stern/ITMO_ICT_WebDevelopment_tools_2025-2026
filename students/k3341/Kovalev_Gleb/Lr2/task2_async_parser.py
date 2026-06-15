import argparse
import asyncio
from time import perf_counter

import aiohttp

from common.db import init_database, save_title
from common.parser_utils import fetch_async, timed_title_from_html
from common.settings import get_db_url, get_local_urls, get_public_urls, get_workers


async def parse_and_save(url: str) -> dict:
    started_at = perf_counter()
    html = await fetch_async(url, SESSION)
    title, parsing_elapsed = timed_title_from_html(html)
    elapsed = perf_counter() - started_at
    notification_id = await asyncio.to_thread(save_title, DB_URL, url, title, "async", elapsed)
    return {
        "url": url,
        "title": title,
        "notification_id": notification_id,
        "elapsed": elapsed,
        "parsing_elapsed": parsing_elapsed,
    }


async def run_async(urls: list[str], workers: int, db_url: str) -> tuple[list[dict], float]:
    global DB_URL
    global SESSION
    DB_URL = db_url
    init_database(db_url)
    connector = aiohttp.TCPConnector(limit=workers)
    started_at = perf_counter()
    async with aiohttp.ClientSession(connector=connector) as session:
        SESSION = session
        tasks = [parse_and_save(url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results, perf_counter() - started_at


def run(urls: list[str], workers: int, db_url: str) -> tuple[list[dict], float]:
    return asyncio.run(run_async(urls, workers, db_url))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--workers", type=int, default=get_workers())
    parser.add_argument("--db-url", default=get_db_url())
    args = parser.parse_args()
    urls = get_local_urls() if args.local else get_public_urls()
    results, elapsed = run(urls, args.workers, args.db_url)
    for result in results:
        print(f"async saved: {result['title']} -> notification {result['notification_id']}")
    print(f"Approach: async")
    print(f"URLs: {len(urls)}")
    print(f"Saved: {len(results)}")
    print(f"Elapsed seconds: {elapsed:.6f}")


DB_URL = get_db_url()
SESSION = None


if __name__ == "__main__":
    main()
