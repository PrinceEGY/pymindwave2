from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from queue import Queue
import threading
from typing import Callable

from .logger import Logger


class EventType(Enum):
    ConnectorData = 1  # Raw data from the connector only json parsed
    Timeout = 2
    HeadsetData = 3  # Parsed data from the headset contains all streamed attribtues (see Data class)
    Blink = 4
    HeadsetStatus = 5
    SignalQuality = 6


class EventManager:
    """
    Event manager that allows for event-driven programming with multiple listeners.

    Each listener is guaranteed to receive events in order, but different listeners process independently.

    The manager uses a thread pool to process events, which makes it scalable for a large number of
    callbacks without creating excessive threads. Each callback gets its own queue, ensuring that
    events are processed in the order they were received, but different callbacks can process events
    at different speeds without blocking each other.
    """

    def __init__(self, max_workers: int = None):
        """
        Initialize event manager with thread pool.

        Args:
            max_workers: Maximum number of threads to use
        """
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self._listeners = defaultdict(list)
        self._queues = defaultdict(Queue)
        self._locks = defaultdict(threading.Lock)
        self._thread_pool = ThreadPoolExecutor(max_workers)

    def add_listener(self, event_type: EventType, listener: Callable) -> None:
        """
        Register a callback function for a specific event type.
        """
        if listener in self._listeners[event_type]:
            self._logger.info("Listener already exists")
            return

        self._listeners[event_type].append(listener)
        self._queues[listener] = Queue()
        self._locks[listener] = threading.Lock()

    def remove_listener(self, event_type: EventType, listener: Callable) -> None:
        """
        Unregister a callback function for a specific event type.
        """
        if listener not in self._listeners[event_type]:
            self._logger.info("Listener does not exist")
            return

        self._listeners[event_type].remove(listener)
        self._queues.pop(listener)
        self._locks.pop(listener)

    def trigger(self, event_type: EventType, *args, **kwargs) -> None:
        """
        Trigger event for all registered callbacks.
        Events are processed in order per callback.

        Args:
            event_type: Event to trigger
            *args, **kwargs: Arguments for callbacks
        """
        for listener in self._listeners[event_type]:
            q = self._queues[listener]
            lock = self._locks[listener]

            q.put_nowait((event_type, args, kwargs))

            if not lock.locked():
                self._thread_pool.submit(self._process_event, listener)

    def _process_event(self, callback):
        """Process queued events for a callback until queue is empty."""
        q = self._queues[callback]
        lock = self._locks[callback]

        with lock:
            if not q.empty():
                event, args, kwargs = q.get_nowait()
                callback(*args, **kwargs)
                q.task_done()

                if not q.empty():
                    self._thread_pool.submit(self._process_event, callback)

    def __call__(self, event_type: EventType, *args, **kwargs):
        """
        Trigger event for all registered callbacks.
        Events are processed in order per callback.

        Args:
            event_type: Event to trigger
            *args, **kwargs: Arguments for callbacks
        """
        self.trigger(event_type, *args, **kwargs)
