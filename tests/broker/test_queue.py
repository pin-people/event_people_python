from mock import patch
import pika
import pytest
from event_people.config import Settings
import os

class TestQueue:

    @pytest.fixture()
    def setUp(self):
        print("setup")
        os.environ["RABBIT_URL"] = "amqp://guest:guest@localhost:5672"
        os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'EventPeopleExampleApp'
        os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
        os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'topic1'

        yield "resource"
        print("teardown")


    def test_queue_name_with_parameter(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            app_name = os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']
            from event_people.broker.queue import Queue
            q = Queue(mocked_connection.channel)

            assert q.queue_name('test_name') == f'{app_name}-test_name'

    def test_queue_with_many_binding_keys_subscribe(self, setUp):

        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.broker.queue import Queue
            q = Queue(mocked_connection.channel)
            q.subscribe('resource.origin.action')

    def test_queue_with_no_binding_keys_subscribe(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            with pytest.raises(TypeError):
                from event_people.broker.queue import Queue
                q = Queue(mocked_connection.channel)
                q.subscribe()


    def test_queue_with_start_consume(self, setUp):

        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.broker.queue import Queue
            q = Queue(mocked_connection.channel)
            q.subscribe('resource.origin.action')
            q.start('resource.origin.action', None)
