""" Contains utils for the main parareq module.

    - Define functions
        - api_endpoint_from_url (extracts API endpoint from request URL)
        - append_to_jsonl (writes to results file)
        - num_tokens_consumed_from_request (bigger function to infer token usage from request)
        - task_id_generator_function (yields 1, 2, 3, ...)
"""

import re  # for matching endpoint from request URL
import json
import tiktoken
from pathlib import Path


def openai_api_endpoint_from_url(request_url):
    """Extract the API endpoint from the request URL."""

    match = re.search("^https://[^/]+/v\\d+/(.+)$", request_url)
    print(match.groups())
    if match is not None and len(match.groups()) > 0:
        return match[1]
    else:
        raise ValueError(f"Invalid request URL: {request_url}")


def append_to_jsonl(data, filename: str) -> None:
    """Append a json payload to the end of a jsonl file."""
    json_string = json.dumps(data)
    with open(filename, "a") as f:
        f.write(json_string + "\n")


def openai_num_tokens_consumed_from_request(
    request_json: dict,
    api_endpoint: str,
    token_encoding_name: str,
):
    """Count the number of tokens in the request. Only supports completion and embedding requests."""
    encoding = tiktoken.get_encoding(token_encoding_name)
    # if completions request, tokens = prompt + n * max_tokens
    if api_endpoint.endswith("completions"):
        max_tokens = request_json.get("max_tokens", 15)
        n = request_json.get("n", 1)
        completion_tokens = n * max_tokens

        # chat completions
        if api_endpoint.startswith("chat/"):
            num_tokens = 0
            for message in request_json["messages"]:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens -= 1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens + completion_tokens
        # normal completions
        else:
            prompt = request_json["prompt"]
            if isinstance(prompt, str):  # single prompt
                prompt_tokens = len(encoding.encode(prompt))
                num_tokens = prompt_tokens + completion_tokens
                return num_tokens
            elif isinstance(prompt, list):  # multiple prompts
                prompt_tokens = sum([len(encoding.encode(p)) for p in prompt])
                num_tokens = prompt_tokens + completion_tokens * len(prompt)
                return num_tokens
            else:
                raise TypeError(
                    'Expecting either string or list of strings for "prompt" field in completion request'
                )
    # if embeddings request, tokens = input tokens
    elif api_endpoint == "embeddings":
        input = request_json["input"]
        if isinstance(input, str):  # single input
            num_tokens = len(encoding.encode(input))
            return num_tokens
        elif isinstance(input, list):  # multiple inputs
            num_tokens = sum([len(encoding.encode(i)) for i in input])
            return num_tokens
        else:
            raise TypeError(
                'Expecting either string or list of strings for "inputs" field in embedding request'
            )
    # more logic needed to support other API calls (e.g., edits, inserts, DALL-E)
    else:
        raise NotImplementedError(
            f'API endpoint "{api_endpoint}" not implemented in this script'
        )


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
