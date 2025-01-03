import csv
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from .headset import BlinkEvent, MindWaveMobile2
from .utils.event_manager import Event, EventManager, EventType
from .utils.logger import Logger
from .utils.stream_parser import HeadsetDataEvent


class SessionSignal(Enum):
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


@dataclass
class SessionEvent(Event):
    def __init__(self, signal: SessionSignal, class_name: str = None, timestamp: datetime = None):
        super().__init__(event_type=EventType.SessionEvent, timestamp=timestamp)
        self.signal = signal
        self.class_name = class_name


@dataclass
class SessionConfig:
    user_name: str = None
    user_age: int = None
    user_gender: str = None

    classes: list = field(default_factory=lambda: ["default"])
    trials: int = 1
    baseline_duration: float = 15
    rest_duration: float = 2
    ready_duration: float = 1
    cue_duration: float = 1.5
    motor_duration: float = 4
    extra_duration: float = 0  # Random duration to be added to the motor duration in range [0, extra_duration]
    save_dir: str = "./sessions/"
    capture_blinks: bool = False


class Session:
    def __init__(
        self,
        headset: MindWaveMobile2,
        config: SessionConfig,
        lazy_start: bool = True,
    ):
        self._logger = Logger.get_logger(self.__class__.__name__)
        self.headset = headset
        self.config = config

        self.start_time = None
        self.end_time = None
        self.is_active = False
        self.is_finished = False

        self._event_manager = EventManager()
        self._save_dir = None
        self._data_subscription = None
        self._blinks_subscription = None
        self._data = []
        self._events = []
        self._stop_flag = threading.Event()

        if not lazy_start:
            self.start()

        random.seed(time.perf_counter())

    def start(self) -> None:
        if self.is_active:
            self._logger.info("Session is already active!")
            return
        if self.is_finished:
            self._logger.info("Session is finished!")
            return

        self._data_subscription = self.headset.on_data(self._data_collator)

        if self.config.capture_blinks:
            self._blinks_subscription = self.headset.on_blink(self._blinks_collator)

        self._create_user_dir()
        self._save_info()

        self.is_active = True
        self.start_time = datetime.now()
        self._stop_flag.clear()

        thread = threading.Thread(target=self._events_processor, daemon=True)
        thread.start()

        self._logger.info(f"New Session started at {self.start_time.strftime('%H:%M:%S')}")

    def stop(self) -> None:
        if not self.is_active:
            self._logger.info("Session is not active!")
            return

        self._stop_flag.set()
        self.end_time = datetime.now()

        self.is_active = False
        self.is_finished = True

        self._data_subscription.detach()
        if self.config.capture_blinks:
            self._blinks_subscription.detach()

        self._logger.info(f"Session ended at {self.end_time.strftime('%H:%M:%S')}")

    def save(self):
        if self.is_active:
            self._logger.info("Session is still active!, stop the session before saving")
            return
        if len(self) == 0:
            self._logger.info("Session data is empty!, nothing to save")
            return

        if not self._save_dir:
            self._create_user_dir()

        filename = f"{self._save_dir}/data.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self._data[0].keys())
            writer.writeheader()
            writer.writerows(self._data)

        self._save_events()

        self._logger.info(f"Session collected data is saved to {self._save_dir}")

    def on_event(self, listener):
        return self._event_manager.add_listener(EventType.SessionEvent, listener)

    def _events_processor(self):
        for event, duration in self._event_generator():
            if self._stop_flag.is_set():
                break

            self._logger.info(
                f"Session signal: {event.signal}" + (f" - class: {event.class_name}" if event.class_name else "")
            )
            record = {
                "time": event.timestamp.strftime("%H:%M:%S"),
                "signal": event.signal,
                "class": event.class_name,
            }

            self._events.append(record)
            self._event_manager.emit(event)
            self._stop_flag.wait(duration)

            if event.signal == SessionSignal.SESSION_END:
                self.stop()

    def _event_generator(self):
        """Yields the session events in order in the form of (SessionEvent, duration) tuple"""
        classes_events = self._setup_classes_events()

        yield SessionEvent(SessionSignal.SESSION_START), 1
        yield SessionEvent(SessionSignal.BASELINE_START), self.config.baseline_duration
        yield SessionEvent(SessionSignal.BASELINE_END), 1

        for class_event in classes_events:
            yield SessionEvent(SessionSignal.TRIAL_START, class_name=class_event), 1

            yield SessionEvent(SessionSignal.REST), self.config.rest_duration

            yield SessionEvent(SessionSignal.READY), self.config.ready_duration

            yield SessionEvent(SessionSignal.CUE), self.config.cue_duration

            motor_duration = self.config.motor_duration + random.uniform(0, self.config.extra_duration)
            yield SessionEvent(SessionSignal.MOTOR), motor_duration

            yield SessionEvent(SessionSignal.TRIAL_END, class_event), 1

        yield SessionEvent(SessionSignal.SESSION_END), 0

    def _setup_classes_events(self) -> list:
        classes_events = []

        for class_name in self.config.classes:
            classes_events += [class_name] * self.config.trials
        random.shuffle(classes_events)

        return classes_events

    def _save_events(self):
        if len(self._events) == 0:
            self._logger.info("No session events to save!")
            return

        if not self._save_dir:
            self._create_user_dir()

        file_name = f"{self._save_dir}/events.csv"
        with open(file_name, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self._events[0].keys())
            writer.writeheader()
            writer.writerows(self._events)

    def _data_collator(self, event: HeadsetDataEvent):
        self._logger.debug(f"Data received: {event.data}")
        record = {
            "time": event.timestamp.strftime("%H:%M:%S"),
            "data_type": "headset_data",  # "headset_data" or "blink_data"
            "attention": event.data.attention,
            "meditation": event.data.meditation,
            "delta": event.data.delta,
            "theta": event.data.theta,
            "lowAlpha": event.data.lowAlpha,
            "highAlpha": event.data.highAlpha,
            "lowBeta": event.data.lowBeta,
            "highBeta": event.data.highBeta,
            "lowGamma": event.data.lowGamma,
            "highGamma": event.data.highGamma,
            "raw_data": event.data.raw_data,
            "blink_strength": None,
        }

        self._data.append(record)

    def _blinks_collator(self, event: BlinkEvent):
        self._logger.debug(f"Blink detected: {event.blink_strength}")
        record = {
            "time": event.timestamp.strftime("%H:%M:%S"),
            "data_type": "blink_data",  # "headset_data" or "blink_data"
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
            "blink_strength": event.blink_strength,
        }

        self._data.append(record)

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
            file.write(" User info ".center(40, "=") + "\n\n")
            file.write(f"user_name: {self.config.user_name}\n")
            file.write(f"user_age: {self.config.user_age}\n")
            file.write(f"user_gender: {self.config.user_gender}\n")

            file.write("\n" + " Session info ".center(40, "=") + "\n\n")
            file.write(f"classes: {self.config.classes}\n")
            file.write(f"trials: {self.config.trials}\n")
            file.write(f"capture_blinks: {self.config.capture_blinks}\n")
            file.write(f"save_dir: {self.config.save_dir}\n")

            file.write("\n" + " Durations info ".center(40, "=") + "\n\n")
            file.write(f"baseline_duration: {self.config.baseline_duration}\n")
            file.write(f"rest_duration: {self.config.rest_duration}\n")
            file.write(f"ready_duration: {self.config.ready_duration}\n")
            file.write(f"cue_duration: {self.config.cue_duration}\n")
            file.write(f"motor_duration: {self.config.motor_duration}\n")
            file.write(f"extra_duration: {self.config.extra_duration}\n")

    def __repr__(self) -> str:
        start_time = self.start_time.strftime("%H:%M:%S") if self.start_time else "Session didn't start"
        end_time = self.end_time.strftime("%H:%M:%S") if self.end_time else "Session didn't end"
        return f"Session(start_time:{start_time}, " f"end_time:{end_time}, is_active={self.is_active})"

    def __len__(self) -> int:
        return len(self._data)
