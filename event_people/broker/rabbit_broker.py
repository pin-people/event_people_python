import os
import pika
from pika.exceptions import AMQPConnectionError, StreamLostError

from event_people.broker.rabbit.queue import Queue
from event_people.broker.base import Base
from event_people.broker.rabbit.topic import Topic

class RabbitBroker(Base):
    VHOST = os.environ['RABBIT_EVENT_PEOPLE_VHOST']
    RABBIT_URL = os.environ['RABBIT_URL']

    def get_connection(self):
        try:
            if self.connection and not self.connection.is_closed:
                return self.connection.channel()

            return self._channel()
        except (AMQPConnectionError, StreamLostError) as error:
            return self._channel()

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
        self.connection = pika.BlockingConnection(self._parameters())

        return self.connection.channel()

    def _parameters(self):
        return pika.connection.URLParameters(self._full_url())

    def _full_url(self):
        return f'{self.RABBIT_URL}/{self.VHOST}'
