import os

from event_people.broker.rabbit_broker import RabbitBroker

class Config:
    """ Class that load all enviroment variable necessary to feature works"""

    APP_NAME = os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']
    TOPIC_NAME = os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME']
    VHOST = os.environ['RABBIT_EVENT_PEOPLE_VHOST']
    RABBIT_URL = os.environ['RABBIT_URL']
    MAX_ATTEMPTS = int(os.environ.get('RABBIT_EVENT_PEOPLE_MAX_RETRIES', 3))
    DELAY_STRATEGY = os.environ.get('RABBIT_EVENT_PEOPLE_DELAY_STRATEGY', 'exponential')
    DLQ_NAME = f"{os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']}_dlq"
    broker = None

    @classmethod
    def get_broker(cls):
        cls.broker = cls.broker or RabbitBroker()

        return cls.broker

    @classmethod
    def get_retry_config(cls):
        return {
            'max_attempts': cls.MAX_ATTEMPTS,
            'delay_strategy': cls.DELAY_STRATEGY,
            'dlq_name': cls.DLQ_NAME,
        }
