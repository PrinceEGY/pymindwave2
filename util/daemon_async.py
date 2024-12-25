import asyncio
import threading


class DaemonAsync:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._start_event_loop, daemon=True)
        self._thread.start()

    def _start_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def start_task(self, func, *args, **kwargs):
        """Start an asyncio task in the background."""
        if not self._loop.is_running():
            raise RuntimeError("Event loop is not running.")
        return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self._loop)


def daemon_task(func):
    """
    Decorator to start and handle an asyncio task

    This is used so that the user can call the function as a normal sync function
    """

    def wrapper(self: DaemonAsync, *args, **kwargs):
        future = self.start_task(func, self, *args, **kwargs)
        return future.result()  # Calling result will raise any exceptions that were thrown in the task

    return wrapper
