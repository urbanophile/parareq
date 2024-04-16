"""Contains utils for calling the openai api

    - Define functions
        - api_endpoint_from_url (extracts API endpoint from request URL)
"""

import re  # for matching endpoint from request URL
import json
import tiktoken
from pathlib import Path


def openai_api_endpoint_from_url(request_url: str) -> str:
    """Extract the API endpoint from the request URL."""

    # ^https://    -> Starts with "https://"
    # [^/]+/       -> root string followed by a forward slash "api.openai.com/"
    # v\\d+/       -> Matches "v[some_number]/"
    # (.+)$        -> Captures the rest of the string

    match = re.search("^https://[^/]+/v\\d+/(.+)$", request_url)
    if match is not None and len(match.groups()) > 0:
        print("match groups: ", match.groups())
        return match[1]
    else:

        raise ValueError(
            f"No matches found, URL doesn't match structure: {request_url}"
        )


def count_embedding_tokens(
    encoding: tiktoken.Encoding, request_json: dict, api_endpoint: str
) -> int:
    """embeddings request: tokens = input tokens"""
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


def count_completion_tokens(
    encoding: tiktoken.Encoding, request_json: dict, api_endpoint: str
) -> int:
    """completions request: tokens = prompt + n * max_tokens"""
    max_tokens = request_json.get("max_tokens", 15)
    n = request_json.get("n", 1)
    completion_tokens = n * max_tokens

    # chat completions
    if api_endpoint.startswith("chat/"):
        num_tokens = 0
        for message in request_json["messages"]:
            num_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
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


def openai_num_tokens_consumed_from_request(
    request_json: dict,
    api_endpoint: str,
    token_encoding_name: str,
) -> int:
    """Count the number of tokens in the request. Only supports completion and embedding requests."""
    encoding = tiktoken.get_encoding(token_encoding_name)
    if api_endpoint.endswith("completions"):
        return count_completion_tokens(
            request_json=request_json, encoding=encoding, api_endpoint=api_endpoint
        )
    elif api_endpoint == "embeddings":
        return count_embedding_tokens(
            request_json=request_json, encoding=encoding, api_endpoint=api_endpoint
        )
    # more logic needed to support other API calls (e.g., edits, inserts, DALL-E)
    else:
        raise NotImplementedError(
            f'API endpoint "{api_endpoint}" not implemented in this script'
        )
