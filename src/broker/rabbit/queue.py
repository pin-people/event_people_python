import os
from functools import partial
from event import Event
from .context import Context

class Queue:
    TOPIC_NAME = os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME']
    APP_NAME = os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']

    """ Queue wrappper for python user"""
    def __init__(self, channel):
        if channel is None:
            raise ValueError("Channel must be defined.")

        channel.basic_qos(prefetch_count=1)
        self._channel = channel

    @classmethod
    def subscribe(cls, channel, event_name, continuous, callback):
        cls(channel).isubscribe(event_name, continuous, callback)

    def isubscribe(self, event_name, continuous, callback):
        queue_name = self._define_queue(event_name)
        
        on_message_callback = partial(self._callback, args=(continuous, callback))
        self._channel.basic_consume(
            queue=queue_name, on_message_callback=on_message_callback, auto_ack=False)
    
    def _define_queue(self, event_name):
        routing_key = '.'.join(event_name.split('.')[0:4])

        queue_name = self._queue_name(routing_key)
        queue = self._channel.queue_declare(
            queue_name, durable=True, exclusive=False)

        self._channel.queue_bind(
            exchange=self.TOPIC_NAME, queue=queue_name, routing_key=routing_key)

        return queue_name

    def _topic(self):
        Topic.get_topic(self._channel)

    def _callback(self, channel, delivery_info, properties, payload, args):
        continuous, callback = args
        event_name = delivery_info.routing_key

        event = Event(event_name, payload)
        context = Context(channel, delivery_info)

        callback(event, context)

        if not continuous:
            channel.stop_consuming()

    def _queue_name(self, routing_key) -> str:
        broken_event_name = routing_key.split('.')
        event_name = '.'.join(broken_event_name[0:4])

        if broken_event_name[3] != 'all':
            event_name = f"{'.'.join(broken_event_name[0:3])}.all"

        return f'{self.APP_NAME.lower()}-{event_name.lower()}'
