from mindwave.data import Data
from util.event_handler import EventHandler, EventType
from util.logger import Logger


class StreamParser:
    """
    Can be thought of as a wrapper class for Connector Raw data. It processes the incoming data from the stream and triggers events based on the data received.
    """

    def __init__(self):
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.event_handler = EventHandler()
        self._data = Data()
        self._raw_data = []
        self._raw_flag = False

    def stream_data(self, data):
        """
        Processes the incoming data and stream it again.
        """
        if "blinkStrength" in data:
            self.event_handler.trigger(EventType.Blink, data["blinkStrength"])
            self._logger.debug(
                f"Blink Triggered with strength: {data['blinkStrength']}"
            )
        else:
            data = self._parse_data(data)
            if self._raw_flag:
                self.event_handler.trigger(EventType.HeadsetData, self._data)
                self._raw_flag = False
                self._logger.debug(f"data streamed: {self._data}")

    def __call__(self, data):
        self.stream_data(data)

    def add_listener(self, event_type, listener):
        self.event_handler.add_listener(event_type, listener)

    def remove_listener(self, event_type, listener):
        self.event_handler.remove_listener(event_type, listener)

    def _parse_data(self, data):
        if "eSense" in data:
            self._data.update_data(**data["eSense"], **data["eegPower"])
        elif "rawEeg" in data:
            self._raw_data.append(data["rawEeg"])
            if len(self._raw_data) == 512:
                self._data.update_data(raw_data=self._raw_data)
                self._raw_data = []
                self._raw_flag = True
        else:
            self._logger.debug(f"Unknown data: {data}")

        return data

    def reset_data(self):
        self._data = Data()
        self._raw_data = []
        self._logger.debug("Data reset!")
