"""Session module for handling the EEG data collection sessions.

This module provides functionality for creating and managing sessions that record data
streamed from a MindWave Mobile 2 EEG headset. It handles session configuration,
event management, data collection, and storage.
"""

import csv
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from .headset import BlinkEvent, MindWaveMobile2
from .utils.event_manager import Event, EventManager, EventType, Subscription
from .utils.logger import Logger
from .utils.stream_parser import HeadsetDataEvent


class SessionSignal(Enum):
    """Enumeration of signals emitted during a session."""

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
    """Session Event.

    Attributes:
        signal (SessionSignal): The signal emitted during the session.
        class_name (str): The class name associated with the event.
        (e.g., the class being imagined during a motor imagery task).
        timestamp (datetime): The timestamp of the event.
    """

    def __init__(self, signal: SessionSignal, class_name: str = None, timestamp: datetime = None) -> None:
        """Initializes a new SessionEvent instance.

        Args:
            signal (SessionSignal): The signal emitted during the session.
            class_name (str, optional): The class name associated with the event.
            (e.g., the class being imagined during a motor imagery task).
            timestamp (datetime, optional): The timestamp of the event.
        """
        super().__init__(event_type=EventType.SessionEvent, timestamp=timestamp)
        self.signal = signal
        self.class_name = class_name


@dataclass
class SessionConfig:
    """Configuration settings for a session.

    Attributes:
        user_name (str): Name of the user.
        user_age (int): Age of the user.
        user_gender (str): Gender of the user.
        classes (list): List of class names for the session.
        trials (int): Number of trials per class.
        baseline_duration (float): Duration of the baseline phase in seconds.
        rest_duration (float): Duration of the rest phase in seconds.
        ready_duration (float): Duration of the ready phase in seconds.
        cue_duration (float): Duration of the cue phase in seconds.
        motor_duration (float): Duration of the motor phase in seconds.
        extra_duration (float): Additional random duration added to motor phase.
        save_dir (str): Directory to save session data.
        capture_blinks (bool): Whether to capture blink events.
    """

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
    # Random duration to be added to the motor duration in range [0, extra_duration]
    extra_duration: float = 0
    save_dir: str = "./sessions/"
    capture_blinks: bool = False


class Session:
    """Manages EEG headset data collection sessions.

    This class handles the configuration, execution, and data storage of EEG data collection sessions.

    It also emits signals at different stages of the session, this can be used to build a UI on top of it.

    Session flow:

    - Session Start signal: Indicates the start of the session.
    - Baseline Start signal: Indicates the start of the baseline phase.
    - Baseline End signal: Indicates the end of the baseline phase.
    for trial in range(trials*len(classes)):
        - Trial Start signal: Indicates the start of a new trial associated with a class.
        - Rest signal: Indicates the rest phase before starting the motor imagery task.
        - Ready signal: Indicates the ready phase before the cue.
        - Cue signal: Indicates the cue phase for the motor imagery task.
        - Motor signal: Indicates the start of the motor imagery task.
        - Trial End signal: Indicates the end of the trial associated with a class.
    - Session End signal: Indicates the end of the session.
    """

    def __init__(
        self,
        headset: MindWaveMobile2,
        config: SessionConfig,
        lazy_start: bool = True,
    ) -> None:
        """Initializes a new Session instance.

        Args:
            headset (MindWaveMobile2): The MindWave Mobile 2 headset instance.
            config (SessionConfig): The configuration settings for the session.
            lazy_start (bool, optional): Whether to start the session immediately after initialization.
        """
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
        """Starts the data collection session.

        NOTE: The headset must be running before starting the session.
        """
        if not self.headset.is_running:
            self._logger.info("Headset is not running!, start headset before starting the session")
            return
        if self.is_active:
            self._logger.info("Session is already active!")
            return
        if self.is_finished:
            self._logger.info("Session is finished!")
            return

        self._data_subscription = self.headset.on_data(self._data_collator)
        if self.config.capture_blinks:
            self._blinks_subscription = self.headset.on_blink(self._data_collator)

        self._create_user_dir()
        self._save_info()

        self.is_active = True
        self.start_time = datetime.now()
        self._stop_flag.clear()

        thread = threading.Thread(target=self._events_processor, daemon=True)
        thread.start()

        self._logger.info(f"New Session started at {self.start_time.strftime('%H:%M:%S')}")

    def stop(self) -> None:
        """Stops the data collection session."""
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
        """Saves the collected session data and events to disk."""
        if self.is_active:
            self._logger.info("Session is still active!, stop the session before saving")
            return
        if len(self) == 0:
            self._logger.info("Session data is empty!, nothing to save")
            return

        if not self._save_dir:
            self._create_user_dir()

        filename = f"{self._save_dir}/data.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self._data[0].keys())
            writer.writeheader()
            writer.writerows(self._data)

        self._save_events()

        self._logger.info(f"Session collected data is saved to {self._save_dir}")

    def on_signal(self, listener: Callable[[SessionEvent], Any]) -> Subscription:
        """Registers a listener for session signals.

        Args:
            listener: The listener function to be called when a session event is emitted.

        Returns:
            Subscription: A Subscription object that can be used to unsubscribe the listener.
        """
        return self._event_manager.add_listener(EventType.SessionEvent, listener)

    def _events_processor(self) -> None:

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
        """Yield the session events in order in the form of (SessionEvent, duration) tuple."""
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

    def _save_events(self) -> None:
        if len(self._events) == 0:
            self._logger.info("No session events to save!")
            return

        if not self._save_dir:
            self._create_user_dir()

        file_name = f"{self._save_dir}/events.csv"
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self._events[0].keys())
            writer.writeheader()
            writer.writerows(self._events)

    def _data_collator(self, event: Event) -> None:
        self._logger.debug(f"Session headset event received: {event}")
        record = {
            "time": event.timestamp.strftime("%H:%M:%S"),
            "data_type": None,  # "headset_data" or "blink_data"
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
            "blink_strength": None,
        }
        if isinstance(event, BlinkEvent) and self.config.capture_blinks:
            record["data_type"] = "blink_data"
            record["blink_strength"] = event.blink_strength
        elif isinstance(event, HeadsetDataEvent):
            record["data_type"] = "headset_data"
            record["attention"] = event.data.attention
            record["meditation"] = event.data.meditation
            record["delta"] = event.data.delta
            record["theta"] = event.data.theta
            record["lowAlpha"] = event.data.lowAlpha
            record["highAlpha"] = event.data.highAlpha
            record["lowBeta"] = event.data.lowBeta
            record["highBeta"] = event.data.highBeta
            record["lowGamma"] = event.data.lowGamma
            record["highGamma"] = event.data.highGamma
            record["raw_data"] = event.data.raw_data

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

    def _save_info(self) -> None:
        file_name = f"{self._save_dir}/session.info"
        with open(file_name, mode="w", encoding="utf-8") as file:
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
