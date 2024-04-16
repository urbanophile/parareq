from parareq.rate_limiter import RateLimiter


def test_ratelimiter_init():
    """test the basic rate limiter initialization."""
    limiter = RateLimiter(limit=100, period=10)
    assert limiter.current_capacity == 100.0
