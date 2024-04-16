from parareq.openai_utils import (
    openai_api_endpoint_from_url,
)


def test_openai_api_endpoint_from_url():
    """Test the function that extracts the API endpoint from the request URL."""
    request_url = "https://api.openai.com/v1/embeddings"
    endpoint = openai_api_endpoint_from_url(request_url)
    assert endpoint == "embeddings"
