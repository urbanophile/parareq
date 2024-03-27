# read version from installed package
from importlib.metadata import version
from parareq.parareq import APIRequestProcessor

__version__ = version("parareq")

from parareq import parareq

__all__ = ["parareq", "APIRequestProcessor"]
