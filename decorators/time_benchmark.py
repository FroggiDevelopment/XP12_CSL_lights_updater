"""
Copyright (C) 2025  Richard J.M. Muller / Froggi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import logging

from typing import Callable, Any
from functools import wraps
from time import perf_counter

from helpers.init_logging import init_logging

# Setup logging
init_logging()
log = logging.getLogger(__name__)


def time_benchmark(func: Callable[..., Any]) -> Any:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        start_time = perf_counter()
        log.debug(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        end_time = perf_counter()
        log.debug(f"Finished {func.__name__}")

        duration = end_time - start_time

        log.info(f"It took {duration:.2f} seconds to complete {func.__name__}")
        return result

    return wrapper


def named_time_benchmark(argument: str = ""):
    def time_benchmark(func: Callable[..., Any]) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            start_time = perf_counter()
            log.debug(f"Starting {func.__name__}")
            result = func(*args, **kwargs)
            log.debug(f"Finished {func.__name__}")
            end_time = perf_counter()

            duration = end_time - start_time
            if argument != "":
                log.info(
                    f"It took {duration:.2f} seconds to complete {argument}")
            else:
                log.info(
                    f"It took {duration:.2f} seconds to complete {func.__name__}")
            return result

        return wrapper

    return time_benchmark
