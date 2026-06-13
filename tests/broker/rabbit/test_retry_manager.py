"""Tests for RetryManager — spec v1.2.0: initial_delay is a constructor param
(no longer sourced from RABBIT_EVENT_PEOPLE_RETRY_TTL_MS env var)."""

import pytest


class TestRetryManager:

    def test_should_retry_when_under_max(self, setup):
        from event_people.broker.rabbit.retry_manager import RetryManager
        rm = RetryManager(max_attempts=3, delay_strategy='exponential', initial_delay=1000)
        assert rm.should_retry(0) is True
        assert rm.should_retry(1) is True
        assert rm.should_retry(2) is True

    def test_should_not_retry_when_at_max(self, setup):
        from event_people.broker.rabbit.retry_manager import RetryManager
        rm = RetryManager(max_attempts=3, delay_strategy='exponential', initial_delay=1000)
        assert rm.should_retry(3) is False
        assert rm.should_retry(4) is False

    def test_exponential_delay_uses_initial_delay(self, setup):
        """Exponential: initialDelay * (5 ^ retry_count)."""
        from event_people.broker.rabbit.retry_manager import RetryManager
        rm = RetryManager(max_attempts=3, delay_strategy='exponential', initial_delay=1000)
        assert rm.get_next_delay(0) == 1000      # 1000 * 5^0 = 1000
        assert rm.get_next_delay(1) == 5000      # 1000 * 5^1 = 5000
        assert rm.get_next_delay(2) == 25000     # 1000 * 5^2 = 25000

    def test_exponential_delay_custom_initial(self, setup):
        from event_people.broker.rabbit.retry_manager import RetryManager
        rm = RetryManager(max_attempts=3, delay_strategy='exponential', initial_delay=500)
        assert rm.get_next_delay(0) == 500       # 500 * 5^0
        assert rm.get_next_delay(1) == 2500      # 500 * 5^1

    def test_exponential_delay_capped_at_max_delay(self, setup):
        from event_people.broker.rabbit.retry_manager import RetryManager
        rm = RetryManager(max_attempts=3, delay_strategy='exponential', initial_delay=1000)
        # 1000 * 5^10 >> 600_000 — should be capped
        assert rm.get_next_delay(10) == 600_000

    def test_fixed_delay_constant(self, setup):
        """Fixed strategy returns initial_delay regardless of retry count."""
        from event_people.broker.rabbit.retry_manager import RetryManager
        rm = RetryManager(max_attempts=3, delay_strategy='fixed', initial_delay=2000)
        assert rm.get_next_delay(0) == 2000
        assert rm.get_next_delay(1) == 2000
        assert rm.get_next_delay(5) == 2000

    def test_fixed_delay_default_initial(self, setup):
        from event_people.broker.rabbit.retry_manager import RetryManager
        rm = RetryManager(max_attempts=3, delay_strategy='fixed')
        assert rm.get_next_delay(0) == 1000

    def test_no_env_var_dependency(self, setup, monkeypatch):
        """RetryManager must NOT read RABBIT_EVENT_PEOPLE_RETRY_TTL_MS — removed in v1.2.0."""
        import os
        monkeypatch.delenv('RABBIT_EVENT_PEOPLE_RETRY_TTL_MS', raising=False)
        from event_people.broker.rabbit.retry_manager import RetryManager
        rm = RetryManager(max_attempts=3, delay_strategy='exponential', initial_delay=3000)
        # Should use the constructor arg, not any env var
        assert rm.get_next_delay(0) == 3000
