import csv
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from .headset import MindWaveMobile2
from .utils.event_manager import EventManager
from .utils.logger import Logger
from .utils.stream_parser import Data


class Session:
    def __init__(
        self,
        headset: MindWaveMobile2,
        capture_blinks: bool = False,
        lazy_start: bool = False,
    ):
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.capture_blinks = capture_blinks
        self.headset = headset

        self.start_time = None
        self.end_time = None
        self.is_active = False
        self._is_finished = False
        self._data = []

        if not lazy_start:
            self.start()

    def start(self) -> None:
        if self.is_active:
            self._logger.info("Session is already active!")
            return
        if self._is_finished:
            self._logger.info("Session is finished!")
            return

        self.headset.on_data(self._data_collator)

        if self.capture_blinks:
            self.headset.on_blink(self._blinks_collator)

        self.start_time = datetime.now()
        self.is_active = True
        self._logger.info(f"New Session started at {self.start_time.strftime('%H:%M:%S')}")

    def stop(self) -> None:
        if not self.is_active:
            self._logger.info("Session is not active!")
            return

        self.end_time = datetime.now()

        self.is_active = False
        self._is_finished = True
        self._logger.info(f"Session ended at {self.end_time.strftime('%H:%M:%S')}")

    def save(self, file_name: str):
        if self.is_active:
            self._logger.info("Session is still active!, stop the session before saving")
            return
        if len(self) == 0:
            self._logger.info("Session data is empty!, nothing to save")
            return

        with open(file_name, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self._data[0].keys())
            writer.writeheader()
            writer.writerows(self._data)

        self._logger.info(f"Session data saved to {file_name}")

    def _data_collator(self, data: Data):
        self._logger.debug(f"Data received: {data}")
        curr_time = datetime.now().strftime("%H:%M:%S")
        record = {
            "time": curr_time,
            "event": "headset_data",  # "headset_data" or "blink_data"
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
            "blink_strength": None,
        }

        self._data.append(record)

    def _blinks_collator(self, blink_strength: int):
        self._logger.debug(f"Blink detected: {blink_strength}")
        curr_time = datetime.now().strftime("%H:%M:%S")
        record = {
            "time": curr_time,
            "event": "blink_data",  # "headset_data" or "blink_data"
            "attention": None,
            "meditation": None,
            "delta": None,
            "theta": None,
            "lowAlpha": None,
            "highAlpha": None,
            "lowBeta": None,
            "highBeta": None,
            "lowGamma": None,
            "highGamma": None,
            "raw_data": None,
            "blink_strength": blink_strength,
        }

        self._data.append(record)

    def __repr__(self) -> str:
        start_time = self.start_time.strftime("%H:%M:%S") if self.start_time else "Session didn't start"
        end_time = self.end_time.strftime("%H:%M:%S") if self.end_time else "Session didn't end"
        return f"Session(start_time:{start_time}, " f"end_time:{end_time}, is_active={self.is_active})"

    def __len__(self) -> int:
        return len(self._data)


@dataclass
class SessionConfig:
    user_name: str = None
    user_age: int = None
    user_gender: str = None

    classes: list = field(default_factory=lambda: list())
    trials: int = 1
    baseline_duration: float = 15
    rest_duration: float = 2
    ready_duration: float = 1
    cue_duration: float = 1.5
    motor_duration: float = 4
    extra_duration: float = 0  # Random duration to be added to the motor duration in range [0, extra_duration]
    save_dir: str = "./sessions/"
    capture_blinks: bool = False


class SessionEvent(Enum):
    SESSION_START = 1
    SESSION_END = 2
    BASELINE_START = 3
    BASELINE_END = 4
    TRIAL_START = 5
    TRIAL_END = 6
    REST = 7
    READY = 8
    CUE = 9
    MOTOR = 10


class SessionManager:
    def __init__(self, headset: MindWaveMobile2, config: SessionConfig, max_workers: int = 4):
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.headset = headset
        self.config = config
        self._event_manager = EventManager(max_workers=max_workers)
        self._events = []
        self._save_dir = None

        self.session = Session(
            headset=headset,
            capture_blinks=config.capture_blinks,
            lazy_start=True,
        )

        random.seed(time.perf_counter())

    def start(self) -> None:
        if self.session.is_active:
            self._logger.info("Session is already active!")
            return

        # Create user directory
        self._create_user_dir()
        self._save_info()

        self.session.start()
        thread = threading.Thread(target=self._session_loop)
        thread.start()

        self.add_listener(self._session_handler)

    def stop(self) -> None:
        # TODO:
        pass

    def add_listener(self, listener):
        self._event_manager.add_listener(SessionEvent, listener)

    def remove_listener(self, listener):
        self._event_manager.remove_listener(SessionEvent, listener)

    def _create_user_dir(self):
        # create user dir with incremental number if already exists
        base_dir = Path(self.config.save_dir)
        i = 1
        user_dir = base_dir / f"{self.config.user_name}_{str(i).zfill(2)}"

        while user_dir.exists():
            i += 1
            user_dir = base_dir / f"{self.config.user_name}_{str(i).zfill(2)}"

        user_dir.mkdir(parents=True, exist_ok=True)

        self._save_dir = str(user_dir)

    def _save_info(self):
        file_name = f"{self._save_dir}/session.info"
        with open(file_name, mode="w") as file:
            file.write(" User info ".center(40, "=") + "\n")
            file.write(f"user_name: {self.config.user_name}\n")
            file.write(f"user_age: {self.config.user_age}\n")
            file.write(f"user_gender: {self.config.user_gender}\n")

            file.write("\n" + "=" * 20 + "\n\n")
            file.write(" Session info ".center(40, "=") + "\n")
            file.write(f"classes: {self.config.classes}\n")
            file.write(f"trials: {self.config.trials}\n")
            file.write(f"capture_blinks: {self.config.capture_blinks}\n")
            file.write(f"save_dir: {self.config.save_dir}\n")

            file.write("\n" + "=" * 20 + "\n\n")
            file.write(" Durations info ".center(40, "=") + "\n")
            file.write(f"baseline_duration: {self.config.baseline_duration}\n")
            file.write(f"rest_duration: {self.config.rest_duration}\n")
            file.write(f"ready_duration: {self.config.ready_duration}\n")
            file.write(f"cue_duration: {self.config.cue_duration}\n")
            file.write(f"motor_duration: {self.config.motor_duration}\n")
            file.write(f"extra_duration: {self.config.extra_duration}\n")

    def _session_handler(self, *args):
        event: SessionEvent = args[0]
        self._logger.info(f"Session event: {event.name}, class: {args[1] if len(args) > 1 else None}")
        curr_time = datetime.now().strftime("%H:%M:%S")
        record = {
            "time": curr_time,
            "event": event.name,
            "class": args[1] if len(args) > 1 else None,
        }

        self._events.append(record)
        if event == SessionEvent.SESSION_END:
            self.session.stop()
            self.remove_listener(self._session_handler)

            self._save_events()
            self.session.save(f"{self._save_dir}/data.csv")

    def _session_loop(self) -> None:
        classes_events = self._setup_classes_events()

        time.sleep(1)
        self.self._event_manager.emit(SessionEvent, SessionEvent.SESSION_START)
        time.sleep(1)

        self.self._event_manager.emit(SessionEvent, SessionEvent.BASELINE_START)
        time.sleep(self.config.baseline_duration)

        self.self._event_manager.emit(SessionEvent, SessionEvent.BASELINE_END)

        for class_event in classes_events:
            self.self._event_manager.emit(SessionEvent, SessionEvent.TRIAL_START, class_event)

            self.self._event_manager.emit(SessionEvent, SessionEvent.REST)
            time.sleep(self.config.rest_duration)

            self.self._event_manager.emit(SessionEvent, SessionEvent.READY)
            time.sleep(self.config.ready_duration)

            self.self._event_manager.emit(SessionEvent, SessionEvent.CUE)
            time.sleep(self.config.cue_duration)

            self.self._event_manager.emit(SessionEvent, SessionEvent.MOTOR)
            time.sleep(self.config.motor_duration)
            time.sleep(random.uniform(0, self.config.extra_duration))

            self.self._event_manager.emit(SessionEvent, SessionEvent.TRIAL_END, class_event)

        self.self._event_manager.emit(SessionEvent, SessionEvent.SESSION_END)

    def _setup_classes_events(self) -> list:
        classes_events = []

        for class_name in self.config.classes:
            classes_events += [class_name] * self.config.trials
        random.shuffle(classes_events)

        return classes_events

    def _save_events(self):
        if len(self._events) == 0:
            self._logger.info("No events to save")
            return

        Path(self.config.save_dir).mkdir(parents=True, exist_ok=True)
        file_name = f"{self._save_dir}/events.csv"

        with open(file_name, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self._events[0].keys())
            writer.writeheader()
            writer.writerows(self._events)

        self._logger.info(f"Session events saved to {file_name}")
