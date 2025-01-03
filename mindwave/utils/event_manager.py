import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from queue import Queue
from typing import Callable

from mindwave.utils.singleton_meta import SingletonMeta

from .logger import Logger


class EventType(Enum):
    Blink = 1  # Blink detection event
    ConnectorData = 2  # Raw data from the connector, JSON-parsed
    HeadsetData = 3  # Parsed data from the headset, contains all streamed attributes
    HeadsetStatus = 4  # Status updates from the headset
    SessionEvent = 5  # Events related to session
    SignalQuality = 6  # Signal quality updates
    Timeout = 7  # Timeout event


@dataclass(kw_only=True)
class Event:
    event_type: EventType
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Subscription:
    def __init__(self, event_type: EventType, listener: Callable):
        self.event_type = event_type
        self.listener = listener

    def detach(self):
        EventManager().remove_listener(self.event_type, self.listener)


class EventManager(metaclass=SingletonMeta):
    """
    Event manager that allows for event-driven programming with multiple listeners.

    Each listener is guaranteed to receive events in order, but different listeners process independently.

    The manager uses a thread pool to process events, which makes it scalable for a large number of
    callbacks without creating excessive threads. Each callback gets its own queue, ensuring that
    events are processed in the order they were received, but different callbacks can process events
    at different speeds without blocking each other.
    """

    def __init__(self, max_workers: int = None) -> None:
        """
        Initialize event manager with thread pool.

        Args:
            max_workers: Maximum number of threads to use
        """
        self._logger = Logger.get_logger(self.__class__.__name__)
        self._listeners = defaultdict(list)
        self._queues = defaultdict(Queue)
        self._locks = defaultdict(threading.Lock)
        self._supscriptions = defaultdict(tuple)
        self._thread_pool = ThreadPoolExecutor(max_workers)

    def add_listener(self, event_type: EventType, listener: Callable) -> Subscription:
        """
        Register a callback function for a specific event type.
        """
        key = (event_type, listener)
        if listener in self._listeners[event_type]:
            self._logger.debug("Listener already exists")
            return self._supscriptions[key]

        self._listeners[event_type].append(listener)
        self._queues[listener] = Queue()
        self._locks[listener] = threading.Lock()

        self._supscriptions[key] = Subscription(*key)
        return self._supscriptions[key]

    def remove_listener(self, event_type: EventType, listener: Callable) -> None:
        """
        Unregister a callback function for a specific event type.
        """
        if listener not in self._listeners[event_type]:
            self._logger.debug("Listener does not exist")
            return

        self._listeners[event_type].remove(listener)
        self._queues.pop(listener)
        self._locks.pop(listener)
        self._supscriptions.pop((event_type, listener))

    def emit(self, event: Event) -> None:
        """
        Emits event for all registered callbacks.
        Events are processed in order per callback.

        Args:
            event_type: Event to trigger
            *args, **kwargs: Arguments for callbacks
        """
        for listener in self._listeners[event.event_type]:
            q = self._queues[listener]
            lock = self._locks[listener]

            q.put_nowait(event)

            if not lock.locked():
                self._thread_pool.submit(self._process_event, listener)

    def _process_event(self, callback) -> None:
        """Process queued events for a callback until queue is empty."""
        q = self._queues[callback]
        lock = self._locks[callback]

        with lock:
            if not q.empty():
                event = q.get_nowait()
                callback(event)
                q.task_done()

                if not q.empty():
                    self._thread_pool.submit(self._process_event, callback)
