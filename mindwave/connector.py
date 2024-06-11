from telnetlib import Telnet
import json

from util.logger import Logger


class MindWaveConnector:
    def __init__(
        self, host="localhost", port=13854, enable_raw_output=True, output_format="Json"
    ):
        self.host = host
        self.port = port
        self.enable_raw_output = enable_raw_output
        self.output_format = output_format
        self.tn = Telnet()
        self._logger = Logger._instance.get_logger(self.__class__.__name__)

    def write(self, data):
        self.tn.write(data)

    def read(self):
        assert (
            self.is_connected()
        ), "The device is not connected, please connect first using the connect() method."
        out = self.tn.read_until(b"\r")
        return out

    def connect(self):
        self._logger.info("Initializing connection to ThinkGear Connector...")
        assert (
            not self.is_connected()
        ), "The device is already connected, to reconnect with different settings, please disconnect first using the disconnect() method."
        try:
            self.tn.open(self.host, self.port)
        except ConnectionRefusedError:
            self._logger.error(
                f"Connection to ThinkGear Connector at {self.host}:{self.port} refused!, Check if the ThinkGear Connector is running."
            )
            return False
        self.tn.write(
            json.dumps(
                {
                    "enableRawOutput": self.enable_raw_output,
                    "format": self.output_format,
                }
            ).encode("utf-8")
        )

    def disconnect(self):
        self._logger.info("Disconnecting ThinkGear Connector...")
        assert self.is_connected(), "The device is not connected"
        self.tn.close()

    def is_connected(self):
        return self.tn.get_socket() is not None

    def __del__(self):
        if self.is_connected():
            self.disconnect()
