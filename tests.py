from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from config.models import Message
from worker import Worker


@pytest.fixture
def worker():
    return Worker()


@pytest.fixture
def message():
    mock_message = MagicMock(spec=Message)
    mock_message.id = 1
    mock_message.room_id = 1
    mock_message.room = MagicMock()
    mock_message.kind = Message.KIND_TEXT
    mock_message.current_task = Message.TASK_GPT
    mock_message.state = Message.RUNNING
    mock_message.created_at = datetime.now(timezone.utc)
    mock_message.updated_at = datetime.now(timezone.utc)
    mock_message.notifications = True
    return mock_message


def test_on_message_existing_message(worker, message, mocker):
    mocker.patch('config.models.Message.get_or_none', return_value=message)
    mocker.patch.object(worker, 'process_response')
    body = {'message_id': 1}

    worker.on_message(body, MagicMock())

    worker.process_response.assert_called_once_with(message, body)


def test_on_message_non_existing_message(worker, mocker):
    mocker.patch('config.models.Message.get_or_none', return_value=None)
    body = {'message_id': 1}

    with patch('worker.logger') as mock_logger:
        worker.on_message(body, MagicMock())
        mock_logger.info.assert_any_call('Message 1 does not exist')


def test_handle_processing_error(worker, message, mocker):
    mocker.patch.object(message, 'save')
    error_message = 'Test error message'
    exception = Exception(error_message)

    with patch('worker.logger') as mock_logger:
        worker.handle_processing_error(message, error_message, exception)
        mock_logger.exception.assert_called_once_with(error_message, exc_info=exception)

    assert message.state == Message.FAILED
    message.save.assert_called_once()


def test_create_response_message(worker, message, mocker):
    mocker.patch('config.models.Message.create', return_value=message)
    body = {'result': 'Test result'}
    response = worker.create_response_message(message, body, Message.TASK_GPT, text='Test result')

    assert response == message
