# parareq

[![Github-CI][github-ci]][github-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI][pypi-badge]][pypi-link]



Reliable Parallel API Request Processing with Rate Limiting. Useful for 
- doing lots of HTTP API requests while respecting rate limits.
- simple CLI jobs 
- batch processing stuff through the openai/hugging face APIs
- working in jupyter notebooks

The goal is really to have quick and simple task queue and not have to setup celery/redis/rabbitmq/zeromq/whatever

Honestly, I don't recommend using this right now but please check back soon. 

This is a basically a packaged version of the [code from the OpenAI Cookbook here](https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py).

## Installation

The package is published on PyPI and can be installed by running:


```bash
pip install parareq
```

or to install the dev version

``` bash
git clone https://github.com/urbanophile/parareq
cd parareq 
pip install -e . 
```

## OpenAI usage

Now run
```
OPENAI_API_KEY="abcdzyz1234"
parareq     \ 
         --requests_filepath examples/input/salt_survey_example.jsonl \
         --save_filepath output/response_salt_survey_example.jsonl \
         --request_url https://api.openai.com/v1/chat/completions
```

## TODO 
- github actions 
    - [X] run test suite against python 3.9-3.12
    - [ ] run test suite against ubuntu 22.04, ubuntu 20.04,
    - [ ] run against latest_macos 
- testing  
    - [ ] write tests for token bucket implementation (NEXT)
    - [ ] write longer functional test for openai api (NEXT)
    - [ ] write test for custom api (NEXT)
        - [ ] fix flask dummy api 
    - [ ] 100% coverage for parareq.parareq (NEXT)
- features:
    - [ ] publish 0.1.1 to pypi (NEXT)
    - [ ] allow custom actions on api call completion
        - [ ] write example workflow for "generating knowledge prompting" (2-step)
        - [ ] write example workflow for "prompt chaining" (2-step)
        - [ ] write example workflow for self-consistency (n-step)
        - [ ] write example workflow for summarisation (n-step)
    - [ ] custom api 
    - [ ] some sort of better persistence 
- refactor and troubleshooting
    - [ ] debug huggingface api calls (NEXT)
    - [ ] allow api calls to be somethign other than post requests
    - [ ] move rate limiting logic into rate_limiter
- docs
    - [ ] decide on plan 
    - [ ] medium article howto

- release 0.1.2:
    - functional tests for openai
    - 100% coverage for parareq.parareq
    - ubuntu testing 

- release 0.2:
    - hugging face integration
    - custom api integration
    - run tests against macos 

- release 0.3: 
    - multistep workflows


## License

`parareq` was created by Matt Gibson. It is licensed under the terms of the MIT license.


[github-ci]: https://github.com/urbanophile/parareq/actions/workflows/ci.yml/badge.svg?branch=main
[github-link]: https://github.com/urbanophile/parareq
[pypi-badge]: https://img.shields.io/pypi/v/parareq.svg
[pypi-link]: https://pypi.org/project/parareq/
[rtd-badge]: https://readthedocs.org/projects/parareq/badge/?version=latest
[rtd-link]: https://parareq.readthedocs.io/en/latest/?badge=latest