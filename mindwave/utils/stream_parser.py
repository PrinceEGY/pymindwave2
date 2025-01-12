"""MindWaveMobile2 Stream Parser Module."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from ..connector import ConnectorDataEvent

from .event_manager import Event, EventManager, EventType, Subscription
from .logger import Logger


@dataclass
class Data:
    """A data container for storing the parsed data from the stream.

    Attributes:
        raw_data (list[int]): A list of 512 raw EEG readings.
        attention (int): The attention level (0-100).
        meditation (int): The meditation level (0-100).
        delta (int): Power level in the delta frequency band.
        theta (int): Power level in the theta frequency band.
        lowAlpha (int): Power level in the low alpha frequency band.
        highAlpha (int): Power level in the high alpha frequency band.
        lowBeta (int): Power level in the low beta frequency band.
        highBeta (int): Power level in the high beta frequency band.
        lowGamma (int): Power level in the low gamma frequency band.
        highGamma (int): Power level in the high gamma frequency band.
    """

    raw_data: list[int] = field(default_factory=lambda: [0 for _ in range(512)])
    attention: int = 0
    meditation: int = 0

    delta: int = 0
    theta: int = 0
    lowAlpha: int = 0
    highAlpha: int = 0
    lowBeta: int = 0
    highBeta: int = 0
    lowGamma: int = 0
    highGamma: int = 0

    def update_data(self, **kwargs) -> None:
        """Update the data attributes with the specified values.

        Args:
            **kwargs: A dictionary of attribute names and values to update.

        Raises:
            AttributeError: If an invalid attribute name is specified.
        """
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"Invalid attribute: {key}")

            setattr(self, key, value)

    def __repr__(self) -> str:
        raw_summary = (
            f"[{', '.join(map(str, self.raw_data[:3]))}...."
            f"{', '.join(map(str, self.raw_data[-3:]))} "
            f"(length: {len(self.raw_data)})]"
        )
        return (
            f"Data(raw_data={raw_summary}, attention={self.attention}, "
            f"meditation={self.meditation}, delta={self.delta}, theta={self.theta}, "
            f"lowAlpha={self.lowAlpha}, highAlpha={self.highAlpha}, lowBeta={self.lowBeta}, "
            f"highBeta={self.highBeta}, lowGamma={self.lowGamma}, highGamma={self.highGamma})"
        )


@dataclass
class HeadsetDataEvent(Event):
    """Headset Data Event.

    Attributes:
        data (Data): The parsed data from the stream.
        timestamp (datetime): The timestamp of the event.
    """

    def __init__(self, data: Data, timestamp: datetime = None) -> None:
        """Initializes a new HeadsetDataEvent instance.

        Args:
            data (Data): The parsed data from the stream.
            timestamp (datetime, optional): The timestamp of the event.
        """
        super().__init__(event_type=EventType.HeadsetData, timestamp=timestamp)
        self.data = data


class StreamParser:
    """Processes and manages the data stream from a MindWave headset.

    This class acts as a wrapper for the raw connector data, processing incoming
    data streams and emitting events when complete data sets are available. It
    handles both raw EEG data (collected in 512-sample blocks) and processed
    metrics (attention, meditation, etc.).

    This ensures an event is emitted roughly every second.
    """

    def __init__(self):
        """Initializes a new StreamParser instance."""
        self._logger = Logger.get_logger(self.__class__.__name__)
        self.event_manager = EventManager()
        self._data = Data()
        self._raw_data = []
        self._raw_completed: bool = False

    def stream_data(self, event: ConnectorDataEvent) -> None:
        """Processes incoming data and emits a HeadsetDataEvent data is complete.

        Handles the streaming of data from the connector, processes it, and emits
        events when complete data is available.

        Args:
            event: The incoming data event from the connector.
        """
        self._parse_data(event.data)
        if self._raw_completed:
            self.event_manager.emit(HeadsetDataEvent(data=self._data))
            self._logger.debug(f"data streamed: {self._data}")
            self.reset_data()

    def on_data(self, listener: Callable[[HeadsetDataEvent], Any]) -> Subscription:
        """Registers a listener for headset data events.

        Args:
            listener: A callback function that will be called with HeadsetDataEvent
                instances when new data is available.

        Returns:
            A Subscription object that can be used to unsubscribe the listener.
        """
        return self.event_manager.add_listener(EventType.HeadsetData, listener)

    def _parse_data(self, data: dict) -> None:
        """Parses incoming data and updates internal state.

        Processes both processed metrics (eSense) and raw EEG data, updating the
        internal Data object accordingly.

        Args:
            data: Dictionary containing either eSense metrics or raw EEG data.
        """
        if "eSense" in data:
            self._data.update_data(**data["eSense"], **data["eegPower"])
        elif "rawEeg" in data:
            self._raw_data.append(data["rawEeg"])
            if len(self._raw_data) == 512:
                self._data.update_data(raw_data=self._raw_data)
                self._raw_completed = True
        else:
            self._logger.debug(f"Unknown data: {data}")

    def reset_data(self) -> None:
        """Resets all internal data structures to their initial state."""
        self._data = Data()
        self._raw_data = []
        self._raw_completed = False
