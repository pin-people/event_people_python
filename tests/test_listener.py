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

            Listener.on(lambda x: x**2, 'resource.origin.action')


    def test_listener_with_no_event_name(self, setUp):
        from event_people.listener import Listener

        Listener.on(lambda x: print(x))


    def test_listener_with_wrong_pattern_event_name(self, setUp):
        with pytest.raises(ValueError):
                from event_people.listener import Listener

                Listener.on(lambda x: print(x), "wrong.test")


    def test_listener_with_event_parts_name_with_all(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.listener import Listener

            l = Listener.on(None, 'payment.payments.pay')


    def test_listener_with_callback_none(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True
            from event_people.listener import Listener
            l = Listener.on(None, 'payment.payments.pay.all')

    def test_listener_callback_not_none(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.listener import Listener

            l = Listener.on(lambda x: print(x), 'payment.payments.pay.all' )
            assert l.callback is not None
            assert l.callback.__name__ == '<lambda>'

    def test_listener_with_more_than_one_queue(self, setUp):
            with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
                mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
                mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

                from event_people.listener import Listener

                l = Listener.on(lambda x: print(x), 'payment.payments.pay.all', 'resource.origin.action.all' )
