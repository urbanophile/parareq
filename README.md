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

## OpenAI Usage

We default to using openai, you need to setup your API key

### Setup API Key

You have three options to set up your environment variable for the OpenAI API key:

- One option is to export the environment variable every time you open the terminal. You can add the export command to your .bashrc file to avoid this.
    - `export OPENAI_API_KEY=[add your api key here]`
- Another option is to 
    1. create a copy of the `.env.template` file and name it `.env`. 
    2. Then, you can add your OpenAI API key in the `.env` file.
- finally, you can provide as a cli argument e.g. `parareq --api_key "XYZABCEFG"`

### Run OpenAI calls

Having set your API key in an accessible place, now just run:
```
parareq     \ 
         --requests_filepath examples/input/salt_survey_example.jsonl \
         --save_filepath output/response_salt_survey_example.jsonl \
         --request_url https://api.openai.com/v1/chat/completions
```



## HuggingFace usage
You need to set the enviromental variable 
To use huggingface is then just do: 

``` bash
parareq  --requests_filepath examples/input/huggingface_example.jsonl \
         --save_filepath examples/data/huggingface_example_response.jsonl \
         --which_api huggingface \
         --request_url https://api-inference.huggingface.co/models/bert-base-uncased
```



## API usage 

This not particularly stable tbh, but you can get start as follow below:
``` python
from parareq import APIRequestProcessor
processor = APIRequestProcessor(api_key="xyz")
processor.run("request.cfg")
```


## 


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`parareq` was created by Matt Gibson. It is licensed under the terms of the MIT license.

## Credits

`parareq` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).

[github-ci]: https://github.com/urbanophile/parareq/workflows/ci/badge.svg?branch=main
[github-link]: https://github.com/urbanophile/parareq
[pypi-badge]: https://img.shields.io/pypi/v/parareq.svg
[pypi-link]: https://pypi.org/project/parareq/
[rtd-badge]: https://readthedocs.org/projects/parareq/badge/?version=latest
[rtd-link]: https://parareq.readthedocs.io/en/latest/?badge=latest