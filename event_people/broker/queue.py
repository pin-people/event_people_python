from event_people.config import get_settings
from event_people.utils import adjust_name_event
from pika.exchange_type import ExchangeType
config = get_settings

class Queue:

    """ Queue wrappper for python user"""
    def __init__(self, channel):
        if channel is None:
            raise ValueError("Channel can't be None")

        self.channel = channel
        self.channel.exchange_declare(exchange=config().EVENT_PEOPLE_TOPIC_NAME, exchange_type=ExchangeType.topic)

    def subscribe(self, *binding_keys):
        for binding_key in binding_keys:
            routing_key = adjust_name_event(binding_key)
            name_queue = self.queue_name(routing_key)
            self.channel.queue_declare(name_queue, exclusive=True)

            self.channel.queue_bind(
                    exchange=config().EVENT_PEOPLE_TOPIC_NAME, queue=name_queue, routing_key=routing_key)

    def start(self,callback,*events_name):
        for event_name in events_name:
            routing_key = adjust_name_event(event_name)
            queue_name = self.queue_name(routing_key)
            self.channel.basic_consume(
                queue=queue_name, on_message_callback=callback)


    def queue_name(self, routing_key) -> str:
        return f'{config().EVENT_PEOPLE_APP_NAME}-{routing_key}'

