import pytest


class TestConfig:

    def test_env_exists(self, setup):
        from event_people.config import Config
        assert Config().RABBIT_URL == 'amqp://guest:guest@localhost:5672'
        assert Config().APP_NAME == 'service_name'
        assert Config().VHOST == 'event_people'
        assert Config().TOPIC_NAME == 'event_people'

    def test_config_get_broker(self, setup):
        from event_people.config import Config
        config = Config()
        broker = config.get_broker()
        assert broker is not None

    # --- v1.2.0 ---

    def test_hardcoded_retry_defaults(self, setup):
        """Env vars RABBIT_EVENT_PEOPLE_MAX_RETRIES / RABBIT_EVENT_PEOPLE_RETRY_TTL_MS
        were removed in v1.2.0; defaults are now hardcoded."""
        from event_people.config import Config
        assert Config.MAX_ATTEMPTS == 3
        assert Config.INITIAL_DELAY == 1000
        assert Config.DELAY_STRATEGY == 'exponential'

    def test_get_retry_config_returns_initial_delay(self, setup):
        """get_retry_config() now includes initial_delay (new in v1.2.0)."""
        from event_people.config import Config
        cfg = Config.get_retry_config()
        assert 'max_attempts' in cfg
        assert 'initial_delay' in cfg
        assert 'delay_strategy' in cfg
        assert 'dlq_name' in cfg
        assert cfg['initial_delay'] == 1000
        assert cfg['max_attempts'] == 3
        assert cfg['delay_strategy'] == 'exponential'
        assert cfg['dlq_name'] == 'service_name_dlq'

    def test_configure_overrides_max_attempts(self, setup):
        from event_people.config import Config
        original = Config.MAX_ATTEMPTS
        try:
            Config.configure({'max_attempts': 5})
            assert Config.MAX_ATTEMPTS == 5
            assert Config.get_retry_config()['max_attempts'] == 5
        finally:
            Config.MAX_ATTEMPTS = original

    def test_configure_overrides_initial_delay(self, setup):
        from event_people.config import Config
        original = Config.INITIAL_DELAY
        try:
            Config.configure({'initial_delay': 2000})
            assert Config.INITIAL_DELAY == 2000
            assert Config.get_retry_config()['initial_delay'] == 2000
        finally:
            Config.INITIAL_DELAY = original

    def test_configure_overrides_delay_strategy(self, setup):
        from event_people.config import Config
        original = Config.DELAY_STRATEGY
        try:
            Config.configure({'delay_strategy': 'fixed'})
            assert Config.DELAY_STRATEGY == 'fixed'
            assert Config.get_retry_config()['delay_strategy'] == 'fixed'
        finally:
            Config.DELAY_STRATEGY = original

    def test_configure_overrides_dlq_name(self, setup):
        from event_people.config import Config
        original = Config.DLQ_NAME
        try:
            Config.configure({'dlq_name': 'custom_dlq'})
            assert Config.DLQ_NAME == 'custom_dlq'
            assert Config.get_retry_config()['dlq_name'] == 'custom_dlq'
        finally:
            Config.DLQ_NAME = original

    def test_configure_with_multiple_options(self, setup):
        from event_people.config import Config
        orig_ma = Config.MAX_ATTEMPTS
        orig_id = Config.INITIAL_DELAY
        orig_ds = Config.DELAY_STRATEGY
        orig_dlq = Config.DLQ_NAME
        try:
            Config.configure({
                'max_attempts': 7,
                'initial_delay': 500,
                'delay_strategy': 'fixed',
                'dlq_name': 'my_dlq',
            })
            cfg = Config.get_retry_config()
            assert cfg['max_attempts'] == 7
            assert cfg['initial_delay'] == 500
            assert cfg['delay_strategy'] == 'fixed'
            assert cfg['dlq_name'] == 'my_dlq'
        finally:
            Config.MAX_ATTEMPTS = orig_ma
            Config.INITIAL_DELAY = orig_id
            Config.DELAY_STRATEGY = orig_ds
            Config.DLQ_NAME = orig_dlq

    def test_configure_none_is_noop(self, setup):
        """configure(None) should not raise and should leave defaults intact."""
        from event_people.config import Config
        Config.configure(None)
        assert Config.MAX_ATTEMPTS == 3
        assert Config.INITIAL_DELAY == 1000

    def test_configure_empty_dict_is_noop(self, setup):
        """configure({}) should not change any defaults."""
        from event_people.config import Config
        Config.configure({})
        assert Config.MAX_ATTEMPTS == 3
        assert Config.INITIAL_DELAY == 1000

    def test_dlq_name_defaults_to_app_name_dlq(self, setup):
        """DLQ_NAME=None → get_retry_config returns '{appName}_dlq'."""
        from event_people.config import Config
        original = Config.DLQ_NAME
        try:
            Config.DLQ_NAME = None
            assert Config.get_retry_config()['dlq_name'] == 'service_name_dlq'
        finally:
            Config.DLQ_NAME = original
