import pytest
from mock import patch
import pika
import os

from pika.spec import Basic
import sys

os.environ['RABBIT_URL'] = 'amqp://guest:guest@localhost:5672'
os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'service_name'
os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'event_people'
sys.path.insert(0, 'src')

from broker.rabbit.queue import Queue
from broker.rabbit_broker import RabbitBroker
from broker.rabbit.context import Context

class TestQueue:

    def callback(event, context):
        print(event.name)
        print(event.header)
        print(event.body)
        context.success()


    def test_create_queue_without_channel(self):
        with pytest.raises(ValueError):
            q = Queue(None)

    def test_create_queue_with_channel_ok(self):
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            q = Queue(channel)
            assert q

    def test_queue_without_connection_sucessfully_created(self):
        os.environ['RABBIT_URL'] = 'amqp://guest:guest@localhost:7787'
        with pytest.raises(ValueError):
            rabbit = RabbitBroker()
            rabbit.get_connection()

    def test_subscribe_queue_ok(self):
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Queue.subscribe(channel, 'resource.custom.receive.all', True, TestQueue.callback)


    def test_subscribe_queue_name_less_four_parts(self):
        with pytest.raises(ValueError):
            with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
                rabbit = RabbitBroker()
                channel = rabbit.get_connection()
                Queue.subscribe(channel, 'resource.custom', False, TestQueue.callback)

    def test_subscribe_with_fourth_queue_name_different_than_all(self):
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Queue.subscribe(channel, 'resource.custom.recieve.action', False, TestQueue.callback)

    def test_callback_subscribe_sucessffuly(self, setup):
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            delivery_tag = Basic.Deliver('consumer_tag_')
            delivery_tag.routing_key = 'resource.custom.pay'
            body = { 'amount': 350, 'name': 'George' }
            context = Context(channel, delivery_tag)
            Queue._callback(None, channel=channel, delivery_info= delivery_tag, properties=context, payload=body, args=[False, TestQueue.callback])
