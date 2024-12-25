import json
import threading
import traceback
from mindwave.connector import MindWaveConnector
from mindwave.stream_parser import StreamParser
from util.connection_state import ConnectionStatus
from util.daemon_async import DaemonAsync
from util.event_manager import EventManager, EventType
from util.logger import Logger
import time
import asyncio


class MindWaveMobile2(DaemonAsync):
    def __init__(
        self,
        **connector_args,
    ):
        super().__init__()
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.connector = MindWaveConnector(**connector_args)
        self.event_manager = EventManager()  # Emit ConnectorData events
        self._signal_quality = 0
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._stream_parser = StreamParser()

        self.on_connector_data(self._update_status)
        self._read_loop_task = None
        self.is_running = False

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
        if value == ConnectionStatus.CONNECTED and self._connection_status != ConnectionStatus.CONNECTED:
            # Connection changed to Connected
            self.event_manager.add_listener(
                event_type=EventType.ConnectorData,
                listener=self._stream_parser,
            )
            self._logger.info("Connected to MindWaveMobile2 device!")
        elif self._connection_status == ConnectionStatus.CONNECTED and value != ConnectionStatus.CONNECTED:
            # Connection changed from connected to something else
            self.event_manager.remove_listener(
                event_type=EventType.ConnectorData,
                listener=self._stream_parser,
            )
            self._logger.info("MindWaveMobile2 device Disconnected!")

        self._connection_status = value

    async def start(self, n_tries=3, timeout=15):
        """Start the connection to the MindWaveMobile2 device."""
        self.is_running = True
        self._read_loop_task = asyncio.create_task(self._read_loop())

        if await self._connect(n_tries=n_tries, timeout=timeout):
            await self._read_loop_task
        else:
            # Connection failure or timeout
            self.is_running = False

    async def stop(self):
        """Stop the connection to the MindWaveMobile2 device."""
        self._logger.info("Stopping MindWaveMobile2 device...")
        self.is_running = False
        await asyncio.sleep(1)
        self._disconnect()

    async def _connect(self, timeout=15, n_tries=3):
        """Attempt to connect to the MindWaveMobile2 device with a specified number of retries in case of a timeout."""
        # TODO: Implement the retry mechanism
        for i in range(1, n_tries + 1):
            self._logger.debug(f"{self._read_loop_task.done()}")
            if await self._attempt_connect(timeout) == True:
                return True
            else:
                self._logger.warning(f"Connection timed out. Retrying Attempt {i+1} ...")
                await asyncio.sleep(1)

        self._logger.error("Maximum number of retries reached. Failed to connect to MindWaveMobile2 device!")
        return False

    async def _attempt_connect(self, timeout=15):
        """Connect to the MindWaveMobile2 device and start a read loop to process and stream incoming data."""

        async def check_bluetooth_connection():
            while self.is_running:
                if self.connection_status == ConnectionStatus.CONNECTED:
                    return True
                if time.time() - self.start_connection_time > timeout:
                    self._timeout()
                    return False
                await asyncio.sleep(0.5)

        self.start_connection_time = time.time()
        await self.connector.connect()

        return await check_bluetooth_connection()

    def _timeout(self):
        self._disconnect()
        self.event_manager(EventType.Timeout)

    def _disconnect(self):
        if self.connection_status == ConnectionStatus.DISCONNECTED and not self.connector.is_connected():
            self._logger.warning("MindWaveMobile2 device is already disconnected!")
            return

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

    async def _read_loop(self):
        while self.is_running:
            if self.connector.is_connected():
                try:
                    out = await self.connector.read()
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
                    # FIXME: This needs to be handled here because 'asyncio' does not propagate the exception and instead halts the task.
                    # The exception is stored within the task object and is only raised when the task is awaited.
                    # However, in this case, the task is not awaited until the connection is established,
                    # so the exception cannot be caught externally.
                    self._logger.error("read loop error: \n" + traceback.format_exc())
                    # self._disconnect()
                    print("EXCEPTION: ", e)
                    raise e
            else:
                await asyncio.sleep(0.1)

    def _update_status(self, data):
        # TODO: create an Event queue to seperate the producing and consuming of events
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
