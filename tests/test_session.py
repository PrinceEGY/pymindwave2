import os
import time

import pytest

from mindwave.headset import BlinkEvent, MindWaveMobile2
from mindwave.session import Session, SessionConfig
from mindwave.utils.event_manager import EventManager
from mindwave.utils.logger import Logger
from mindwave.utils.singleton_meta import SingletonMeta
from mindwave.utils.stream_parser import HeadsetDataEvent

Logger.configure_logger(level="ERROR")


def test_start_success(mock_tg_connector, mocker, tmp_path):
    SingletonMeta._instances = {}

    tg_connector = mock_tg_connector(scan_count=1, scan_sleep_duration=0.1)
    headset = MindWaveMobile2(tg_connector=tg_connector)
    headset.start()

    session = Session(headset, SessionConfig(save_dir=tmp_path))
    session.start()

    assert session.is_active is True
    assert session._stop_flag.is_set() is False

    assert session._data_subscription is not None
    assert os.path.exists(session._save_dir)

    # cleanup
    session.stop()
    headset.stop()


def test_start_failure(mock_tg_connector, mocker, tmp_path):
    SingletonMeta._instances = {}

    tg_connector = mock_tg_connector(scan_count=10, scan_sleep_duration=0.5)
    headset = MindWaveMobile2(tg_connector=tg_connector)

    session = Session(headset, SessionConfig(save_dir=tmp_path))

    assert session.is_active is False

    assert session._data_subscription is None
    assert session._save_dir is None


def test_stop(mock_tg_connector, mocker, tmp_path):
    SingletonMeta._instances = {}

    tg_connector = mock_tg_connector(scan_count=1, scan_sleep_duration=0.1)
    headset = MindWaveMobile2(tg_connector=tg_connector)
    headset.start()

    session = Session(headset, SessionConfig(save_dir=tmp_path))
    session.start()

    assert session.is_active is True
    assert session._stop_flag.is_set() is False

    session.stop()

    assert session.is_active is False
    assert session._stop_flag.is_set() is True

    # cleanup
    headset.stop()


def test_data_collection(mocker, tmp_path):
    SingletonMeta._instances = {}
    headset = MindWaveMobile2()
    headset.is_running = True

    session = Session(headset, SessionConfig(save_dir=tmp_path))
    session.start()

    event_manager = EventManager()
    mock_data = mocker.Mock()

    for _ in range(10):
        event_manager.emit(HeadsetDataEvent(mock_data))
    time.sleep(0.5)
    assert len(session._data) == 10


@pytest.mark.parametrize("capture_blinks", [True, False])
def test_blink_collection(mocker, tmp_path, capture_blinks):
    SingletonMeta._instances = {}
    headset = MindWaveMobile2()
    headset.is_running = True

    session = Session(headset, SessionConfig(save_dir=tmp_path, capture_blinks=capture_blinks))
    session.start()

    event_manager = EventManager()
    mock_data = mocker.Mock()

    for _ in range(10):
        event_manager.emit(BlinkEvent(mock_data))
    time.sleep(0.5)

    if capture_blinks is False:
        assert session._blinks_subscription is None
        assert len(session._data) == 0
    else:
        assert session._blinks_subscription is not None
        assert len(session._data) == 10


def test_event_generation(mocker, tmp_path):
    SingletonMeta._instances = {}

    headset = MindWaveMobile2()
    headset.is_running = True

    session = Session(headset, SessionConfig(save_dir=tmp_path, trials=5))
    mocker.patch("threading.Event.wait", return_value=False)

    events_count = 0
    for _ in session._event_generator():
        events_count += 1

    mock_callback = mocker.Mock()
    session.on_event(mock_callback)
    session.start()

    time.sleep(1)
    assert mock_callback.call_count == events_count


def test_save(mocker, tmp_path):
    SingletonMeta._instances = {}

    headset = MindWaveMobile2()
    headset.is_running = True

    session = Session(headset, SessionConfig(save_dir=tmp_path))
    session.start()

    event_manager = EventManager()
    mock_data = mocker.Mock()

    for _ in range(10):
        event_manager.emit(HeadsetDataEvent(mock_data))
    time.sleep(0.5)

    session.stop()
    session.save()

    assert os.path.exists(os.path.join(session._save_dir, "data.csv"))
    assert os.path.exists(os.path.join(session._save_dir, "events.csv"))
    assert os.path.exists(os.path.join(session._save_dir, "session.info"))
