"""Module providing a thread-safe singleton metaclass."""

import threading


class SingletonMeta(type):
    """A thread-safe singleton metaclass.

    This metaclass ensures that only one instance of a class is created,
    even in multi-threaded environments.
    """

    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Creates a new instance of the class if it doesn't exist."""
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return cls._instances[cls]
