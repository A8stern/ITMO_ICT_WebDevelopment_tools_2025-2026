from multiprocessing import Pool

from common.settings import get_limit, get_workers
from common.sum_utils import calculate_range_sum, expected_sum, measure, split_ranges


def calculate_sum(start: int, end: int) -> int:
    return calculate_range_sum(start, end)


def run(limit: int, workers: int) -> int:
    ranges = split_ranges(limit, workers)
    with Pool(processes=workers) as pool:
        results = pool.starmap(calculate_sum, ranges)
    return sum(results)


def main() -> None:
    limit = get_limit()
    workers = get_workers()
    result, elapsed = measure(lambda: run(limit, workers))
    print(f"Approach: multiprocessing")
    print(f"Limit: {limit}")
    print(f"Workers: {workers}")
    print(f"Result: {result}")
    print(f"Expected: {expected_sum(limit)}")
    print(f"Correct: {result == expected_sum(limit)}")
    print(f"Elapsed seconds: {elapsed:.6f}")


if __name__ == "__main__":
    main()
