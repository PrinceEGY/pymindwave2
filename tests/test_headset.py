import time

from mindwave.headset import ConnectionStatus, MindWaveMobile2
from mindwave.utils.logger import Logger
from mindwave.utils.singleton_meta import SingletonMeta

Logger.configure_logger(level="ERROR")


def test_start_success(mock_tg_connector, mocker):
    SingletonMeta._instances = {}

    tg_connector = mock_tg_connector(scan_count=1, scan_sleep_duration=0.1)
    headset = MindWaveMobile2(tg_connector=tg_connector)

    assert headset._tg_connector is tg_connector

    result = headset.start()
    assert result is True
    assert headset.is_running is True
    assert headset.connection_status is ConnectionStatus.CONNECTED

    # cleanup
    headset.stop()


def test_start_timeout(mock_tg_connector, mocker):
    SingletonMeta._instances = {}

    tg_connector = mock_tg_connector(scan_count=10, scan_sleep_duration=0.5)

    headset = MindWaveMobile2(tg_connector=tg_connector)
    mock_callback = mocker.Mock()
    _ = headset.on_timeout(mock_callback)

    value = headset.start(timeout=1, n_tries=1)
    assert value is False
    assert headset.is_running is False
    mock_callback.assert_called_once()


def test_stop_device(mock_tg_connector):
    SingletonMeta._instances = {}

    tg_connector = mock_tg_connector(scan_count=1, scan_sleep_duration=0.1)
    headset = MindWaveMobile2(tg_connector=tg_connector)

    value = headset.start(timeout=5)
    assert value is True

    headset.stop()
    assert headset.is_running is False
    assert headset.connection_status == ConnectionStatus.DISCONNECTED


def test_multiple_start_attempts(mock_tg_connector, mocker):
    SingletonMeta._instances = {}

    tg_connector = mock_tg_connector(scan_count=50, scan_sleep_duration=0.2)
    headset = MindWaveMobile2(tg_connector=tg_connector)

    mock_callback = mocker.Mock()
    headset.on_timeout(mock_callback)

    value = headset.start(timeout=1, n_tries=5)
    time.sleep(0.5)  # wait for the timeouts to be called
    assert value is False
    assert headset.is_running is False
    assert mock_callback.call_count == 5

    # cleanup
    headset.stop()


def test_data_callback(mock_tg_connector, mocker):
    SingletonMeta._instances = {}

    tg_connector = mock_tg_connector(scan_count=1, scan_sleep_duration=0.1)
    headset = MindWaveMobile2(tg_connector=tg_connector)

    data_callback = mocker.Mock()
    headset.on_data(data_callback)

    value = headset.start(timeout=5)
    assert value is True

    time.sleep(1.5)  # wait for data to be received

    data_callback.assert_called()

    # cleanup
    headset.stop()
