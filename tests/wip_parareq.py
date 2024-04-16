import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from parareq.parareq import (
    APIRequest,
    StatusTracker,
    APIRequestProcessor,
)  # Import your classes from the actual module
import json


@pytest.mark.asyncio
async def test_api_request_init():
    api_request = APIRequest(
        task_id=1,
        request_json={"key": "value"},
        token_consumption=0,
        attempts_left=3,
        metadata={"metadata_key": "metadata_value"},
    )
    assert api_request.task_id == 1
    assert api_request.request_json == {"key": "value"}
    assert api_request.token_consumption == 0
    assert api_request.attempts_left == 3
    assert api_request.metadata == {"metadata_key": "metadata_value"}
    assert api_request.result == []


@patch("parareq.parareq.aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_api_request_successful_call(mock_session):
    session = MagicMock()
    session.put.return_value.__aenter__.return_value.status = 200
    session.put.return_value.__aenter__.return_value.json.return_value = {
        "response": "response_val"
    }
    mock_session.return_value.__aenter__.return_value = session

    status_tracker = StatusTracker()  # You can initialize this with the required values
    status_tracker.num_tasks_in_progress = 1

    async_queue_mock = MagicMock()
    # Create an instance of APIRequest
    api_request = APIRequest(
        task_id=1,
        request_json={"request_key": "request_value"},
        token_consumption=0,
        attempts_left=3,
        metadata={"metadata_key": "metadata_value"},
        write_to_file=False,
    )

    # Call the API method
    await api_request.call_api(
        "https://example.com/api",
        {"Authorization": "Bearer your_token"},
        async_queue_mock,
        "/path/to/save_file.json",
        status_tracker,
    )

    # Assertions
    # assert api_request.result == [{"response_key": "response_value"}]
    assert status_tracker.num_tasks_succeeded == 1
    assert status_tracker.num_tasks_in_progress == 0

    # Additional assertions as needed
    # For example, you can assert that the aiohttp.ClientSession was called with the correct parameters


@patch("parareq.parareq.aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_api_request_api_error(mock_session):
    ##### setup
    session = MagicMock()
    session.put.return_value.__aenter__.return_value.status = 200
    session.put.return_value.__aenter__.return_value.json.return_value = {
        "error": "Some error message"
    }
    mock_session.return_value.__aenter__.return_value = session

    status_tracker = StatusTracker()  # You can initialize this with the required values
    status_tracker.num_tasks_in_progress = 1

    async_queue_mock = MagicMock()

    ##### test
    # Create an instance of APIRequest
    api_request = APIRequest(
        task_id=1,
        request_json={"request_key": "request_value"},
        token_consumption=0,
        attempts_left=3,
        metadata={"metadata_key": "metadata_value"},
        write_to_file=False,
    )

    await api_request.call_api(
        request_url="https://example.com",
        request_header={"Content-Type": "application/json"},
        retry_queue=async_queue_mock,
        save_filepath="test.json",
        status_tracker=status_tracker,
    )

    # Assert that the result is saved correctly
    api_error_response = ["!!!!"]  # fixme: what is the correct response?
    assert api_request.result == [api_error_response]

    # Assert that status tracker variables are updated accordingly
    assert status_tracker.num_api_errors == 1
    assert status_tracker.num_tasks_in_progress == 0


@patch("parareq.parareq.aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_api_request_exception(mock_session):
    ##### setup
    session = MagicMock()
    session.put.return_value.__aenter__.return_value.status = 200
    session.put.return_value.__aenter__.return_value.json.return_value = (
        pytest.Exception()
    )
    mock_session.return_value.__aenter__.return_value = session

    status_tracker = StatusTracker()  # You can initialize this with the required values
    status_tracker.num_tasks_in_progress = 1

    async_queue_mock = MagicMock()

    ##### test
    # Create an instance of APIRequest
    api_request = APIRequest(
        task_id=1,
        request_json={"request_key": "request_value"},
        token_consumption=0,
        attempts_left=3,
        metadata={"metadata_key": "metadata_value"},
        write_to_file=False,
    )


# @patch("parareq.parareq.aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_request_processor_init():
    request_processor = APIRequestProcessor(
        api_key="YOUR_API_KEY",
        save_filepath="test.json",
        request_url="https://example.com",
        max_requests_per_minute=3_500 * 0.75,
        max_tokens_per_minute=90_000 * 0.75,
        token_encoding_name="cl100k_base",
        max_attempts=5,
        logging_level=20,
    )


# @patch("parareq.parareq.aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_request_processor_run_single():
    pass


@pytest.mark.asyncio
async def test_request_processor_run_multiple():
    pass


# @patch("parareq.parareq.aiohttp.ClientSession")
# @pytest.mark.asyncio
def test_parareq_cli():
    pass
