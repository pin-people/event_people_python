class RetryManager:
    MAX_DELAY = 600_000

    def __init__(self, max_attempts, delay_strategy='exponential', initial_delay=1000):
        self.max_attempts = max_attempts
        self.delay_strategy = delay_strategy
        self.initial_delay = initial_delay

    def should_retry(self, retry_count):
        return retry_count < self.max_attempts

    def get_next_delay(self, retry_count):
        if self.delay_strategy == 'fixed':
            return self.initial_delay
        # exponential: initialDelay * (5 ^ retry_count), capped at maxDelay
        return min(self.initial_delay * (5 ** retry_count), self.MAX_DELAY)
