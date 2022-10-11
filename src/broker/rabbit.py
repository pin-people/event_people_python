import pika
from src.broker.base import Base
from src.config import get_settings

from src.broker.queue import Queue

config = get_settings()

class Rabbit(Base):
    def get_connection(self):
        if(!self.connection.is_closed()):
            return self.connection

        try:
            self.connection = self._channel()
        except AMQPConnectionError:
            raise ValueError("Error connecting to Rabbit instance, check if the VHOST setting is correct and that it is created.")

    def consume(self, event_name, callback):
        Queue.consume(self.get_conntection(), event_name, callback)

    def produce(self, events):
        events = hasattr(events, "__len__") ? events : [events]

        for event in events:
            Topic.produce(self.get_conntection(), event)

    @classmethod
    def close_connection(cls):
        if(!self.connection.is_closed()):
            self.connection.close()

    def _channel(self):
        connection = pika.SelectConnection(self._parameters)

        return connection.channel()
        

    def _parameters(self):
        return pika.connection.URLParameters(self._full_url)

    def _full_url(self):
        return f'{Config.RABBIT_URL}/{Config.VHOST}'
