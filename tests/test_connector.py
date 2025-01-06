import json

import pytest

from mindwave.connector import ThinkGearConnector
from mindwave.utils.logger import Logger

Logger.configure_logger(level="ERROR")


@pytest.mark.asyncio(loop_scope="session")
async def test_connect_success(mocker):
    tg_connector = ThinkGearConnector()
    mock_reader = mocker.AsyncMock()
    mock_writer = mocker.Mock()

    mocker.patch("asyncio.open_connection", return_value=(mock_reader, mock_writer))

    result = await tg_connector.connect()

    assert result is True
    assert tg_connector.st_reader == mock_reader
    assert tg_connector.st_writer == mock_writer

    expected_config = {"enableRawOutput": True, "format": "Json"}
    mock_writer.write.assert_called_once_with(json.dumps(expected_config).encode("utf-8"))


@pytest.mark.asyncio(loop_scope="session")
async def test_connect_failure(mocker):
    tg_connector = ThinkGearConnector()
    mocker.patch("asyncio.open_connection", side_effect=ConnectionRefusedError)
    mocker.patch("asyncio.sleep", return_value=False)

    result = await tg_connector.connect()

    assert result is False
    assert tg_connector.st_reader is None
    assert tg_connector.st_writer is None


@pytest.mark.asyncio(loop_scope="session")(loop_scope="session")
async def test_connect_already_connected(mocker):
    tg_connector = ThinkGearConnector()
    mock_reader = mocker.AsyncMock()
    mock_writer = mocker.Mock()
    mock_writer.is_closing.return_value = False
    tg_connector.st_reader = mock_reader
    tg_connector.st_writer = mock_writer

    # Try connecting again
    result = await tg_connector.connect()

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_read_success(mocker):
    tg_connector = ThinkGearConnector()
    # Setup mock connection
    mock_reader = mocker.AsyncMock()
    mock_writer = mocker.Mock()
    mock_writer.is_closing.return_value = False
    tg_connector.st_reader = mock_reader
    tg_connector.st_writer = mock_writer

    # Mock read data
    expected_data = b"mocked data\r"
    mock_reader.readuntil.return_value = expected_data

    data = await tg_connector.read()
    assert data == expected_data
    mock_reader.readuntil.assert_called_once_with(b"\r")


@pytest.mark.asyncio(loop_scope="session")
async def test_read_not_connected(mocker):
    tg_connector = ThinkGearConnector()
    # Setup mock connection
    mock_reader = mocker.AsyncMock()
    mock_writer = mocker.Mock()
    tg_connector.st_reader = mock_reader
    tg_connector.st_writer = mock_writer
    tg_connector.st_reader.is_closing.return_value = True

    with pytest.raises(ConnectionError):
        await tg_connector.read()


def test_disconnect_success(mocker):
    tg_connector = ThinkGearConnector()
    # Setup mock connection
    mock_writer = mocker.Mock()
    mock_writer.is_closing.return_value = False
    tg_connector.st_writer = mock_writer

    result = tg_connector.disconnect()

    assert result is True
    mock_writer.close.assert_called_once()


def test_disconnect_already_disconnected():
    tg_connector = ThinkGearConnector()
    result = tg_connector.disconnect()

    assert result is True


def test_is_connected(mocker):
    tg_connector = ThinkGearConnector()
    # Test when not connected
    assert not tg_connector.is_connected()

    # Test when connected
    mock_writer = mocker.Mock()
    mock_writer.is_closing.return_value = False
    tg_connector.st_writer = mock_writer
    assert tg_connector.is_connected()

    # Test when writer is closing
    mock_writer.is_closing.return_value = True
    assert not tg_connector.is_connected()


def test_write(mocker):
    tg_connector = ThinkGearConnector()
    mock_writer = mocker.Mock()
    tg_connector.st_writer = mock_writer
    test_data = b"test_data"

    tg_connector.write(test_data)
    mock_writer.write.assert_called_once_with(test_data)
