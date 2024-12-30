import asyncio
import json
import threading
import time
from enum import Enum

from .connector import ThinkGearConnector

from .utils.daemon_async import verbose
from .utils.event_manager import EventManager, EventType
from .utils.logger import Logger
from .utils.stream_parser import StreamParser


class ConnectionStatus(Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    IDLE = 3
    SCANNING = 4
    NOTSCANNING = 5
    UNKOWN = 6
    CONNECTION_LOST = 7


class MindWaveMobile2:
    def __init__(self, max_workers=4, event_loop=None, **tg_connector_args):
        super().__init__()
        self.is_running = False
        self._event_loop = event_loop

        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self._tg_connector = ThinkGearConnector(**tg_connector_args)
        self._event_manager = EventManager(max_workers=max_workers)  # Emit ConnectorData events
        self._signal_quality = 0
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._stream_parser = StreamParser()
        self._lock = asyncio.Lock()
        self._read_loop_task = None

        self.on_connector_data(self._update_status)

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
        if value != self._connection_status:
            self._event_manager(EventType.HeadsetStatus, value)

        if value == ConnectionStatus.CONNECTED and self._connection_status != ConnectionStatus.CONNECTED:
            # Connection changed to Connected
            self._logger.info("Connected to MindWaveMobile2 device!")

            self._event_manager.add_listener(
                event_type=EventType.ConnectorData,
                listener=self._stream_parser,
            )

        elif self._connection_status == ConnectionStatus.CONNECTED and value != ConnectionStatus.CONNECTED:
            # Connection changed from connected to something else
            self._logger.info("MindWaveMobile2 device Disconnected!")
            if self.is_running:
                self.stop()

            self._event_manager.remove_listener(
                event_type=EventType.ConnectorData,
                listener=self._stream_parser,
            )

            time.sleep(3)  # Wait for the read loop to stop
            self._event_manager(EventType.HeadsetStatus, ConnectionStatus.CONNECTION_LOST)

        self._connection_status = value

    def start(self, n_tries=3, timeout=15, blocking=True):
        self._setup_event_loop()
        future = asyncio.run_coroutine_threadsafe(self._start_async(n_tries=n_tries, timeout=timeout), self._event_loop)

        if blocking:
            return future.result()

    async def _start_async(self, n_tries=3, timeout=15):
        """Start the connection to the MindWaveMobile2 device."""
        if self.is_running:
            self._logger.info("MindWaveMobile2 device is already running!")
            return True

        self.is_running = True
        connection_success = await self._connect(n_tries=n_tries, timeout=timeout)

        if not connection_success:
            self.is_running = False
            return False

        return True

    def stop(self, blocking=True):
        self._setup_event_loop()

        future = asyncio.run_coroutine_threadsafe(self._stop_async(), self._event_loop)
        if blocking:
            return future.result()

    async def _stop_async(self):
        """Stop the connection to the MindWaveMobile2 device."""
        if not self.is_running:
            self._logger.info("MindWaveMobile2 device is already stopped!")
            return True

        self._logger.info("Stopping MindWaveMobile2 device...")
        self.is_running = False
        self._read_loop_task.cancel()
        await asyncio.sleep(1)
        return await self._disconnect()

    async def _connect(self, timeout=15, n_tries=3):
        """Attempt to connect to the MindWaveMobile2 device with a specified number of retries in case of a timeout."""
        for i in range(1, n_tries + 1):
            if await self._attempt_connect(timeout) == True:
                return True
            elif i < n_tries:
                self._logger.warning(f"Connection timed out. Retrying Attempt {i+1} ...")
                await asyncio.sleep(1)

        self._logger.error("Maximum number of retries reached. Failed to connect to MindWaveMobile2 device!")
        self.is_running = False
        self._read_loop_task.cancel()
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
        if await self._tg_connector.connect():
            self._logger.info("Connecting to MindWaveMobile2 device...")

            if self._read_loop_task is None or self._read_loop_task.done():
                self._read_loop_task = asyncio.create_task(self._read_loop())
                self._read_loop_task

            return await check_bluetooth_connection()

        return False

    async def _timeout(self):
        await self._disconnect()
        self._event_manager(EventType.Timeout)

    async def _disconnect(self):
        async with self._lock:
            if self.connection_status == ConnectionStatus.DISCONNECTED and not self._tg_connector.is_connected():
                self._logger.info("MindWaveMobile2 device is already disconnected!")
                return True

            self.connection_status = ConnectionStatus.DISCONNECTED
            return self._tg_connector.disconnect()

    def _setup_event_loop(self) -> None:
        def run_on_thread(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        # Event loop is provided
        if self._event_loop is not None:
            return

        # Event loop is not provided, get the current event loop if it exists
        try:
            self._event_loop = asyncio.get_running_loop()
            self._logger.info("Event loop is not provided, Found an existing event loop running and using it.")

        # Event loop is not provided and no event loop is running in the current thread
        # create a new event loop in a new thread
        except RuntimeError:
            self._logger.warning(
                "Event loop is not provided and no Event loop is running in the current thread. "
                "Creating a new event loop in a new thread."
            )
            self._event_loop = asyncio.new_event_loop()
            thread = threading.Thread(target=run_on_thread, args=(self._event_loop,), daemon=True)
            thread.start()

    @verbose
    async def _read_loop(self):
        while self.is_running:
            async with self._lock:
                if self._tg_connector.is_connected():
                    try:
                        out = await self._tg_connector.read()
                        data = json.loads(out)
                        self._event_manager(EventType.ConnectorData, data)
                    except json.JSONDecodeError:
                        self._logger.warning(f"JSONDecodeError: {out}")
                    except UnicodeDecodeError as e:
                        self._logger.warning(f"UnicodeDecodeError: {e}, data: {out}")
                    except Exception as e:
                        self.is_running = False
                        raise
                else:
                    await asyncio.sleep(0.1)

    def _update_status(self, data):
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
            # To be used later if needed
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
