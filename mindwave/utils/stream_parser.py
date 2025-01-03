from dataclasses import dataclass, field
from datetime import datetime

from mindwave.connector import ConnectorDataEvent

from .event_manager import Event, EventManager, EventType
from .logger import Logger


@dataclass
class Data:
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

    def update_data(self, **kwargs):
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
    def __init__(self, data: Data, timestamp: datetime = None):
        super().__init__(event_type=EventType.HeadsetData)
        self.data = data


class StreamParser:
    """
    Can be thought of as a wrapper class for Connector Raw data. It processes the incoming data from the stream and emits events based on the data received.
    """

    def __init__(self):
        self._logger = Logger.get_logger(self.__class__.__name__)
        self.event_manager = EventManager()
        self._data = Data()
        self._raw_data = []
        self._raw_completed = False

    def stream_data(self, event: ConnectorDataEvent):
        """
        Processes the incoming data and stream it again.
        """
        self._parse_data(event.data)
        if self._raw_completed:
            self.event_manager.emit(HeadsetDataEvent(data=self._data))
            self.reset_data()
            self._logger.debug(f"data streamed: {self._data}")

    def __call__(self, data):
        self.stream_data(data)

    def add_listener(self, event_type, listener):
        return self.event_manager.add_listener(event_type, listener)

    def _parse_data(self, data: dict):
        if "eSense" in data:
            self._data.update_data(**data["eSense"], **data["eegPower"])
        elif "rawEeg" in data:
            self._raw_data.append(data["rawEeg"])
            if len(self._raw_data) == 512:
                self._data.update_data(raw_data=self._raw_data)
                self._raw_completed = True
        else:
            self._logger.debug(f"Unknown data: {data}")

    def reset_data(self):
        self._data = Data()
        self._raw_data = []
        self._raw_completed = False
