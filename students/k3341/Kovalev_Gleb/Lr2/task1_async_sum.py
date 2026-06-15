import asyncio

from common.settings import get_limit, get_workers
from common.sum_utils import calculate_range_sum, expected_sum, measure, split_ranges


async def calculate_sum(start: int, end: int) -> int:
    await asyncio.sleep(0)
    return calculate_range_sum(start, end)


async def run_async(limit: int, workers: int) -> int:
    ranges = split_ranges(limit, workers)
    tasks = [calculate_sum(start, end) for start, end in ranges]
    results = await asyncio.gather(*tasks)
    return sum(results)


def run(limit: int, workers: int) -> int:
    return asyncio.run(run_async(limit, workers))


def main() -> None:
    limit = get_limit()
    workers = get_workers()
    result, elapsed = measure(lambda: run(limit, workers))
    print(f"Approach: async")
    print(f"Limit: {limit}")
    print(f"Workers: {workers}")
    print(f"Result: {result}")
    print(f"Expected: {expected_sum(limit)}")
    print(f"Correct: {result == expected_sum(limit)}")
    print(f"Elapsed seconds: {elapsed:.6f}")


if __name__ == "__main__":
    main()
