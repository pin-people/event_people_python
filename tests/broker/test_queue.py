import pytest
from mock import patch
import pika

from pika.spec import Basic


class TestQueue:

    def callback(event, context, final_method):
        print(event.name)
        print(event.header)
        print(event.body)
        print(final_method)
        context.success()


    def test_create_queue_without_channel(self, setup):
        from event_people import Queue
        with pytest.raises(ValueError):
            q = Queue(None)
            assert q

    def test_create_queue_with_channel_ok(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            q = Queue(channel)
            assert q


    def test_subscribe_queue_ok(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Queue.subscribe(channel, 'resource.custom.receive.all', True, TestQueue.callback)


    def test_subscribe_queue_name_less_four_parts(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        with pytest.raises(ValueError):
            with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
                rabbit = RabbitBroker()
                channel = rabbit.get_connection()
                Queue.subscribe(channel, 'resource.custom', False, TestQueue.callback)

    def test_subscribe_with_fourth_queue_name_different_than_all(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Queue.subscribe(channel, 'resource.custom.recieve.action', False, TestQueue.callback)

    def test_callback_subscribe_sucessffuly(self, setup):
        from event_people import RabbitBroker
        from event_people import Context
        from event_people import Queue

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            delivery_tag = Basic.Deliver('consumer_tag_')
            delivery_tag.routing_key = 'resource.custom.pay'
            body = { 'amount': 350, 'name': 'George' }
            context = Context(channel, delivery_tag)
            Queue._callback(None, channel=channel, delivery_info= delivery_tag, properties=context, payload=body, args=[False, TestQueue.callback, 'callback'])
