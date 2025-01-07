import asyncio
import random

import pytest

from mindwave.connector import ThinkGearConnector

SCANNING_DATA = b'{"poorSignalLevel":200,"status":"scanning"}\r'
CONNECTED_DATA = {
    "rawEeg": b'{"rawEeg":%d}\r',
    "eSense": b'{"eSense":{"attention":%d,"meditation":%d},\
    "eegPower":{"delta":%d,"theta":%d,"lowAlpha":%d,"highAlpha":%d,\
    "lowBeta":%d,"highBeta":%d,"lowGamma":%d,"highGamma":%d},"poorSignalLevel":%d}\r',
    "blinkStrength": b'{"blinkStrength":%d}\r',
}


def generate_random_data(data_type=None):
    if data_type == "rawEeg":
        return CONNECTED_DATA["rawEeg"] % random.randint(-2048, 2048)
    elif data_type == "eSense":
        return CONNECTED_DATA["eSense"] % (
            random.randint(0, 100),  # attention
            random.randint(0, 100),  # meditation
            random.randint(0, 1000000),  # delta
            random.randint(0, 1000000),  # theta
            random.randint(0, 100000),  # lowAlpha
            random.randint(0, 1000000),  # highAlpha
            random.randint(0, 100000),  # lowBeta
            random.randint(0, 1000000),  # highBeta
            random.randint(0, 100000),  # lowGamma
            random.randint(0, 1000000),  # highGamma
            random.randint(0, 200),  # poorSignalLevel
        )
    elif data_type == "blinkStrength":
        return CONNECTED_DATA["blinkStrength"] % random.randint(0, 255)


class MockThinkGearConnector:
    def __init__(self, mocker, scan_count=10, scan_sleep_duration=0.5):
        self.mocker = mocker
        self.scan_count = scan_count
        self.scan_sleep_duration = scan_sleep_duration
        self.tg_connector = ThinkGearConnector()
        self._connection_indication = False

        self.data_queue = []

        mocker.patch("mindwave.connector.ThinkGearConnector.read", side_effect=self.mock_read)
        mocker.patch("mindwave.connector.ThinkGearConnector.connect", side_effect=self._connect)
        mocker.patch("mindwave.connector.ThinkGearConnector.disconnect", side_effect=self._disconnect)

    async def mock_read(self):
        if self.scan_count > 0:
            await asyncio.sleep(self.scan_sleep_duration)
            self.scan_count -= 1
            return SCANNING_DATA

        if not self._connection_indication:
            # send random data once to indicate connection
            self._connection_indication = True
            return generate_random_data(data_type="rawEeg")

        if not self.data_queue:
            self.data_queue = self._prepare_data_queue()
            await asyncio.sleep(1)

        data_type = self.data_queue.pop(0)

        return generate_random_data(data_type=data_type)

    def get_connector(self):
        return self.tg_connector

    def _prepare_data_queue(self):
        data_types = ["rawEeg"] * 512 + ["eSense"] * 1 + ["blinkStrength"] * random.randint(0, 2)
        random.shuffle(data_types)
        return data_types

    async def _connect(self):
        self.tg_connector.st_writer = self.mocker.Mock()
        self.tg_connector.st_reader = self.mocker.AsyncMock()
        self.tg_connector.st_writer.is_closing.return_value = False
        return True

    def _disconnect(self):
        self.tg_connector.st_writer = None
        self.tg_connector.st_reader = None
        return True


@pytest.fixture
def mock_tg_connector(mocker):
    def create_mock(scan_count=0, scan_sleep_duration=0.5):
        return MockThinkGearConnector(mocker, scan_count, scan_sleep_duration).get_connector()

    return create_mock
