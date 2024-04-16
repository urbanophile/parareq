import json
from unittest.mock import mock_open, patch
import pytest
from parareq.utils import append_to_jsonl


def test_append_to_jsonl():
    # Define test data
    data = {"key": "value"}
    filename = "test_file.jsonl"

    # Mock the open function to avoid writing to an actual file
    with patch("builtins.open", mock_open()) as mock_file:
        # Call the function being tested
        append_to_jsonl(data, filename)

        # Assert that the open function was called with the correct arguments
        mock_file.assert_called_once_with(filename, "a")

        # Assert that the write method was called with the correct argument
        expected_json_string = json.dumps(data) + "\n"
        mock_file().write.assert_called_once_with(expected_json_string)
