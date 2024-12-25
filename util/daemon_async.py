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
        asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self._loop)
