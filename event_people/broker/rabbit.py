import pika
import functools
import asyncio
from event_people.broker.base import Base
from event_people.config import get_settings

from event_people.broker.queue import Queue
from event_people.event import Event
from event_people.broker.topic import Topic
import asyncio

config = get_settings

class Rabbit(Base):

    def __init__(self) -> None:
        self.connection = None
        self.channel = None

    def __enter__(self):
        self.connection = pika.BlockingConnection(
                pika.URLParameters(f'{config().EVENT_PEOPLE_RABBIT_URL}/{config().EVENT_PEOPLE_VHOST}'))
        self.channel = self.connection.channel()
        return self

    def consume(self,callback=None, *event_name):
        q = Queue(self.channel)
        q.subscribe(*event_name)
        q.start(callback, *event_name)
        print(' [*] Waiting for logs. To exit press CTRL+C')
        self.channel.start_consuming()

    def producer(self, events):
        t = Topic(self.channel)
        t.produce(events)

    def close(self):
        self.channel.close()
        self.connection.close()

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        if exception_value is not None:
            print(exception_value)
