import os
import json

class Topic:
    """ Queue wrappper for python user"""
    TOPIC_NAME = os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME']
    EXCHANGE_TYPE = 'topic'

    def __init__(self, channel):
        if channel is None:
            raise ValueError("Channel must be defined.")

        self._channel = channel

    @classmethod
    def get_topic(cls, channel):
        cls(channel).iget_topic()

    def iget_topic(self):
        self._channel.exchange_declare(
            self.TOPIC_NAME, exchange_type=self.EXCHANGE_TYPE, passive=True, durable=True)

        return self._channel

    @classmethod
    def produce(cls, channel, event):
        cls(channel).iproduce(event)

    def iproduce(self, event):
        topic = self.iget_topic()
        body = json.dumps(event.body, indent=2).encode('utf-8')

        topic.basic_publish(exchange=self.TOPIC_NAME, routing_key=event.name, body=body)
