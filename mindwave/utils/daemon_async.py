"""A module to manage background Async tasks.

A module for managing asynchronous tasks in a background thread and providing utilities for debugging
and handling exceptions in async functions.
"""

import traceback
from functools import wraps


def verbose(func: callable) -> callable:
    """A decorator for async functions that ensures exceptions are printed even when the task is not awaited.

    This decorator wraps async functions to provide immediate feedback about exceptions that occur during
    execution, rather than silently failing or only showing errors when explicitly awaited. This is
    particularly useful for background tasks or fire-and-forget operations where exceptions might
    otherwise go unnoticed.

    Args:
        func (Callable): The async function to be wrapped. Must be a coroutine function.

    Returns:
        Callable: A wrapped version of the input function that prints exceptions when they occur.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            print(f"Exception in asyncio task '{func.__name__}':\n{traceback.format_exc()}")
            raise

    return wrapper
