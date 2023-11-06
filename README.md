# parareq

Reliable Parallel OpenAI API Request Processing with Rate Limiting. This is a basically a packaged version of the [code from the OpenAI Cookbook here](https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py).

## Installation

```bash
$ pip install parareq
```

## Usage

``` python
from parareq.parareq import APIRequestProcessor
APIRequestProcessor().run(...)
```

``` bash
$ parareq  ...
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`parareq` was created by Matt Gibson. It is licensed under the terms of the MIT license.

## Credits

`parareq` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
