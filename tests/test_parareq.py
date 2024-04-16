import os
from pathlib import Path
import pytest
from parareq.parareq import (
    OpenAISettings,
    RateLimiter,
    StatusTracker,
    APIRequest,
    APIRequestProcessor,
)


def test_openai_settings_init():
    """Test the OpenAI settings initialization."""
    settings = OpenAISettings()
    assert settings.api_routes == ["chat", "embedding"]
    assert settings.chat_request_rate == 3500
    assert settings.chat_tokens_rate == 90000


def test_statustracker_init():
    """test the basic status tracker initialization."""
    tracker = StatusTracker()
    assert tracker.num_tasks_started == 0
    assert tracker.last_rate_error_time == 0


def test_apirequest_init():
    """Test the API request processor initialization."""
    api_request = APIRequest(
        task_id=1,
        request_json={"input": "hello"},
        token_consumption=5,
        attempts_left=5,
        metadata={"status": "pending"},
        result=[],
    )

    assert api_request.write_to_file


@pytest.fixture
def mock_environment(monkeypatch):
    # Mock the environment variable
    monkeypatch.setenv("OPENAI_API_KEY", "mock_api_key")


def test_init_api_req_proc_defaults(mock_environment):
    # Test initialization with default values
    instance = APIRequestProcessor()

    assert instance.api_key == "mock_api_key"
    assert instance.save_filepath == "parareq_results.jsonl"
    # Add more assertions for other default values


def test_init_api_req_proc_custom_values(mock_environment):
    # Test initialization with custom values
    instance = APIRequestProcessor(
        api_key="custom_key",
        save_filepath="custom_filepath",
        # Provide other custom values here
    )

    assert instance.api_key == "custom_key"
    assert instance.save_filepath == "custom_filepath"
    # Add more assertions for other custom values
