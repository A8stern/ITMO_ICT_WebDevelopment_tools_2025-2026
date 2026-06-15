from time import perf_counter
from typing import Callable


def split_ranges(limit: int, workers: int) -> list[tuple[int, int]]:
    step = limit // workers
    ranges = []
    start = 1
    for index in range(workers):
        end = start + step - 1
        if index == workers - 1:
            end = limit
        ranges.append((start, end))
        start = end + 1
    return ranges


def calculate_range_sum(start: int, end: int) -> int:
    count = end - start + 1
    return (start + end) * count // 2


def expected_sum(limit: int) -> int:
    return limit * (limit + 1) // 2


def measure(function: Callable[[], int]) -> tuple[int, float]:
    started_at = perf_counter()
    result = function()
    finished_at = perf_counter()
    return result, finished_at - started_at
