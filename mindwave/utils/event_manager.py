"""Event manager for event-driven programming with multiple listeners."""

import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from queue import Queue
from typing import Any, Callable

from .singleton_meta import SingletonMeta

from .logger import Logger


class EventType(Enum):
    """Enumeration of event types that can be emitted by the event manager."""

    Blink = 1
    """Blink detection event."""
    ConnectorData = 2
    """Raw data from the connector, JSON-parsed."""
    HeadsetData = 3
    """Parsed data from the headset, contains all streamed attributes."""
    HeadsetStatus = 4
    """Status updates from the headset."""
    SessionEvent = 5
    """Events related to session."""
    SignalQuality = 6
    """Signal quality updates."""
    Timeout = 7
    """Timeout event."""


@dataclass(kw_only=True)
class Event:
    """Base class for events that can be emitted by the event manager.

    Attributes:
        event_type (EventType): The type of event.
        timestamp (datetime): The timestamp of the event. Defaults to the current time.
    """

    event_type: EventType
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Subscription:
    """An object that manages the subscription of a listener to an event type.

    Attributes:
        event_type (EventType): The type of event the listener is subscribed to.
        listener (Callable): The listener callback.
    """

    def __init__(self, event_type: EventType, listener: Callable[[Event], Any]) -> None:
        """Initialize the subscription object.

        Args:
            event_type (EventType): The type of event the listener is subscribed to.
            listener (Callable): The listener callback.
        """
        self.event_type = event_type
        self.listener = listener

    def detach(self) -> None:
        """Remove the listener from the event manager."""
        EventManager().remove_listener(self.event_type, self.listener)

    def is_attached(self) -> bool:
        """Check if the listener is attached to the event manager.

        Returns:
            bool: True if the listener is attached, False otherwise.
        """
        return EventManager().is_attached(self.event_type, self.listener)


class EventManager(metaclass=SingletonMeta):
    """Event manager that allows for event-driven programming with multiple listeners.

    Each listener is guaranteed to receive events in order, but different listeners process independently.

    The manager uses a thread pool to process events, which makes it scalable for a large number of
    callbacks without creating excessive threads. Each callback gets its own queue, ensuring that
    events are processed in the order they were received, but different callbacks can process events
    at different speeds without blocking each other.
    """

    def __init__(self, max_workers: int = None) -> None:
        """Initialize the event manager.

        Args:
            max_workers (int, optional): The maximum number of worker threads in the thread pool.
        """
        self._logger = Logger.get_logger(self.__class__.__name__)
        self._listeners = defaultdict(list)
        self._queues = defaultdict(Queue)
        self._locks = defaultdict(threading.Lock)
        self._supscriptions = defaultdict(tuple)
        self._thread_pool = ThreadPoolExecutor(max_workers)

    def add_listener(self, event_type: EventType, listener: Callable[[Event], Any]) -> Subscription:
        """Adds a new listener for the specified event type.

        Args:
            event_type (EventType): The type of event to listen for.
            listener (function): The callback function to be called when
                events of the specified type occur.

        Returns:
            Subscription: A subscription object that can be used to manage the listener.
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

    def remove_listener(self, event_type: EventType, listener: Callable[[Event], Any]) -> None:
        """Removes a listener from the specified event type.

        Args:
            event_type (EventType): The type of event to remove the listener from.
            listener (function): The callback function to remove.
        """
        if listener not in self._listeners[event_type]:
            self._logger.debug("Listener does not exist")
            return

        self._listeners[event_type].remove(listener)
        self._queues.pop(listener)
        self._locks.pop(listener)
        self._supscriptions.pop((event_type, listener))

    def emit(self, event: Event) -> None:
        """Emits an event to all listeners of the event type.

        Args:
            event (Event): The event to emit.
        """
        for listener in self._listeners[event.event_type]:
            q = self._queues[listener]
            lock = self._locks[listener]

            q.put_nowait(event)

            if not lock.locked():
                self._thread_pool.submit(self._process_event, listener)

    def _process_event(self, callback: Callable[[Event], Any]) -> None:
        """Processes an event for a specific callback.

        This method is called by the thread pool to process events for a specific
        callback. It ensures events are processed in order and manages the callback's
        lock to prevent concurrent processing.

        Args:
            callback (function): The callback to process the event for.
        """
        q = self._queues[callback]
        lock = self._locks[callback]

        with lock:
            if not q.empty():
                event = q.get_nowait()
                callback(event)
                q.task_done()

                if not q.empty():
                    self._thread_pool.submit(self._process_event, callback)

    def is_attached(self, event_type: EventType, listener: Callable[[Event], Any]) -> bool:
        """Check if a listener is attached to the event manager.

        Args:
            event_type (EventType): The type of event the listener is subscribed to.
            listener (function): The listener callback.

        Returns:
            bool: True if the listener is attached, False otherwise.
        """
        return listener in self._listeners[event_type]
