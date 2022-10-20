import pika
import pytest
from mock import patch


class TestTopic:

    def test_get_topic_with_channel(self, setup):
        from event_people import RabbitBroker
        from event_people import Topic

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Topic.get_topic(channel=channel)

    def test_get_topic_whithout_channel(self, setup):
        from event_people import Topic

        with pytest.raises(ValueError):
            Topic.get_topic(channel=None)

    def test_produce_topic_with_channel(self, setup):
        from event_people import RabbitBroker
        from event_people import Event
        from event_people import Topic

        body = { 'amount': 350, 'name': 'George' }
        event = Event(name='resource.custom.pay', body=body)
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Topic.produce(channel=channel, event=event)

    def test_produce_topic_without_channel(self, setup):
        from event_people import Event
        from event_people import Topic
        with pytest.raises(ValueError):
            body = { 'amount': 350, 'name': 'George' }
            event = Event(name='resource.custom.pay', body=body)
            Topic.produce(channel=None, event=event)
