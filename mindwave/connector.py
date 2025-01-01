import asyncio
import json

from .utils.logger import Logger


class ThinkGearConnector:
    def __init__(self, host="localhost", port=13854, enable_raw_output=True, output_format="Json"):
        self.host: str = host
        self.port: int = port
        self.enable_raw_output: bool = enable_raw_output
        self.output_format: str = output_format
        self.st_writer: asyncio.StreamWriter = None
        self.st_reader: asyncio.StreamReader = None
        self._logger = Logger.get_logger(self.__class__.__name__)

    def write(self, data):
        self.st_writer.write(data)

    async def read(self):
        if not self.is_connected():
            raise ConnectionError("The device is not connected, please connect first using the connect() method.")

        out = await self.st_reader.readuntil(b"\r")
        return out

    async def connect(self):
        self._logger.debug("Initializing connection to ThinkGear Connector...")
        if self.is_connected():
            self._logger.warning(
                "The ThinkGear connector is already connected, to reconnect with different settings, "
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

    def disconnect(self):
        self._logger.info("Disconnecting ThinkGear Connector...")

        if not self.is_connected():
            self._logger.debug("The device is already disconnected!")
            return True

        self.st_writer.close()  # Closing the st_writer automatically cleans up the st_reader as well.
        return True

    def is_connected(self):
        if not self.st_writer:
            return False

        return not self.st_writer.is_closing()

    def __del__(self):
        if self.is_connected():
            self.disconnect()
