from typing import Callable, Any
from functools import wraps
from time import perf_counter
import logging

log = logging.getLogger("benchmark")


def time_benchmark(func: Callable[..., Any]) -> Any:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        start_time = perf_counter()
        log.info(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        log.info(f"Finished {func.__name__}")
        end_time = perf_counter()

        duration = end_time - start_time

        log.info(f"It took {duration:.2f} seconds to complete {func.__name__}")
        return result

    return wrapper
