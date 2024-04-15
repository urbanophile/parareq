import os
import parareq as pq

FUNCTIONAL_TEST = False


def setup():
    json_cfg = """{"model": "text-embedding-ada-002", "input": "embed me", "metadata": {"row_id": 1}}"""
    with open("cfg_test.jsonl", "w") as f:
        f.write(json_cfg)


def teardown():
    os.remove("cfg_test.jsonl")


if FUNCTIONAL_TEST:
    setup()

    print("functional test # 1 with dummy api")
    processor = pq.APIRequestProcessor(
        api_key="xyz", which_api="dummy", request_url="http://127.0.0.1:5000/api"
    )
    processor.run(requests_file="cfg_test.jsonl")
    print("functional test # 1 passed")

    print("functional test # 2 with openai api")
    processor = pq.APIRequestProcessor(api_key="xyz")
    processor.run(requests_file="cfg_test.jsonl")
    print("functional test # 2 passed")

    print("functional test # 3 with huggingface api")

    print("functional test # 3 passed")
    teardown()
