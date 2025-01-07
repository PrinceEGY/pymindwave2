"""NeuroSky MindWave Mobile 2 Headset Module.

This module provides an event-driven interface for connecting to and receiving data from
a NeuroSky MindWaveMobile2 headset through the ThinkGear connector service. It handles
the connection lifecycle, data streaming, and event emission for various headset states
and measurements.

Features:
    - Event-based data streaming
    - Connection status tracking and updates
    - Asynchronous connection handling with retry mechanisms
    - Signal quality monitoring and normalization
    - Blink detection events
    - Includes different levels of logging
"""

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from .connector import ConnectorDataEvent, ThinkGearConnector
from .utils.daemon_async import verbose
from .utils.event_manager import Event, EventManager, EventType, Subscription
from .utils.logger import Logger
from .utils.stream_parser import HeadsetDataEvent, StreamParser


class ConnectionStatus(Enum):
    """Enumeration of possible headset connection states.

    States marked as TGC are emitted natively by the ThinkGear Connector.

    States marked as CUSTOM are custom states defined by this module.
    """

    CONNECTED = 1
    """TGC: The headset is successfully connected via ThinkGear Connector
        and actively streaming data. """
    DISCONNECTED = 2
    """TGC: Both the headset and the ThinkGear Connector are disconnected."""
    IDLE = 3
    """TGC: The headset is not connected and the ThinkGear Connector is idle."""
    SCANNING = 4
    """TGC: The ThinkGear Connector is scanning for the MindWaveMobile2 device."""
    NOTSCANNING = 5
    """TGC: The ThinkGear Connector is not scanning for the MindWaveMobile2 device."""
    UNKOWN = 6
    """CUSTOM: Unrecognized TGC connection status."""
    CONNECTION_LOST = 7
    """CUSTOM: The headset connection was lost.
    (Represents a transition from CONNECTED to any other state)
    """


@dataclass
class BlinkEvent(Event):
    """Blink detection event.

    Attributes:
        blink_strength (int): The strength of the detected blink.
        timestamp (datetime): The timestamp when the blink was detected.
    """

    def __init__(self, blink_strength: int, timestamp: datetime = None):
        """Initialize a BlinkEvent.

        Args:
            blink_strength (int): Strength of the detected blink [0-255].
            timestamp (datetime, optional): Timestamp of the event.
            if not provided, the current time is used.

        """
        super().__init__(event_type=EventType.Blink, timestamp=timestamp)
        self.blink_strength = blink_strength


@dataclass
class HeadsetStatusEvent(Event):
    """Headset connection status change event.

    Attributes:
        status (ConnectionStatus): Current ConnectionStatus of the headset.
        timestamp (datetime): The timestamp when the status changed.
    """

    def __init__(self, status: ConnectionStatus, timestamp: datetime = None):
        """Initialize a HeadsetStatusEvent.

        Args:
            status (ConnectionStatus): New ConnectionStatus of the headset.
            timestamp (datetime, optional): The timestamp when the status changed.
            if not provided, the current time is used.
        """
        super().__init__(event_type=EventType.HeadsetStatus, timestamp=timestamp)
        self.status = status


@dataclass
class SignalQualityEvent(Event):
    """Signal quality change event.

    Attributes:
        signal_quality (int): Integer representing signal quality value (0-100%).
        timestamp (datetime): The timestamp when the signal quality changed.
    """

    def __init__(self, signal_quality: int, timestamp: datetime = None):
        """Initialize a SignalQualityEvent.

        Args:
            signal_quality (int): Integer Signal quality value in the range of 0-100.
            timestamp (datetime, optional): Timestamp of the event.
            if not provided, the current time is used.
        """
        super().__init__(event_type=EventType.SignalQuality, timestamp=timestamp)
        self.signal_quality = signal_quality


@dataclass
class TimeoutEvent(Event):
    """Timeout event.

    Attributes:
        timestamp (datetime): The timestamp when the timeout occurred.
    """

    def __init__(self, timestamp: datetime = None):
        """Initialize a TimeoutEvent.

        Args:
            timestamp (datetime, optional): Timestamp of the event.
            if not provided, the current time is used.
        """
        super().__init__(event_type=EventType.Timeout, timestamp=timestamp)


class MindWaveMobile2:
    """The main interface for the NeuroSky MindWaveMobile2 EEG headset.

    This class provides an event-based interface for connecting to and receiving data
    from a MindWaveMobile2 headset using the ThinkGear connector service.
    """

    def __init__(
        self,
        event_loop: asyncio.AbstractEventLoop = None,
        tg_connector: ThinkGearConnector = None,
    ) -> None:
        """Initialize a MindWaveMobile2 instance.

        Args:
            event_loop (asyncio.AbstractEventLoop, optional): The event loop to use for asynchronous operations.
            If not provided, it will check for a running event loop in the current thread.
            If no running event loop is found, a new event loop will be created in a new thread.
            tg_connector (ThinkGearConnector, optional): The ThinkGearConnector instance to use.
            If not provided, a new instance with default settings will be created.
        """
        super().__init__()
        self.is_running: bool = False
        self._event_loop: asyncio.AbstractEventLoop = event_loop

        self._logger: logging.Logger = Logger.get_logger(self.__class__.__name__)
        self._tg_connector = ThinkGearConnector() if tg_connector is None else tg_connector
        self._event_manager = EventManager()
        self._signal_quality: int = 0
        self._connection_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
        self._stream_parser = StreamParser()
        self._parser_connector_supscription: Subscription = None
        self._lock = asyncio.Lock()
        self._read_loop_task: asyncio.Task = None

        self.on_connector_data(self._update_status)

    @property
    def signal_quality(self) -> float:
        """Float signal quality value normalized to the range of 0-100%.

        The raw signal quality value is in the range of 0-200
        (0 indicating a good signal and 200 indicating an off-head state).

        If the raw signal quality value is needed, it can be accessed from the connector data
        through the on_connector_data events.
        """
        return self._signal_quality

    @signal_quality.setter
    def signal_quality(self, value: int) -> None:
        value = abs(value - 200)  # Invert the signal quality value
        value = value / 2  # Normalize the signal quality value to 0-100%
        if value != self._signal_quality:
            self._event_manager.emit(SignalQualityEvent(signal_quality=value))
            self._logger.debug(f"Signal Quality value Changed: {value}%")

        self._signal_quality = float(value)

    @property
    def connection_status(self) -> ConnectionStatus:
        """Current ConnectionStatus of the headset."""
        return self._connection_status

    @connection_status.setter
    def connection_status(self, value: ConnectionStatus) -> None:
        if value != self._connection_status:
            self._event_manager.emit(HeadsetStatusEvent(status=value))

        if value == ConnectionStatus.CONNECTED and self._connection_status != ConnectionStatus.CONNECTED:
            # Connection changed to Connected
            self._logger.info("Connected to MindWaveMobile2 device!")

            self._parser_connector_supscription = self.on_connector_data(self._stream_parser.stream_data)

        elif self._connection_status == ConnectionStatus.CONNECTED and value != ConnectionStatus.CONNECTED:
            # Connection changed from connected to something else
            self._logger.info("MindWaveMobile2 device Disconnected!")
            if self.is_running:
                self.stop()

            self._parser_connector_supscription.detach()

            time.sleep(3)  # Wait for the read loop to stop
            self._event_manager.emit(HeadsetStatusEvent(status=ConnectionStatus.CONNECTION_LOST))

        self._connection_status = value

    def start(self, n_tries=3, timeout=15, blocking=True) -> bool:
        """Start the connection to the MindWaveMobile2 device.

        A connection to be considered successful, the Connection to the TGConnector is not an indication,
        The TGConnector must find and connect to the MindWaveMobile2 device and start streaming data.
        Which is indicated by the ConnectionStatus.CONNECTED.

        Args:
            n_tries (int, optional): The number of connection attempts.
            timeout (int, optional): The timeout for each connection attempt in seconds.
            blocking (bool, optional): Whether to block until the connection is established.

        Returns:
            bool: True if the connection was successful, False otherwise.
            If blocking is False, it returns True if the connection process was started successfully.
        """
        self._setup_event_loop()
        future = asyncio.run_coroutine_threadsafe(self._start_async(n_tries=n_tries, timeout=timeout), self._event_loop)

        if blocking:
            return future.result()
        else:
            return True

    async def _start_async(self, n_tries=3, timeout=15) -> bool:
        """Asynchronously start the connection to the MindWaveMobile2 device.

        Args:
            n_tries (int, optional): The number of connection attempts.
            timeout (int, optional): The timeout for each connection attempt in seconds.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        if self.is_running:
            self._logger.info("MindWaveMobile2 device is already running!")
            return True

        self.is_running = True
        connection_success = await self._connect(n_tries=n_tries, timeout=timeout)

        if not connection_success:
            self.is_running = False
            return False

        return True

    def stop(self, blocking=True) -> bool:
        """Stop the connection to the MindWaveMobile2 device.

        Args:
            blocking (bool, optional): Whether to block until the disconnection is complete.

        Returns:
            bool: True if the disconnection was successful, False otherwise.
            If blocking is False, it returns True if the disconnection process was started successfully.
        """
        self._setup_event_loop()

        future = asyncio.run_coroutine_threadsafe(self._stop_async(), self._event_loop)
        if blocking:
            return future.result()
        else:
            return True

    async def _stop_async(self) -> bool:
        """Asynchronously stop the connection to the MindWaveMobile2 device.

        Returns:
            bool: True if the disconnection was successful, False otherwise.
        """
        if not self.is_running:
            self._logger.info("MindWaveMobile2 device is already stopped!")
            return True

        self._logger.info("Stopping MindWaveMobile2 device...")
        self.is_running = False
        self._read_loop_task.cancel()
        await asyncio.sleep(1)
        return await self._disconnect()

    async def _connect(self, timeout=15, n_tries=3) -> bool:
        """Attempt to connect to the MindWaveMobile2 device.

        This method main purpose is to handle the connection retry mechanism.
        """
        for i in range(1, n_tries + 1):
            if await self._attempt_connect(timeout) is True:
                return True
            elif i < n_tries:
                self._logger.warning(f"Connection timed out. Retrying Attempt {i + 1} ...")
                await asyncio.sleep(1)

        self._logger.error("Maximum number of retries reached. Failed to connect to MindWaveMobile2 device!")
        self.is_running = False
        if self._read_loop_task is not None:
            # It will be None if the connection to the ThinkGearConnector failed
            self._read_loop_task.cancel()
        return False

    async def _attempt_connect(self, timeout=15) -> bool:
        """A single connection attempt to the MindWaveMobile2 device."""

        async def check_bluetooth_connection():
            while self.is_running:
                if self.connection_status == ConnectionStatus.CONNECTED:
                    return True
                await asyncio.sleep(0.5)
            return False

        if await self._tg_connector.connect():
            self._logger.info("Connecting to MindWaveMobile2 device...")

            if self._read_loop_task is None or self._read_loop_task.done():
                self._read_loop_task = asyncio.create_task(self._read_loop())

            try:
                return await asyncio.wait_for(check_bluetooth_connection(), timeout=timeout)
            except asyncio.TimeoutError:
                await self._timeout()
                return False

        return False

    async def _timeout(self) -> None:
        await self._disconnect()
        self._event_manager.emit(TimeoutEvent())

    async def _disconnect(self) -> bool:
        async with self._lock:
            if self.connection_status == ConnectionStatus.DISCONNECTED and not self._tg_connector.is_connected():
                self._logger.info("MindWaveMobile2 device is already disconnected!")
                return True

            self.connection_status = ConnectionStatus.DISCONNECTED
            return self._tg_connector.disconnect()

    def _setup_event_loop(self) -> None:
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

            def run_on_thread(loop: asyncio.AbstractEventLoop):
                asyncio.set_event_loop(loop)
                loop.run_forever()

            self._logger.info(
                "Event loop is not provided and no Event loop is running in the current thread. "
                "Creating a new event loop in a new thread."
            )
            self._event_loop = asyncio.new_event_loop()
            thread = threading.Thread(target=run_on_thread, args=(self._event_loop,), daemon=True)
            thread.start()

    @verbose
    async def _read_loop(self) -> None:
        while self.is_running:
            async with self._lock:
                if self._tg_connector.is_connected():
                    try:
                        out = await self._tg_connector.read()
                        data = json.loads(out)
                        self._event_manager.emit(ConnectorDataEvent(data=data))
                        if "blinkStrength" in data:
                            self._event_manager.emit(BlinkEvent(blink_strength=data["blinkStrength"]))
                            self._logger.debug(f"Blink Triggered with strength: {data['blinkStrength']}")
                    except json.JSONDecodeError:
                        self._logger.error(f"JSONDecodeError: {out}")
                    except UnicodeDecodeError as e:
                        self._logger.error(f"UnicodeDecodeError: {e}, data: {out}")
                    except Exception:
                        self.is_running = False
                        raise
                else:
                    await asyncio.sleep(0.1)

    def _update_status(self, event: ConnectorDataEvent) -> None:
        """Update the connection status based on the received data.

        The process of determining the connection status is based on the received data.
        it might be a naive way but there are no other ways to determine the connection status
        since the "status" field is not always present in the connector data.

        Args:
            event (ConnectorDataEvent): The ConnectorDataEvent containing the received data.
        """
        data = event.data
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

    def on_data(self, callback: Callable[[HeadsetDataEvent], Any]) -> Subscription:
        """Rigister a callback for the processed headset data.

        Args:
            callback (function): The callback function to be called when data is received.

        Returns:
            Subscription: A Subscription object that can be used to detach the callback.
        """
        return self._stream_parser.on_data(callback)

    def on_blink(self, callback: Callable[[BlinkEvent], Any]) -> Subscription:
        """Register a callback for the blink detection event.

        Args:
            callback (function): The callback function to be called when a blink is detected.

        Returns:
            Subscription: the subscription object that can be used to detach the callback
        """
        return self._event_manager.add_listener(EventType.Blink, callback)

    def on_status_change(self, callback: Callable[[HeadsetStatusEvent], Any]) -> Subscription:
        """Register a callback for the headset connection status change event.

        Args:
            callback (function): The callback function to be called when the connection status changes.

        Returns:
            Subscription: the subscription object that can be used to detach the callback
        """
        return self._event_manager.add_listener(EventType.HeadsetStatus, callback)

    def on_signal_quality_change(self, callback: Callable[[SignalQualityEvent], Any]) -> Subscription:
        """Register a callback for the signal quality change event.

        Args:
            callback (function): The callback function to be called when the signal quality changes.

        Returns:
            Subscription: the subscription object that can be used to detach the callback
        """
        return self._event_manager.add_listener(EventType.SignalQuality, callback)

    def on_connector_data(self, callback: Callable[[ConnectorDataEvent], Any]) -> Subscription:
        """Register a callback for the ThinkGear Connector data event.

        Args:
            callback (function): The callback function to be called when data is received from the ThinkGear Connector.

        Returns:
            Subscription: the subscription object that can be used to detach the callback
        """
        return self._event_manager.add_listener(EventType.ConnectorData, callback)

    def on_timeout(self, callback: Callable[[TimeoutEvent], Any]) -> Subscription:
        """Register a callback for the timeout event.

        Args:
            callback (function): The callback function to be called when a timeout occurs.

        Returns:
            Subscription: the subscription object that can be used to detach the callback
        """
        return self._event_manager.add_listener(EventType.Timeout, callback)
