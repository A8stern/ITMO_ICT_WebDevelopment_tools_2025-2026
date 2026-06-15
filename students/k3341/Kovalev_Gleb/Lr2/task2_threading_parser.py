import argparse
import threading
from time import perf_counter

from common.db import init_database, save_title
from common.parser_utils import fetch_sync, split_items, timed_title_from_html
from common.settings import get_db_url, get_local_urls, get_public_urls, get_workers


def parse_and_save(url: str) -> dict:
    started_at = perf_counter()
    html = fetch_sync(url)
    title, parsing_elapsed = timed_title_from_html(html)
    elapsed = perf_counter() - started_at
    notification_id = save_title(DB_URL, url, title, "threading", elapsed)
    return {
        "url": url,
        "title": title,
        "notification_id": notification_id,
        "elapsed": elapsed,
        "parsing_elapsed": parsing_elapsed,
    }


def worker(urls: list[str], results: list[dict], lock: threading.Lock) -> None:
    for url in urls:
        result = parse_and_save(url)
        with lock:
            results.append(result)
            print(f"threading saved: {result['title']} -> notification {result['notification_id']}")


def run(urls: list[str], workers: int, db_url: str) -> tuple[list[dict], float]:
    global DB_URL
    DB_URL = db_url
    init_database(db_url)
    chunks = split_items(urls, workers)
    results = []
    lock = threading.Lock()
    threads = []
    started_at = perf_counter()

    for chunk in chunks:
        thread = threading.Thread(target=worker, args=(chunk, results, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results, perf_counter() - started_at


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--workers", type=int, default=get_workers())
    parser.add_argument("--db-url", default=get_db_url())
    args = parser.parse_args()
    urls = get_local_urls() if args.local else get_public_urls()
    results, elapsed = run(urls, args.workers, args.db_url)
    print(f"Approach: threading")
    print(f"URLs: {len(urls)}")
    print(f"Saved: {len(results)}")
    print(f"Elapsed seconds: {elapsed:.6f}")


DB_URL = get_db_url()


if __name__ == "__main__":
    main()
