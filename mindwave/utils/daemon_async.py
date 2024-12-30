import asyncio
import threading
import traceback
import warnings
from functools import wraps


class DaemonAsync:
    def __init__(self):

        warnings.warn("DaemonAsync is deprecated and will be removed in a future release.", DeprecationWarning, 2)
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self.__start_event_loop, daemon=True)
        self._thread.start()

    def __start_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _start_task(self, func, *args, **kwargs):
        """Start an asyncio task in the background."""
        if not self._loop.is_running():
            raise RuntimeError("Event loop is not running.")
        return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self._loop)


def verbose(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"Exception in asyncio task '{func.__name__}':\n{traceback.format_exc()}")

    return wrapper
