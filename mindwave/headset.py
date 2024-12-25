import json
from mindwave.connector import MindWaveConnector
from mindwave.stream_parser import StreamParser
from util.connection_state import ConnectionStatus
from util.daemon_async import DaemonAsync, daemon_task
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
        self._connector = MindWaveConnector(**connector_args)
        self._event_manager = EventManager()  # Emit ConnectorData events
        self._signal_quality = 0
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._stream_parser = StreamParser()
        self._lock = asyncio.Lock()

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
            self._event_manager(EventType.SignalQuality, value)
            self._logger.debug(f"Signal Quality value Changed: {value}%")

        self._signal_quality = float(value)

    @property
    def connection_status(self):
        return self._connection_status

    @connection_status.setter
    def connection_status(self, value: ConnectionStatus):
        self._event_manager(EventType.HeadsetStatus, value)
        if value == ConnectionStatus.CONNECTED and self._connection_status != ConnectionStatus.CONNECTED:
            # Connection changed to Connected
            self._event_manager.add_listener(
                event_type=EventType.ConnectorData,
                listener=self._stream_parser,
            )
            self._logger.info("Connected to MindWaveMobile2 device!")
        elif self._connection_status == ConnectionStatus.CONNECTED and value != ConnectionStatus.CONNECTED:
            # Connection changed from connected to something else
            self._event_manager.remove_listener(
                event_type=EventType.ConnectorData,
                listener=self._stream_parser,
            )
            self._logger.info("MindWaveMobile2 device Disconnected!")
            if self.is_running:
                self.stop()

        self._connection_status = value

    @daemon_task
    async def start(self, n_tries=3, timeout=15):
        """Start the connection to the MindWaveMobile2 device."""
        self.is_running = True
        self._read_loop_task = asyncio.create_task(self._read_loop())
        connect_task = asyncio.create_task(self._connect(n_tries=n_tries, timeout=timeout))
        done, pending = await asyncio.wait([self._read_loop_task, connect_task], return_when=asyncio.FIRST_COMPLETED)

        try:
            if connect_task in done:
                connection_success = await connect_task
                if not connection_success:
                    self.is_running = False
                    self._read_loop_task.cancel()
                else:
                    await self._read_loop_task
            elif self._read_loop_task in done:
                connect_task.cancel()
                self.is_running = False
                await self._read_loop_task
                # raise self._read_loop_task.exception()  # raise any exceptions raised in the task

        except Exception:
            self.is_running = False
            raise
        finally:
            # Clean up the read loop task
            if not self._read_loop_task.done():
                self._read_loop_task.cancel()

    @daemon_task
    async def stop(self):
        """Stop the connection to the MindWaveMobile2 device."""
        self._logger.info("Stopping MindWaveMobile2 device...")
        self.is_running = False
        await asyncio.sleep(1)
        await self._disconnect()

    async def _connect(self, timeout=15, n_tries=3):
        """Attempt to connect to the MindWaveMobile2 device with a specified number of retries in case of a timeout."""
        for i in range(1, n_tries + 1):
            if await self._attempt_connect(timeout) == True:
                return True
            elif i < n_tries:
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
                    await self._timeout()
                    return False
                await asyncio.sleep(0.5)

        self.start_connection_time = time.time()
        await self._connector.connect()
        self._logger.info("Connecting to MindWaveMobile2 device...")

        return await check_bluetooth_connection()

    async def _timeout(self):
        await self._disconnect()
        self._event_manager(EventType.Timeout)

    async def _disconnect(self):
        async with self._lock:
            if self.connection_status == ConnectionStatus.DISCONNECTED and not self._connector.is_connected():
                self._logger.warning("MindWaveMobile2 device is already disconnected!")
                return

            self.connection_status = ConnectionStatus.DISCONNECTED
            self._connector.disconnect()

    async def _read_loop(self):
        while self.is_running:
            async with self._lock:
                if self._connector.is_connected():
                    try:
                        out = await self._connector.read()
                        data = json.loads(out)
                        self._event_manager(EventType.ConnectorData, data)
                    except json.JSONDecodeError:
                        self._logger.warning(f"JSONDecodeError: {out}")
                    except UnicodeDecodeError as e:
                        self._logger.warning(f"UnicodeDecodeError: {e}, data: {out}")
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

    def on_data(self, callback):
        """Add a callback function to the parsed data events. The callback will be called when the parsed data event is triggered."""
        self._stream_parser.add_listener(EventType.HeadsetData, callback)

    def on_blink(self, callback):
        """Add a callback function to the blink events. The callback will be called when the blink event is triggered."""
        self._stream_parser.add_listener(EventType.Blink, callback)

    def on_status_change(self, callback):
        """Add a callback function to the connection status events. The callback will be called when the connection status event is triggered."""
        self._event_manager.add_listener(EventType.HeadsetStatus, callback)

    def on_signal_quality_change(self, callback):
        """Add a callback function to the signal quality change events. The callback will be called when the signal quality change event is triggered."""
        self._event_manager.add_listener(EventType.SignalQuality, callback)

    def on_connector_data(self, callback):
        """Add a callback function to the connector data events. The callback will be called when the connector data event is triggered."""
        self._event_manager.add_listener(EventType.ConnectorData, callback)
