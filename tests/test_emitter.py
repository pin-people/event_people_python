from multiprocessing import Event
from unittest import mock
from mock import patch
import pika

from event_people.config import Settings
from event_people.event import Event

@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_emitter_with_one_event(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
        with patch('src.broker.queue.get_settings', s):
            from event_people.emitter import Emitter
            body = {'text': 'meu chefe é legal!'}
            e = Event(body=body, name='resource.origin.action')
            Emitter.trigger(e)


@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_emitter_with_multiple_event(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
        with patch('src.broker.queue.get_settings', s):
            from event_people.emitter import Emitter
            events = []

            body1 = {'text': 'meu chefe é legal!'}
            e1 = Event(body=body1, name='resource.origin.action')
            events.append(e1)

            body2 = {'text': 'meu chefe é muito legal'}
            e2 = Event(body=body2, name='resource1.origin.action')
            events.append(e2)

            Emitter.trigger(events)
