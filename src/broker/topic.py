from src.event import Event
from src.config import Settings

config = Settings()

class Topic:

    def __init__(self, channel) -> None:
        if channel is None:
            raise ValueError("Channel can't be None")

        self.channel = channel
        self.channel.exchange_declare(exchange=config.EVENT_PEOPLE_TOPIC_NAME, exchange_type='topic')

    def produce(self, events):

        if isinstance(events, list):
            for event in events:
                self.channel.basic_publish(
                    exchange='topic_logs', routing_key=event.name, body=event.payload())

                print(" [x] Sent %r:%r" % (event.name, event.payload()))
        elif isinstance(events, Event):
                self.channel.basic_publish(
                    exchange='topic_logs', routing_key=events.name, body=events.payload())

                print(" [x] Sent %r:%r" % (events.name, events.payload()))