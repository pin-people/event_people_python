import os

from event_people.broker.rabbit_broker import RabbitBroker

class Config:
    """ Class that load all enviroment variable necessary to feature works"""

    APP_NAME = os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']
    TOPIC_NAME = os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME']
    VHOST = os.environ['RABBIT_EVENT_PEOPLE_VHOST']
    RABBIT_URL = os.environ['RABBIT_URL']

    # Retry defaults — hardcoded, overridable via configure() or BaseListener class attributes.
    # Env vars RABBIT_EVENT_PEOPLE_MAX_RETRIES and RABBIT_EVENT_PEOPLE_RETRY_TTL_MS were
    # removed in spec v1.2.0.
    MAX_ATTEMPTS = 3
    INITIAL_DELAY = 1000
    DELAY_STRATEGY = 'exponential'
    DLQ_NAME = None  # Defaults to '{appName}_dlq' when not set

    broker = None

    @classmethod
    def configure(cls, options=None):
        """Set global retry defaults in code.

        Options (all optional):
          max_attempts   — maximum retry attempts (default: 3)
          initial_delay  — base delay in ms for retry backoff (default: 1000)
          delay_strategy — 'exponential' or 'fixed' (default: 'exponential')
          dlq_name       — DLQ name (default: '{appName}_dlq')

        Connection attributes (app_name, url, vhost, topic) are always read from
        environment variables and cannot be overridden here.
        """
        if options is None:
            return
        if 'max_attempts' in options:
            cls.MAX_ATTEMPTS = options['max_attempts']
        if 'initial_delay' in options:
            cls.INITIAL_DELAY = options['initial_delay']
        if 'delay_strategy' in options:
            cls.DELAY_STRATEGY = options['delay_strategy']
        if 'dlq_name' in options:
            cls.DLQ_NAME = options['dlq_name']

    @classmethod
    def get_broker(cls):
        cls.broker = cls.broker or RabbitBroker()

        return cls.broker

    @classmethod
    def get_retry_config(cls):
        """Return the active global retry configuration."""
        return {
            'max_attempts': cls.MAX_ATTEMPTS,
            'initial_delay': cls.INITIAL_DELAY,
            'delay_strategy': cls.DELAY_STRATEGY,
            'dlq_name': cls.DLQ_NAME if cls.DLQ_NAME is not None else f'{cls.APP_NAME}_dlq',
        }
