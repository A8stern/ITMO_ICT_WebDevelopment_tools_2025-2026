import threading

from common.settings import get_limit, get_workers
from common.sum_utils import calculate_range_sum, expected_sum, measure, split_ranges


def calculate_sum(start: int, end: int) -> int:
    return calculate_range_sum(start, end)


def run(limit: int, workers: int) -> int:
    ranges = split_ranges(limit, workers)
    results = [0 for _ in ranges]
    threads = []

    def worker(index: int, start: int, end: int) -> None:
        results[index] = calculate_sum(start, end)

    for index, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=worker, args=(index, start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)


def main() -> None:
    limit = get_limit()
    workers = get_workers()
    result, elapsed = measure(lambda: run(limit, workers))
    print(f"Approach: threading")
    print(f"Limit: {limit}")
    print(f"Workers: {workers}")
    print(f"Result: {result}")
    print(f"Expected: {expected_sum(limit)}")
    print(f"Correct: {result == expected_sum(limit)}")
    print(f"Elapsed seconds: {elapsed:.6f}")


if __name__ == "__main__":
    main()
