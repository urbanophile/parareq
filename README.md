# parareq

[![Github-CI][github-ci]][github-link]
<!-- [![Coverage Status][codecov-badge]][codecov-link] -->
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI][pypi-badge]][pypi-link]


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

[github-ci]: https://github.com/urbanophile/parareq/workflows/ci/badge.svg?branch=master
[github-link]: https://github.com/urbanophile/parareq
<!-- [codecov-badge]: https://codecov.io/gh/executablebooks/MyST-NB/branch/master/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/MyST-NB -->
[pypi-badge]: https://img.shields.io/pypi/v/parareq.svg
[pypi-link]: https://pypi.org/project/parareq/
[rtd-badge]: https://readthedocs.org/projects/parareq/badge/?version=latest
[rtd-link]: https://parareq.readthedocs.io/en/latest/?badge=latest