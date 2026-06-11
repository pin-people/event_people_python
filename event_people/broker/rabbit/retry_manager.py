import os


class RetryManager:
    INITIAL_DELAY = int(os.environ.get('RABBIT_EVENT_PEOPLE_RETRY_TTL_MS', 1000))
    MAX_DELAY = 600_000

    def __init__(self, max_attempts, delay_strategy='exponential'):
        self.max_attempts = max_attempts
        self.delay_strategy = delay_strategy

    def should_retry(self, retry_count):
        return retry_count < self.max_attempts

    def get_next_delay(self, retry_count):
        if self.delay_strategy == 'fixed':
            return self.INITIAL_DELAY
        # exponential: initialDelay * (5 ^ retry_count)
        return min(self.INITIAL_DELAY * (5 ** retry_count), self.MAX_DELAY)
