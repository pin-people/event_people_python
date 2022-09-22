import pytest
import pika
from mock import patch
import os

class TestRabbit:

    @pytest.fixture()
    def setUp(self):
        print("setup")
        os.environ["RABBIT_URL"] = "amqp://guest:guest@localhost:5672"
        os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'EventPeopleExampleApp'
        os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
        os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'topic1'

        yield "resource"
        print("teardown")

    def test_rabbit_close_connection(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            from event_people.broker.rabbit import Rabbit

            with Rabbit() as r:
                mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
                r.close()
                assert r

    def test_rabbit_consume_queue(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            from event_people.broker.rabbit import Rabbit

            with Rabbit() as r:
                mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
                r.consume(None, 'user.users.create.all')


    def test_rabbit_consume_without_parameters(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            from event_people.broker.rabbit import Rabbit
            with Rabbit() as r:
                mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
                r.consume()


    def test_rabbit_emmit_event_sucessfully(self, setUp):
        from event_people.broker.rabbit import Rabbit

        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:

            with Rabbit() as r:
                mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
                ##todo
