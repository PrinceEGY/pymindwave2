import json
import threading
from mindwave.connector import MindWaveConnector
from mindwave.stream_parser import StreamParser
from util.connection_state import ConnectionStatus
from util.event_manager import EventManager, EventType
from util.logger import Logger
import time


class MindWaveMobile2:
    def __init__(
        self,
        **connector_args,
    ):
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.connector = MindWaveConnector(**connector_args)
        self.event_manager = EventManager()  # Emit ConnectorData events
        self._signal_quality = 0
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._stream_parser = StreamParser()

        self.on_connector_data(self._update_status)
        self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._read_thread.start()

    @property
    def signal_quality(self):
        # Normalized signal quality in the range of 0-100%
        # the raw signal quality value in the range 0-200 (0 indicating a good signal and 200 indicating an off-head state)
        # to access the raw signal quality value use the data from the connector (on_connector_data events)
        return self._signal_quality

    @signal_quality.setter
    def signal_quality(self, value: int):
        value = abs(value - 200)  # Invert the signal quality value
        value = value / 2  # Normalize the signal quality value to 0-100%
        if value != self._signal_quality:
            self.event_manager(EventType.SignalQuality, value)
            self._logger.debug(f"Signal Quality value Changed: {value}%")

        self._signal_quality = float(value)

    @property
    def connection_status(self):
        return self._connection_status

    @connection_status.setter
    def connection_status(self, value: ConnectionStatus):
        self.event_manager(EventType.HeadsetStatus, value)
        if (
            value == ConnectionStatus.CONNECTED
            and self._connection_status != ConnectionStatus.CONNECTED
        ):
            # Connection changed to Connected
            self.event_manager.add_listener(
                event_type=EventType.ConnectorData,
                listener=self._stream_parser,
            )
            self._logger.info("Connected to MindWaveMobile2 device!")
        elif (
            self._connection_status == ConnectionStatus.CONNECTED
            and value != ConnectionStatus.CONNECTED
        ):
            # Connection changed from connected to something else
            self.event_manager.remove_listener(
                event_type=EventType.ConnectorData,
                listener=self._stream_parser,
            )
            self._logger.info("MindWaveMobile2 device Disconnected!")

        self._connection_status = value

    def connect(self, timeout=15, n_tries=3):
        """Attempt to connect to the MindWaveMobile2 device with a specified number of retries in case of a timeout."""

        if self._attempt_connect(timeout):
            return

        for i in range(n_tries - 1):
            self._logger.warning(f"Connection timed out. Retrying Attempt {i+2} ...")
            time.sleep(3)
            if self._attempt_connect(timeout):
                return
        self._logger.error(
            "Maximum number of retries reached. Failed to connect to MindWaveMobile2 device!"
        )

    def _attempt_connect(self, timeout=15):
        """Connect to the MindWaveMobile2 device and start a read loop to process and stream incoming data."""

        def check_connection_status(
            stop_event: threading.Event, connected_event: threading.Event
        ):
            while (
                self.connection_status != ConnectionStatus.CONNECTED
                and not stop_event.is_set()
            ):
                if not self.connector.is_connected():
                    connected_event.clear()
                    self._logger.debug(
                        "Connector Connection lost while trying to connect!"
                    )
                    return
            connected_event.set()

        self._logger.info("Connecting to MindWaveMobile2 device...")
        self.connector.connect()

        stop_event = threading.Event()
        connected_event = threading.Event()
        thread = threading.Thread(
            target=check_connection_status, args=(stop_event, connected_event)
        )
        thread.start()
        thread.join(timeout)

        if thread.is_alive() and not connected_event.is_set():  # Timeout occurred
            self._timeout_disconnect()

        stop_event.set()
        return connected_event.is_set()

    def disconnect(self):
        if (
            self.connection_status == ConnectionStatus.DISCONNECTED
            and not self.connector.is_connected()
        ):
            self._logger.warning("MindWaveMobile2 device is already disconnected!")
            return

        self._logger.info("Disconnecting MindWaveMobile2 device...")
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.connector.disconnect()

    def on_data(self, callback):
        """Add a callback function to the parsed data events. The callback will be called when the parsed data event is triggered."""
        self._stream_parser.add_listener(EventType.HeadsetData, callback)

    def on_blink(self, callback):
        """Add a callback function to the blink events. The callback will be called when the blink event is triggered."""
        self._stream_parser.add_listener(EventType.Blink, callback)

    def on_status_change(self, callback):
        """Add a callback function to the connection status events. The callback will be called when the connection status event is triggered."""
        self.event_manager.add_listener(EventType.HeadsetStatus, callback)

    def on_signal_quality_change(self, callback):
        """Add a callback function to the signal quality change events. The callback will be called when the signal quality change event is triggered."""
        self.event_manager.add_listener(EventType.SignalQuality, callback)

    def on_connector_data(self, callback):
        """Add a callback function to the connector data events. The callback will be called when the connector data event is triggered."""
        self.event_manager.add_listener(EventType.ConnectorData, callback)

    def _read_loop(self):
        while True:
            if self.connector.is_connected():
                try:
                    out = self.connector.read()
                    data = json.loads(out)
                    self.event_manager(EventType.ConnectorData, data)
                except json.JSONDecodeError:
                    self._logger.error("Error parsing JSON")
                except UnicodeDecodeError as e:
                    self._logger.error(f"UnicodeDecodeError: {e}, data: {out}")
                except AttributeError as e:
                    self._logger.error(f"AttributeError: {e}")
                    # FIXME: this is raised when the connection is closed normally
                    # The method runs in a separate thread, causing the disconnect method to be called twice.
                    # As a result, a 'recv' method is called on a closed socket, leading to a None object.
                    # Although this doesn't cause any functional issues since the connection is already closed,
                    # it should be handled properly for better code quality.
                except Exception as e:
                    self._logger.error(f"An error occurred: {e}")
                    self.disconnect()
            else:
                time.sleep(0.1)

    def _update_status(self, data):
        # Set the connection status and signal quality based on the connector data
        # This is a naive way but there are no other ways to determine the connection status
        # Since the "status" field is not always present in the connector data
        if "status" in data:
            if data["status"] == "scanning":
                self.connection_status = ConnectionStatus.SCANNING
            elif data["status"] == "idle":
                self.connection_status = ConnectionStatus.IDLE
            elif data["status"] == "notscanning":
                self.connection_status = ConnectionStatus.NOTSCANNING
        elif "eSense" in data or "rawEeg" in data or "blinkStrength" in data:
            self.connection_status = ConnectionStatus.CONNECTED
            if "poorSignalLevel" in data:
                self.signal_quality = data["poorSignalLevel"]
        elif "mentalEffort" in data or "familiarity" in data:
            pass
        else:
            self.connection_status = ConnectionStatus.UNKOWN
            self._logger.warning(f"Unknown connection status, data: {data}")

        if self.connection_status != ConnectionStatus.CONNECTED:
            self._logger.debug(
                f"Connection Status: {self.connection_status.name}, Signal Quality: {self.signal_quality}, Data: {data}"
            )

    def _timeout_disconnect(self):
        self._logger.warning("Connection timed out!")
        self.disconnect()
        self.event_manager(EventType.Timeout)
