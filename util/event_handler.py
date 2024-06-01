from collections import defaultdict
from enum import Enum
from typing import Callable


class EventType(Enum):
    ConnectorData = 1  # Raw data from the connector only json parsed
    Timeout = 2


class EventHandler:
    def __init__(self):
        self.__listeners = defaultdict(list)

    def add_listener(self, event_type: EventType, listener: Callable):
        assert listener not in self.__listeners[event_type], "Listener already exists"
        self.__listeners[event_type].append(listener)

    def remove_listener(self, event_type: EventType, listener: Callable):
        assert listener in self.__listeners[event_type], "Listener does not exist"
        self.__listeners[event_type].remove(listener)

    def trigger(self, event_type: EventType, *args, **kwargs):
        for listener in self.__listeners[event_type]:
            listener(*args, **kwargs)

    def __iadd__(self, event_type: EventType, listener: Callable):
        self.add_listener(event_type, listener)
        return self

    def __isub__(self, event_type: EventType, listener: Callable):
        self.remove_listener(event_type, listener)
        return self

    def __call__(self, event_type: EventType, *args, **kwargs):
        self.trigger(event_type, *args, **kwargs)
