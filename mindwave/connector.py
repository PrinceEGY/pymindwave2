"""ThinkGear Connector Module.

This module provides functionality to establish and manage connections with NeuroSky's
ThinkGear EEG devices through the ThinkGear Connector (TGC) service using a local socket
connection. It enables reading and writing data to/from the device.

Prerequisites:
    Before using this module, the ThinkGear Connector service must be installed and running.
    Download and install from:
    https://download.neurosky.com/public/Products/Utility/TGC/3.2.4/TGC-Setup.exe

Example:
    >>> connector = ThinkGearConnector()
    >>> await connector.connect()
    >>> data = await connector.read()
    >>> connector.disconnect()
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime

from mindwave.utils.event_manager import Event, EventType

from .utils.logger import Logger


@dataclass
class ConnectorDataEvent(Event):
    """ThinkGear Connector Data Event.

    Attributes:
        data (dict): Json formatted data received from the ThinkGear Connector.
        timestamp (datetime): The timestamp when the Data was received.
    """

    def __init__(self, data: dict, timestamp: datetime = None):
        """Initialize the ConnectorDataEvent.

        Args:
            data (dict): The data received from the ThinkGear Connector.
            timestamp (datetime, optional): The timestamp when the event was created.
            if not provided, the current time is used.
        """
        super().__init__(event_type=EventType.ConnectorData, timestamp=timestamp)
        self.data = data


class ThinkGearConnector:
    """Manage connection and communication with the ThinkGear Connector service.

    This class provides methods to establish, maintain, and close connections with the
    ThinkGear Connector service, as well as read and write data to/from the device.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 13854,
        enable_raw_output: bool = True,
        output_format: str = "Json",
    ) -> None:
        """Initialize the ThinkGearConnector.

        The host and port for the ThinkGear Connector service are
        configured with default values of "localhost" and 13854, respectively.
        In most cases, you will not need to modify these settings.

        Args:
            host (str): The hostname of the ThinkGear Connector service.
            port (int): The port number of the ThinkGear Connector service.
            enable_raw_output (bool): Whether to enable raw EEG output.
            output_format (str): The format of the output data. Can be either "Json" or "BinaryPacket".
        """
        self.host: str = host
        self.port: int = port
        self.enable_raw_output: bool = enable_raw_output
        self.output_format: str = output_format
        self.st_writer: asyncio.StreamWriter = None
        self.st_reader: asyncio.StreamReader = None
        self._logger = Logger.get_logger(self.__class__.__name__)

    def write(self, data: bytes) -> None:
        """Write data to the ThinkGear Connector.

        Args:
            data (bytes): The data to be sent to the ThinkGear Connector.

        Raises:
            ConnectionError: If the ThinkGear Connector is not connected
        """
        if not self.is_connected():
            raise ConnectionError("The device is not connected, please connect first using the connect() method.")

        self.st_writer.write(data)

    async def read(self) -> bytes:
        """Read data from the ThinkGear Connector.

        Returns:
            bytes: The data received from the ThinkGear Connector.

        Raises:
            ConnectionError: If the ThinkGear Connector is not connected.
        """
        if not self.is_connected():
            raise ConnectionError("The device is not connected, please connect first using the connect() method.")

        out = await self.st_reader.readuntil(b"\r")
        return out

    async def connect(self) -> bool:
        """Establish connection with the ThinkGear Connector service.

        Attempts to connect to the ThinkGear Connector service using the specified host
        and port. If successful, configures the connection with the specified settings.

        Returns:
            bool: True if connection is successful or already connected, False otherwise.
        """
        self._logger.debug("Initializing connection to ThinkGear Connector...")
        if self.is_connected():
            self._logger.warning(
                "ThinkGear connector is already connected, to reconnect with different settings, "
                "please disconnect first using the disconnect() method."
            )
            return True

        try:
            self.st_reader, self.st_writer = await asyncio.open_connection(self.host, self.port)
            self._logger.debug("Connected to ThinkGear Connector")
        except ConnectionRefusedError:
            self._logger.error(
                f"Connection to ThinkGear Connector at {self.host}:{self.port} refused!, "
                "Check if the ThinkGear Connector is running."
            )
            await asyncio.sleep(3)
            return False

        self.write(
            json.dumps(
                {
                    "enableRawOutput": self.enable_raw_output,
                    "format": self.output_format,
                }
            ).encode("utf-8")
        )
        return True

    def disconnect(self) -> bool:
        """Disconnect from the ThinkGear Connector service.

        Returns:
            bool: True if disconnection is successful or already disconnected.
        """
        self._logger.info("Disconnecting ThinkGear Connector...")

        if not self.is_connected():
            self._logger.debug("The device is already disconnected!")
            return True

        self.st_writer.close()  # Closing st_writer automatically cleans up st_reader as well.
        return True

    def is_connected(self) -> bool:
        """Check if the connection to ThinkGear Connector is active.

        Returns:
            bool: True if connected, False otherwise.
        """
        if not self.st_writer:
            return False

        return not self.st_writer.is_closing()

    def __del__(self) -> None:
        if self.is_connected():
            self.disconnect()
