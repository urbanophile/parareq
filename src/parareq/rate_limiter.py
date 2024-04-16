"""Beginning of refactor of rate limiter to be more generic and reusable."""

import time


class RateLimiter:
    """Implements a token bucket for handling rate limits

    Args:
            limit (int): Maximum rate allowed of over the time period
            period (int): The time in seconds over which the rate limit applies
    """

    def __init__(self, limit: float, period: float):

        self.limit = limit
        self.period = period

        self.current_capacity = limit
        self._last_update_time = time.time()

    def start_timer(self):
        self.start_time = time.time()

    def update_allowance(self):
        update_time = time.time()
        time_passed = update_time - self._last_update_time
        self.current_capacity += time_passed * (self.limit / self.period)
        if self.current_capacity > self.limit:
            self.current_capacity = self.limit  # throttle

    def has_limited(self, attempted_usage) -> bool:
        return self.current_capacity > attempted_usage

    def update_usage(self, usage):
        self.current_capacity -= usage
