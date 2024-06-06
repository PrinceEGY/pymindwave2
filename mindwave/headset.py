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
        self._connection_status = ConnectionStatus.DISCONNECTED
        self.connector = MindWaveConnector(**connector_args)
        self.signal_quality = 200  # 0-200 (0 indicating a good signal and 200 indicating an off-head state)
        self.event_manager = EventManager()  # Emit ConnectorData events
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self._connection_retries = 1
        self._stream_parser = StreamParser()

    @property
    def connection_status(self):
        return self._connection_status

    @connection_status.setter
    def connection_status(self, value: ConnectionStatus):
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

        def on_timeout():
            if self._connection_retries < n_tries:
                self._connection_retries += 1
                self._logger.warning(
                    f"Connection timed out. Retrying Attempt {self._connection_retries} ..."
                )
                time.sleep(3)
                self._attempt_connect(timeout)
            elif self._connection_retries == n_tries:
                self._logger.error(
                    "Maximum number of retries reached. Failed to connect to MindWaveMobile2 device!"
                )
                self.event_manager.remove_listener(EventType.Timeout, on_timeout)

        self._connection_retries = 1

        self._attempt_connect(timeout)

        self.event_manager.add_listener(EventType.Timeout, on_timeout)

    def _attempt_connect(self, timeout=15):
        """Connect to the MindWaveMobile2 device and start a read loop to process and stream incoming data."""

        self._logger.info("Connecting to MindWaveMobile2 device...")
        self.connector.connect()
        self.event_manager.add_listener(EventType.ConnectorData, self._update_status)
        thread = threading.Thread(target=self._read_loop, args=(timeout,), daemon=True)
        thread.start()

    def disconnect(self):
        if (
            self.connection_status == ConnectionStatus.DISCONNECTED
            and not self.connector.is_connected()
        ):
            self._logger.warning("MindWaveMobile2 device is already disconnected!")
            return
        self._logger.info("Disconnecting MindWaveMobile2 device...")
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.event_manager.remove_listener(EventType.ConnectorData, self._update_status)
        self.connector.disconnect()

    def add_listener(self, event_type, listener):
        """Add a listener to the parsed data events. The listener will be called when the parsed data event is triggered."""
        self._stream_parser.add_listener(event_type, listener)

    def remove_listener(self, event_type, listener):
        """Remove a listener from the parsed data events. The listener will no longer be called when the parsed data event is triggered."""
        self._stream_parser.remove_listener(event_type, listener)

    def _read_loop(self, timeout):
        t1 = time.perf_counter()
        while self.connector.is_connected():
            try:
                out = self.connector.read()
                data = json.loads(out)
                self.event_manager(EventType.ConnectorData, data)
            except json.JSONDecodeError:
                self._logger.error("Error parsing JSON")
            except UnicodeDecodeError as e:
                self._logger.error(f"UnicodeDecodeError: {e}, data: {out}")
            except Exception as e:
                # FIXME: this is raised when the connection is closed normally
                # this is because of this method runs in a separate thread
                # which causes the disconnect method to be called twice
                # there will be no issues anyway since the connection is already closed
                # but this should be handled properly for better code quality
                self._logger.error(f"An error occurred: {e}")
                self.disconnect()
                break

            if self.connection_status == ConnectionStatus.CONNECTED:
                t1 = time.perf_counter()
            else:
                t2 = time.perf_counter()
                if t2 - t1 > timeout:
                    self._timeout_disconnect()
                    break

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
                f"Connection Status: {self.connection_status}, Signal Quality: {self.signal_quality}, Data: {data}"
            )

    def _timeout_disconnect(self):
        self._logger.warning("Connection timed out!")
        self.disconnect()
        self.event_manager(EventType.Timeout)
