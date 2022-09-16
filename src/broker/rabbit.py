import pika
from src.broker.base import Base
from src.config import get_settings

from src.broker.queue import Queue

config = get_settings()

class Rabbit(Base):

    def __init__(self) -> None:
        self.connection = None
        self.channel = None

    def __enter__(self):
        self.connection = pika.BlockingConnection(
                pika.URLParameters(config.EVENT_PEOPLE_RABBIT_URL))
        self.channel = self.connection.channel()
        return self

    def consume(self, event_name):
        q = Queue(self.channel)
        q.subscribe(event_name)
        q.start(event_name)

    def producer(self):
        ...

    def close(self):
        self.channel.close()
        self.connection.close()
        
    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        if exception_value is not None:
            print(exception_value)
