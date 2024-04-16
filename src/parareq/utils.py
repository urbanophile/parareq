""" Contains utils for the main parareq module.

    - Define functions
        - api_endpoint_from_url (extracts API endpoint from request URL)
        - append_to_jsonl (writes to results file)
        - num_tokens_consumed_from_request (bigger function to infer token usage from request)
        - task_id_generator_function (yields 1, 2, 3, ...)
"""

import json
from pathlib import Path


def append_to_jsonl(data, filename: str) -> None:
    """Append a json payload to the end of a jsonl file."""
    json_string = json.dumps(data)
    with open(filename, "a") as f:
        f.write(json_string + "\n")


def create_task_id_generator():
    """Generate integers 0, 1, 2, and so on."""
    task_id = 0
    while True:
        yield task_id
        task_id += 1


def nonduplicate_filename(file_path: str) -> str:
    """Ensure that the file path is unique by adding a suffix if necessary."""
    path = Path(file_path)
    if not path.exists():
        return file_path
    else:
        i = 1
        while True:
            new_path = path.with_name(f"{path.stem}_{i}{path.suffix}")
            if not new_path.exists():
                return str(new_path)
            i += 1


def create_requests_file(
    file_path: str = "examples/input/example_requests_to_parallel_process.jsonl",
):
    """The example requests file at openai-cookbook/examples/data/example_requests_to_parallel_process.jsonl
    contains 10,000 requests to text-embedding-ada-002. It was generated with the following code:

    As with all jsonl files, take care that newlines in the content are properly escaped (json.dumps does this automatically).
    """

    n_requests = 10_000
    jobs = [
        {"model": "text-embedding-ada-002", "input": str(x) + "\n"}
        for x in range(n_requests)
    ]
    # check

    with open(file_path, "w") as f:
        for job in jobs:
            json_string = json.dumps(job)
            f.write(json_string + "\n")
