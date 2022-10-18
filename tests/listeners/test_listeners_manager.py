from typing import List
from mock import patch
import pytest
import pika
from pika.spec import Basic
import sys
import os

os.environ['RABBIT_URL'] = 'amqp://guest:guest@localhost:5672'
os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'service_name'
os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'event_people'
sys.path.insert(0, 'src')

from listeners.base_listener import BaseListener


class TestListener(BaseListener):

    def __init__(self, context):
        self.context = context

    def pay(self, event):
        print(f"Paid {event.body['amount']} for {event.body['name']} ~> {event.name}")


    def receive(self, event):
        if event.body['amount'] > 500:
            print(f"Received {event.body['amount']} from {event.body['name']} ~> {event.name}")
        else:
            print('[consumer] Got SKIPPED message')



class TestListenerManager:

    def test_add_with_one_listener(self, setup):
        from listeners.listener_manager import ListenerManager
        ListenerManager.add_listener(listener_class=TestListener, callback=None, event_name='resource.custom.pay')
        assert len(ListenerManager._listeners) == 1


    def test_add_listener_with_more(self, setup):
        from listeners.listener_manager import ListenerManager
        ListenerManager._listeners.clear()
        ListenerManager.add_listener(listener_class=TestListener, callback=None, event_name='resource.custom.pay')
        ListenerManager.add_listener(listener_class=TestListener, callback=None, event_name='resource.custom.service.all')
        assert len(ListenerManager._listeners) == 2

    def test_bind_all_listeners(self, setup):
        from listeners.listener_manager import ListenerManager
        ListenerManager._listeners.clear()
        ListenerManager.add_listener(listener_class=TestListener, callback=None, event_name='resource.custom.pay.service')
        ListenerManager.add_listener(listener_class=TestListener, callback=None, event_name='resource.custom.service.all')
        assert len(ListenerManager._listeners) == 2

        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            ListenerManager.bind_all_listeners()

    def test_listener_callback_ok(self, setup):
        from listeners.listener_manager import ListenerManager
        from broker.rabbit.context import Context
        from event import Event
        ListenerManager._listeners.clear()
        ListenerManager.add_listener(listener_class=TestListener, callback='pay', event_name='resource.custom.pay')
        ListenerManager.add_listener(listener_class=TestListener, callback='receive', event_name='resource.custom.service.all')

        delivery_tag = Basic.Deliver('consumer_tag_')
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            context = Context(mocked_connection, delivery_tag)
            body  = { 'amount': 350, 'name': 'George' }
            e = Event(name='resource.custom.service.all', body=body)
            ListenerManager.callback(e, context)

    def test_listener_callback_without_event_correct(self, setup):
        from listeners.listener_manager import ListenerManager
        from broker.rabbit.context import Context
        from event import Event
        ListenerManager._listeners.clear()
        ListenerManager.add_listener(listener_class=TestListener, callback='pay', event_name='resource.custom.pay')
        ListenerManager.add_listener(listener_class=TestListener, callback='receive', event_name='resource.custom.service.all')

        delivery_tag = Basic.Deliver('consumer_tag_')
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            context = Context(mocked_connection, delivery_tag)
            body  = { 'amount': 350, 'name': 'George' }
            e = Event(name='bla.bla.bla', body=body)
            with pytest.raises(StopIteration):
                ListenerManager.callback(e, context)
