import os
from broker.rabbit_broker import RabbitBroker

class Config():
    """ Class that load all enviroment variable necessary to feature works"""

    APP_NAME = os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']
    TOPIC_NAME = os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME']
    VHOST = os.environ['RABBIT_EVENT_PEOPLE_VHOST']
    RABBIT_URL = os.environ['RABBIT_URL']
    broker = None

    @classmethod
    def get_broker(cls):
        cls.broker = cls.broker or RabbitBroker()
        
        return cls.broker

    @classmethod
    def close_connection(cls):
        RabbitBroker.close_connection()
