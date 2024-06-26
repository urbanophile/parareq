import os
from pathlib import Path
import pytest


def test_cli_entrypoint_help():
    exit_status = os.system("parareq --help")
    assert exit_status == 0


def test_cli_entrypoint_dry_run():
    # setup
    # make sure folder exists
    Path("tests/data").mkdir(parents=True, exist_ok=True)
    with open("tests/data/config_example.jsonl", "w") as f:
        f.write('{"input": "Hello, world!"}\n')
        f.write('{"input": ["Hello", "world!"]}\n')
    # create env var
    os.environ["OPENAI_API_KEY"] = "xyz123"

    # test condition

    exit_status = os.system(
        "parareq --dry_run --save_filepath output_example.jsonl --requests_filepath tests/data/config_example.jsonl"
    )

    # teardown
    # os.remove("output_example.jsonl")

    assert exit_status == 0


def test_cli_entrypoint_dry_run_no_request_conf():
    exit_status = os.system(
        "parareq --dry_run --save_filepath output_example.jsonl --requests_filepath doesnt/exist/config_example.jsonl"
    )
    assert exit_status != 0
