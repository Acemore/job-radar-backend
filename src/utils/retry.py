import asyncio
import functools
from typing import Any, Callable

from src.exceptions.fetcher import FetcherError


def retry(attempts: int, delay: float) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except FetcherError as e:
                    if attempt == attempts:
                        raise e

                    await asyncio.sleep(delay)

        return wrapper

    return decorator
