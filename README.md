# parareq

[![Github-CI][github-ci]][github-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI][pypi-badge]][pypi-link]


Reliable Parallel OpenAI API Request Processing with Rate Limiting. 

Honestly, I don't recommend using this right now but please check back soon. 

This is a basically a packaged version of the [code from the OpenAI Cookbook here](https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py).

## Installation

To just use the library do

```bash
pip install parareq
```

or to install the dev version

``` bash
git clone https://github.com/urbanophile/parareq
cd parareq 
pip install -e . 
```

## Usage

``` python
from parareq import APIRequestProcessor
processor = APIRequestProcessor(api_key="xyz")
processor.run("request.cfg")
```

You can also use parareq as a pure cli tool.

e.g. huggingface 
``` bash
parareq  --requests_filepath examples/input/huggingface_example.jsonl \
         --save_filepath examples/data/huggingface_example_response.jsonl \
         --which_api huggingface \
         --request_url https://api-inference.huggingface.co/models/bert-base-uncased
```
or openai

```
python examples/api_request_parallel_processor.py \
  --requests_filepath examples/data/example_requests_to_parallel_process.jsonl \
  --save_filepath examples/data/example_requests_to_parallel_process_results.jsonl \
  --request_url https://api.openai.com/v1/embeddings \
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`parareq` was created by Matt Gibson. It is licensed under the terms of the MIT license.

## Credits

`parareq` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).

[github-ci]: https://github.com/urbanophile/parareq/workflows/ci/badge.svg?branch=master
[github-link]: https://github.com/urbanophile/parareq
[pypi-badge]: https://img.shields.io/pypi/v/parareq.svg
[pypi-link]: https://pypi.org/project/parareq/
[rtd-badge]: https://readthedocs.org/projects/parareq/badge/?version=latest
[rtd-link]: https://parareq.readthedocs.io/en/latest/?badge=latest