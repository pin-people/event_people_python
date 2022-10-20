import os
import pika
from pika.exceptions import AMQPConnectionError

from event_people.broker.rabbit.queue import Queue
from event_people.broker.base import Base
from event_people.broker.rabbit.topic import Topic

class RabbitBroker(Base):
    VHOST = os.environ['RABBIT_EVENT_PEOPLE_VHOST']
    RABBIT_URL = os.environ['RABBIT_URL']

    def get_connection(self):
        if self.connection and not self.connection.is_closed:
            return self.connection

        try:
            self.connection = self._channel()

            return self.connection
        except AMQPConnectionError:
            raise ValueError("Error connecting to Rabbit instance, check if the VHOST setting is correct and that it is created.")

    def consume(self, event_name, callback, final_method_name=None, continuous=True):
        Queue.subscribe(self.get_connection(), event_name, continuous, callback, final_method_name)

    def produce(self, events):
        events = events if hasattr(events, "__len__") else [events]

        for event in events:
            if hasattr(event, "__len__"):
                for item in event:
                    Topic.produce(self.get_connection(), item)
            else:
                Topic.produce(self.get_connection(), event)


    def _channel(self):
        connection = pika.BlockingConnection(self._parameters())

        return connection.channel()

    def _parameters(self):
        return pika.connection.URLParameters(self._full_url())

    def _full_url(self):
        return f'{self.RABBIT_URL}/{self.VHOST}'
