import pika
import pytest
import os

from multiprocessing import Event
from mock import patch

from event_people.config import Settings
from event_people.event import Event

class TestEmmitter:

    @pytest.fixture()
    def setUp(self):
        print("setup")
        os.environ["RABBIT_URL"] = "amqp://guest:guest@localhost:5672"
        os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'EventPeopleExampleApp'
        os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
        os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'topic1'

        yield "resource"
        print("teardown")


    def test_emitter_with_one_event(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.emitter import Emitter
            body = {'text': 'meu chefe é legal!'}
            e = Event(body=body, name='resource.origin.action')
            Emitter.trigger(e)


    def test_emitter_with_multiple_event(self, setUp):
        with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:

            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

            from event_people.emitter import Emitter
            events = []

            body1 = {'text': 'meu chefe é legal!'}
            e1 = Event(body=body1, name='resource.origin.action')
            events.append(e1)

            body2 = {'text': 'meu chefe é muito legal'}
            e2 = Event(body=body2, name='resource1.origin.action')
            events.append(e2)

            Emitter.trigger(events)
