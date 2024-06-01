import json
import threading
from mindwave.connector import MindWaveConnector
from util.connection_state import ConnectionStatus
from util.event_handler import EventHandler, EventType
from util.logger import Logger
import time


class MindWaveMobile2:
    def __init__(
        self,
        **connector_args,
    ):
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.connector = MindWaveConnector(**connector_args)
        self.signal_quality = 200  # 0-200 (0 indicating a good signal and 200 indicating an off-head state)
        self.event_handler = EventHandler()
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self._connection_retries = 1

    def connect(self, timeout=15, n_tries=3):
        """Attempt to connect to the MindWaveMobile2 device with a specified number of retries in case of a timeout."""

        def on_timeout():
            if self._connection_retries < n_tries:
                self._connection_retries += 1
                self._logger.warning(
                    f"Connection timed out. Retrying Attempt {self._connection_retries} ..."
                )
                self._attempt_connect(timeout)
            elif self._connection_retries == n_tries:
                self._logger.error(
                    "Maximum number of retries reached. Failed to connect to MindWaveMobile2 device!"
                )

        self._connection_retries = 1

        self.event_handler.add_listener(EventType.Timeout, on_timeout)
        self._attempt_connect(timeout)

    def _attempt_connect(self, timeout=15):
        """Connect to the MindWaveMobile2 device and start a read loop to process and stream incoming data."""

        self._logger.info("Connecting to MindWaveMobile2 device...")
        self.connector.connect()
        thread = threading.Thread(target=self._read_loop, args=(timeout,), daemon=True)
        thread.start()
        self.event_handler.add_listener(EventType.ConnectorData, self._update_status)

    def disconnect(self):
        self._logger.info("Disconnecting MindWaveMobile2 device...")
        self.connector.disconnect()
        self.event_handler.remove_listener(EventType.ConnectorData, self._update_status)
        self.connection_status = ConnectionStatus.DISCONNECTED

    def _read_loop(self, timeout):
        t1 = time.perf_counter()
        while True:
            try:
                out = self.connector.read()
                parsed = json.loads(out)
                self.event_handler(EventType.ConnectorData, data)
            except json.JSONDecodeError:
                self._logger.error("Error parsing JSON")
            except UnicodeDecodeError as e:
                self._logger.error(f"UnicodeDecodeError: {e}, data: {out}")
            except Exception as e:
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

    def _update_status(self, parsed):
        # Set the connection status and signal quality based on the parsed data
        # This is a naive way but there are no other ways to determine the connection status
        # Since the "status" field is not always present in the parsed data
        # TODO: detect when the state changes from connected to any other state
        if "status" in parsed:
            if parsed["status"] == "scanning":
                self.connection_status = ConnectionStatus.SCANNING
            elif parsed["status"] == "idle":
                self.connection_status = ConnectionStatus.IDLE
            elif parsed["status"] == "notscanning":
                self.connection_status = ConnectionStatus.NOTSCANNING
        elif "eSense" in parsed or "rawEeg" in parsed or "blinkStrength" in parsed:
            if self.connection_status != ConnectionStatus.CONNECTED:
                self.connection_status = ConnectionStatus.CONNECTED
                self._logger.info("Connected to MindWaveMobile2 device!")
            if "poorSignalLevel" in parsed:
                self.signal_quality = parsed["poorSignalLevel"]
        elif "mentalEffort" in parsed or "familiarity" in parsed:
            pass
        else:
            self.connection_status = ConnectionStatus.UNKOWN
            self._logger.warning(f"Unknown connection status, parsed data: {parsed}")

        self._logger.debug(
            f"Connection Status: {self.connection_status}, Signal Quality: {self.signal_quality}, Parsed Data: {parsed}"
        )

    def _timeout_disconnect(self):
        self._logger.warning("Connection timed out!")
        self.disconnect()
        self.event_handler.trigger(EventType.Timeout)
