""" API REQUEST PARALLEL PROCESSOR

Using the OpenAI API to process lots of text quickly takes some care.
If you trickle in a million API requests one by one, they'll take days to complete.
If you flood a million API requests in parallel, they'll exceed the rate limits and fail with errors.
To maximize throughput, parallel requests need to be throttled to stay under rate limits.

This script parallelizes requests to the OpenAI API while throttling to stay under rate limits.

Features:
- Streams requests from file, to avoid running out of memory for giant jobs
- Makes requests concurrently, to maximize throughput
- Throttles request and token usage, to stay under rate limits
- Retries failed requests up to {max_attempts} times, to avoid missing data
- Logs errors, to diagnose problems with requests
"""
import asyncio  # for running API calls concurrently
import json  # for saving results to a jsonl file
import logging  # for logging rate limit warnings and other messages
import os  # for reading API key

import time  # for sleeping after rate limit is hit
from pathlib import Path
from dataclasses import (  # for storing API inputs, outputs, and metadata
    dataclass,
    field,
)
import aiohttp  # for making API calls concurrently

from parareq.parareq_utils import (
    api_endpoint_from_url,
    append_to_jsonl,
    num_tokens_consumed_from_request,
    task_id_generator_function,
)

from typing import Optional  # for optional arguments

# alternative: os.getenv("OPENAI_API_KEY") but can't remember how to set env vars
# chat         3500 req/min, 90k  tokens/min
# embedding    1500 req/min, 350k tokens/min


class RateLimiter:
    def __init__(self, rate, per):
        self.rate = rate
        self.per = per
        self.allowance = rate

    def update_allowance(self, time_passed):
        self.allowance += time_passed * (self.rate / self.per)
        if self.allowance > self.rate:
            self.allowance = self.rate  # throttle

    def is_limited(self):
        return self.allowance < 1.0

    def update_usage(self):
        self.allowance -= 1.0


class TokenLimiter(RateLimiter):
    def is_limited(self):
        return super().is_limited()

    def update_usage(self):
        super().update_usage()


@dataclass
class StatusTracker:
    """Stores metadata about the script's progress. Only one instance is created."""

    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0  # script ends when this reaches 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0

    num_rate_limit_errors: int = 0
    num_api_errors: int = 0  # excluding rate limit errors, counted above
    num_other_errors: int = 0

    # used to cool off after hitting rate limits
    time_of_last_rate_limit_error: float = 0

    def task_started(self):
        self.num_tasks_started += 1
        self.num_tasks_in_progress += 1

    def task_succeeded(self):
        self.num_tasks_succeeded += 1
        self.num_tasks_in_progress -= 1

    def task_failed(self):
        self.num_tasks_failed += 1
        self.num_tasks_in_progress -= 1


@dataclass
class APIRequest:
    """Stores an API request's inputs, outputs, and other metadata. Contains a method to make an API call."""

    task_id: int
    request_json: dict
    token_consumption: int
    attempts_left: int
    metadata: dict
    result: list = field(default_factory=list)
    write_to_file: bool = True

    async def call_api(
        self,
        request_url: str,
        request_header: dict,
        retry_queue: asyncio.Queue,
        save_filepath: str,
        status_tracker: StatusTracker,
    ):
        """Calls the OpenAI API and saves results."""
        logging.info(f"Starting request #{self.task_id}")
        logging.debug(f"metadata: {self.metadata}")
        error = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=request_url, headers=request_header, json=self.request_json
                ) as response:
                    response = await response.json()
                    print(response)
            if "error" in response:
                logging.warning(
                    f"Request {self.task_id} failed with error {response['error']}"
                )

                error = response
                if "Rate limit" in response["error"].get("message", ""):
                    status_tracker.time_of_last_rate_limit_error = time.time()
                    status_tracker.num_rate_limit_errors += 1
                else:
                    status_tracker.num_api_errors += 1

        except (
            ValueError
        ) as e:  # catching naked exceptions is bad practice, but in this case we'll log & save them
            logging.warning(f"Request {self.task_id} failed with Exception {e}")
            status_tracker.num_other_errors += 1
            error = e
        # if you encounter an error which could not be processed save
        if error:
            await self._failure(error, status_tracker, save_filepath, retry_queue)
        else:
            await self._success(response, status_tracker, save_filepath)

    async def _failure(self, error, status_tracker, save_filepath, retry_queue):
        self.result.append(error)
        if self.attempts_left:
            retry_queue.put_nowait(self)
        else:
            logging.error(
                f"Request {self.request_json} failed after all attempts. Saving errors: {self.result}"
            )
            error_response = [str(e) for e in self.result]
            data = [self.request_json, error_response]
            data.append(self.metadata) if self.metadata else ""

            if self.write_to_file:
                append_to_jsonl(data, save_filepath)
            status_tracker.task_failed()

    async def _success(self, response, status_tracker, save_filepath):
        data = [self.request_json, response]
        data.append(self.metadata) if self.metadata else ""

        print(data)
        if self.write_to_file:
            append_to_jsonl(data, save_filepath)
        status_tracker.task_succeeded()
        logging.debug(f"Request {self.task_id} saved to {save_filepath}")


class APIRequestProcessor:
    """Processes API requests in parallel, throttling to stay under rate limits.

    Args:
        save_filepath (str, optional): path to the file where the results will be saved
            - file will be a jsonl file, where each line is an array with the original request plus the API response
            - e.g., [{"model": "text-embedding-ada-002", "input": "embed me"}, {...}]
            - if omitted, results will be saved to {requests_filename}_results.jsonl

        request_url (str, optional): URL of the API endpoint to call
            - if omitted, will default to "https://api.openai.com/v1/embeddings"

        api_key (str, optional): API key to use
            - if omitted, the script will attempt to read it from an environment variable {os.getenv("OPENAI_API_KEY")}

        max_requests_per_minute (float, optional): target number of requests to make per minute (will make less if limited by tokens)
            - leave headroom by setting this to 50% or 75% of your limit
            - if requests are limiting you, try batching multiple embeddings or completions into one request
            - if omitted, will default to 1,500

        max_tokens_per_minute (float, optional): target number of tokens to use per minute (will use less if limited by requests)
            - leave headroom by setting this to 50% or 75% of your limit
            - if omitted, will default to 125,000

        token_encoding_name (str, optional): name of the token encoding used, as defined in the `tiktoken` package,
            - defaults to "cl100k_base" (used by `text-embedding-ada-002`)

        max_attempts (int, optional): number of times to retry a failed request before giving up
            - if omitted, will default to 5

        logging_level (int, optional): level of logging to use; higher numbers will log fewer messages
            - 40 = ERROR; will log only when requests fail after all retries
            - 30 = WARNING; will log when requests his rate limits or other errors
            - 20 = INFO; will log when requests start and the status at finish
            - 10 = DEBUG; will log various things as the loop runs to see when they occur
            - if omitted, will default to 20 (INFO).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        save_filepath: Optional[str] = None,
        request_url: Optional[str] = "https://api.openai.com/v1/embeddings",
        max_requests_per_minute: Optional[float] = 3_500 * 0.75,
        max_tokens_per_minute: Optional[float] = 90_000 * 0.75,
        token_encoding_name: Optional[str] = "cl100k_base",
        max_attempts: Optional[int] = 5,
        logging_level: Optional[int] = 20,
    ) -> None:
        if api_key is None:
            self.api_key = os.environ["OPENAI_API_KEY"]
        else:
            self.api_key = api_key

        self.save_filepath = save_filepath

        if Path(self.save_filepath).exists():
            raise FileExistsError(
                f"Results file {self.save_filepath} already exists. Please delete it or choose a different save_filepath."
            )
        if not Path(self.save_filepath).parent.exists():
            Path(self.save_filepath).parent.mkdir(parents=True, exist_ok=True)

        self.request_url = request_url
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.logging_level = logging_level

        # constants
        self.rate_limit_pause = 15  # seconds to pause after rate limit error
        self.seconds_to_sleep_each_loop = (
            0.001  # 1 ms limits max throughput to 1,000 requests per second
        )

        # initialize logging
        logging.basicConfig(
            level=self.logging_level,
            format="%(asctime)s  - %(levelname)s - %(message)s",
        )
        logging.debug(f"Logging initialized at level {self.logging_level}")

        # infer API endpoint and construct request header
        self.api_endpoint = api_endpoint_from_url(self.request_url)
        self.request_header = {"Authorization": f"Bearer {self.api_key}"}

    def run(self, file) -> None:
        """Runs the script.

        requests_file(str): a file containing the requests to be processed
            - file should be a jsonl file, where each line is a json object with API parameters and an optional metadata field
            - e.g., {"model": "text-embedding-ada-002", "input": "embed me", "metadata": {"row_id": 1}}
            - as with all jsonl files, take care that newlines in the content are properly escaped (json.dumps does this automatically)
            - an example file is provided at examples/data/example_requests_to_parallel_process.jsonl
            - the code to generate the example file is appended to the bottom of this script

        proceeds as follows:
            - Get next request if one is not already waiting for capacity
            - Update available token & request capacity
            - If enough capacity available, call API
            - The loop pauses if a rate limit error is hit
            - The loop breaks when no tasks remain
        """
        # initialize trackers
        requests_retry_queue = asyncio.Queue()

        # generates integer IDs of 1, 2, 3, ...
        task_id_generator = task_id_generator_function()

        # single instance to track a collection of variables
        status_tracker = StatusTracker()

        # `requests` will provide requests one at a time
        requests = file.__iter__()
        logging.debug(f"File opened. Entering main loop")
        asyncio.run(
            self._process_api_requests_from_file(
                requests,
                requests_retry_queue,
                task_id_generator,
                status_tracker,
            )
        )

    async def _process_api_requests_from_file(
        self,
        requests,
        requests_retry_queue,
        task_id_generator,
        status_tracker,
    ) -> None:
        next_request = None  # variable to hold the next request to call

        # initialize available capacity counts
        available_request_capacity = self.max_requests_per_minute
        available_token_capacity = self.max_tokens_per_minute

        last_update_time = time.time()

        # initialize flags
        file_not_finished = True  # after file is empty, we'll skip reading it
        logging.debug(f"Initialization complete.")

        while True:
            # get next request (if one is not already waiting for capacity)
            if next_request is None:
                if not requests_retry_queue.empty():
                    next_request = requests_retry_queue.get_nowait()
                    logging.debug(
                        f"Retrying request {next_request.task_id}: {next_request}"
                    )
                elif file_not_finished:
                    try:
                        # get new request
                        request_json = json.loads(next(requests))
                        next_request = APIRequest(
                            task_id=next(task_id_generator),
                            request_json=request_json,
                            token_consumption=num_tokens_consumed_from_request(
                                request_json,
                                self.api_endpoint,
                                self.token_encoding_name,
                            ),
                            attempts_left=self.max_attempts,
                            metadata=request_json.pop("metadata", None),
                        )
                        status_tracker.task_started()
                        logging.debug(
                            f"Reading request {next_request.task_id}: {next_request}"
                        )
                    except StopIteration:
                        # if file runs out, set flag to stop reading it
                        logging.debug("Read file exhausted")
                        file_not_finished = False

            # update available capacity
            current_time = time.time()
            seconds_since_update = current_time - last_update_time
            available_request_capacity = min(
                available_request_capacity
                + self.max_requests_per_minute * seconds_since_update / 60.0,
                self.max_requests_per_minute,
            )
            available_token_capacity = min(
                available_token_capacity
                + self.max_tokens_per_minute * seconds_since_update / 60.0,
                self.max_tokens_per_minute,
            )
            last_update_time = current_time

            # if enough capacity available, call API
            if next_request:
                next_request_tokens = next_request.token_consumption
                if (
                    available_request_capacity >= 1
                    and available_token_capacity >= next_request_tokens
                ):
                    # update counters
                    available_request_capacity -= 1
                    available_token_capacity -= next_request_tokens
                    next_request.attempts_left -= 1

                    # call API
                    asyncio.create_task(
                        next_request.call_api(
                            request_url=self.request_url,
                            request_header=self.request_header,
                            retry_queue=requests_retry_queue,
                            save_filepath=self.save_filepath,
                            status_tracker=status_tracker,
                        )
                    )
                    next_request = None  # reset next_request to empty

            # if all tasks are finished, break
            if status_tracker.num_tasks_in_progress == 0:
                break

            # main loop sleeps briefly so concurrent tasks can run
            await asyncio.sleep(self.seconds_to_sleep_each_loop)

            await self._rate_limit_cooldown(status_tracker)

        await self._after_finishing(status_tracker)

    async def _rate_limit_cooldown(self, status_tracker: StatusTracker):
        # if a rate limit error was hit recently, pause to cool down
        seconds_since_rate_limit_error = (
            time.time() - status_tracker.time_of_last_rate_limit_error
        )
        if seconds_since_rate_limit_error < self.rate_limit_pause:
            remaining_seconds_to_pause = (
                self.rate_limit_pause - seconds_since_rate_limit_error
            )
            await asyncio.sleep(remaining_seconds_to_pause)
            # ^e.g., if pause is 15 seconds and final limit was hit 5 seconds ago
            logging.warn(
                f"Pausing to cool down until {time.ctime(status_tracker.time_of_last_rate_limit_error + self.rate_limit_pause)}"
            )

    async def _after_finishing(self, status_tracker: StatusTracker):
        # after finishing, log final status
        logging.info(
            f"""Parallel processing complete. Results saved to {self.save_filepath}"""
        )
        if status_tracker.num_tasks_failed > 0:
            logging.warning(
                f"{status_tracker.num_tasks_failed} / {status_tracker.num_tasks_started} requests failed. Errors logged to {self.save_filepath}."
            )
        if status_tracker.num_rate_limit_errors > 0:
            logging.warning(
                f"{status_tracker.num_rate_limit_errors} rate limit errors received. Consider running at a lower rate."
            )
        # rename file if tasks failed
        if status_tracker.num_tasks_failed > 0:
            os.rename(
                self.save_filepath,
                self.save_filepath.replace(".jsonl", "_with_errors.jsonl"),
            )
