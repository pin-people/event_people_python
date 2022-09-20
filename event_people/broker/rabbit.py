import pika
from event_people.broker.base import Base
from event_people.config import get_settings

from event_people.broker.queue import Queue
from event_people.event import Event
from event_people.broker.topic import Topic

class Rabbit(Base):

    def __new__(cls):
        cls.config = get_settings()
        return Base.__new__(cls)

    def __init__(self) -> None:
        self.connection = None
        self.channel = None

    def __enter__(self):
        self.connection = pika.BlockingConnection(
                pika.URLParameters(f'{self.config.EVENT_PEOPLE_RABBIT_URL}/{self.config.EVENT_PEOPLE_VHOST}'))
        self.channel = self.connection.channel()
        return self

    def consume(self, event_name, callback=None):
        q = Queue(self.channel)
        q.subscribe(binding_key=event_name)
        q.start(event_name, callback)

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
