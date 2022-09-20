import pytest
import os

from mock import patch
import pika
from event_people.config import Settings

class MockCallback:
    @staticmethod
    def routing_key():
        return "routing_key"

class TestListener:

    @pytest.fixture()
    def setUp(self):
        print("setup")
        os.environ["RABBIT_URL"] = "amqp://guest:guest@localhost:5672"
        os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'EventPeopleExampleApp'
        os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
        os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'topic1'

        yield "resource"
        print("teardown")


    def test_listener_with_event_name(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:

            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.listener import Listener

            Listener.on('resource.origin.action')


    def test_listener_with_no_event_name(self, setUp):
        with pytest.raises(ValueError):
            from event_people.listener import Listener

            Listener.on(None, lambda x: print(x))


    def test_listener_with_wrong_pattern_event_name(self, setUp):
        with pytest.raises(ValueError):
                from event_people.listener import Listener

                Listener.on("wrong.test", lambda x: print(x))


    def test_listener_with_event_parts_name_with_all(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.listener import Listener

            l = Listener.on('payment.payments.pay')
            assert l.event_name == 'payment.payments.pay.all'


    def test_listener_with_callback_none(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True
            from event_people.listener import Listener
            l = Listener.on(event_name='payment.payments.pay.all', callback=None)
            assert l.callback is not None
            assert l.callback.__name__ == 'callback_event'

    def test_listener_callback_not_none(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.listener import Listener

            l = Listener.on(event_name='payment.payments.pay.all', callback=lambda x: print(x))
            assert l.callback is not None
            assert l.callback.__name__ == '<lambda>'
