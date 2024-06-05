from datetime import datetime
from mindwave.data import Data
from mindwave.headset import MindWaveMobile2
from util.event_handler import EventType
from util.logger import Logger
import csv


class Session:
    def __init__(
        self,
        headset: MindWaveMobile2,
        capture_blinks: bool = False,
        lazy_start: bool = False,
    ):
        # TODO: handle capture_blinks
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.start_time = None
        self.end_time = None
        self.is_active = False
        self._is_finished = False
        self._session_data = []
        self.headset = headset
        if not lazy_start:
            self.start()

    def start(self) -> None:
        assert not self.is_active, "Session is already active"
        assert not self._is_finished, "Session is already finished"
        self.headset.add_listener(
            event_type=EventType.HeadsetData, listener=self._collator
        )

        self.start_time = datetime.now()
        self.is_active = True
        self._logger.info(
            f"New Session started at {self.start_time.strftime('%H:%M:%S')}"
        )

    def stop(self) -> None:
        assert self.is_active, "Session is not active"
        self.end_time = datetime.now()
        self.headset.remove_listener(
            event_type=EventType.HeadsetData, listener=self._collator
        )

        self.is_active = False
        self._is_finished = True
        self._logger.info(f"Session ended at {self.end_time.strftime('%H:%M:%S')}")

    def save(self, file_name: str):
        assert not self.is_active, "Session is still active"
        assert len(self) > 0, "Session data is empty"
        with open(file_name, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self._session_data[0].keys())
            writer.writeheader()
            writer.writerows(self._session_data)
        self._logger.info(f"Session data saved to {file_name}")

    def _collator(self, data: Data):
        self._logger.debug(f"Data received: {data}")
        curr_time = datetime.now().strftime("%H:%M:%S:%f")
        record = {
            "time": curr_time,
            "attention": data.attention,
            "meditation": data.meditation,
            "delta": data.delta,
            "theta": data.theta,
            "lowAlpha": data.lowAlpha,
            "highAlpha": data.highAlpha,
            "lowBeta": data.lowBeta,
            "highBeta": data.highBeta,
            "lowGamma": data.lowGamma,
            "highGamma": data.highGamma,
            "raw_data": data.raw_data,
        }

        self._session_data.append(record)

    def __repr__(self) -> str:
        start_time = (
            self.start_time.strftime("%H:%M:%S")
            if self.start_time
            else "Session didn't start"
        )
        end_time = (
            self.end_time.strftime("%H:%M:%S")
            if self.end_time
            else "Session didn't end"
        )
        return (
            f"Session(start_time:{start_time}, "
            f"end_time:{end_time}, is_active={self.is_active})"
        )

    def __len__(self) -> int:
        return len(self._session_data)
