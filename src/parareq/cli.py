"""

Example command to call script:
```
python examples/api_request_parallel_processor.py \
  --requests_filepath examples/data/example_requests_to_parallel_process.jsonl \
  --save_filepath examples/data/example_requests_to_parallel_process_results.jsonl \
  --request_url https://api.openai.com/v1/embeddings \
  --max_requests_per_minute 1500 \
  --max_tokens_per_minute 6250000 \
  --token_encoding_name cl100k_base \
  --max_attempts 5 \
  --logging_level 20
```
"""

import argparse
import logging
import os
from parareq.parareq import APIRequestProcessor
from parareq.parareq_utils import create_requests_file


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests_filepath")
    parser.add_argument("--save_filepath", default=None)
    # we use: api.openai.com/v1/chat/completions
    parser.add_argument("--request_url", default="https://api.openai.com/v1/embeddings")
    # alternative: os.getenv("OPENAI_API_KEY") but can't remember how to set env vars
    parser.add_argument("--api_key", default="")
    # chat         3500 req/min, 90k  tokens/min
    # embedding    1500 req/min, 350k tokens/min
    parser.add_argument("--max_requests_per_minute", type=int, default=3_500 * 0.75)
    parser.add_argument("--max_tokens_per_minute", type=int, default=90_000 * 0.75)
    parser.add_argument("--token_encoding_name", default="cl100k_base")
    parser.add_argument("--max_attempts", type=int, default=5)
    parser.add_argument("--logging_level", default=logging.INFO)
    parser.add_argument("--create_requests_file", type=bool, default=False)

    args = parser.parse_args()

    if args.save_filepath is None:
        args.save_filepath = args.requests_filepath.replace(".jsonl", "_results.jsonl")

    if args.create_requests_file:
        create_requests_file()
        exit()

    requests_filepath = args.requests_filepath
    if not os.path.exists(requests_filepath):
        raise FileNotFoundError(f"Requests file {requests_filepath} not found")

    # initialize file reading
    with open(requests_filepath) as file:
        APIRequestProcessor(
            save_filepath=args.save_filepath,
            request_url=args.request_url,
            api_key=args.api_key,
            max_requests_per_minute=float(args.max_requests_per_minute),
            max_tokens_per_minute=float(args.max_tokens_per_minute),
            token_encoding_name=args.token_encoding_name,
            max_attempts=int(args.max_attempts),
            logging_level=int(args.logging_level),
        ).run(file)


if __name__ == "__main__":
    # python request_processor.py
    # parse command line arguments

    cli()
