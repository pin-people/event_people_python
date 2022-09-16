import pytest
from mock import patch
from typing import Any, List
import pika
from src.config import Settings

class MockCallback:
    @staticmethod
    def routing_key():
        return "routing_key"

@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_listener_with_event_name(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
        with patch('src.broker.queue.get_settings', s):
            from src.listener import Listener

            Listener.on('resource.origin.action')


def test_listener_with_no_event_name():
    with pytest.raises(ValueError):
        from src.listener import Listener

        Listener.on(None, lambda x: print(x))


def test_listener_with_wrong_pattern_event_name():
   with pytest.raises(ValueError):
        from src.listener import Listener

        Listener.on("wrong.test", lambda x: print(x))


@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_listener_with_event_parts_name_with_all(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
    with patch('src.broker.queue.get_settings', s):
        from src.listener import Listener

        l = Listener.on('payment.payments.pay')
        assert l.event_name == 'payment.payments.pay.all'


@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_listener_with_callback_none(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
    with patch('src.broker.queue.get_settings', s):
        from src.listener import Listener

        l = Listener.on(event_name='payment.payments.pay.all', callback=None)
        assert l.callback is not None
        assert l.callback.__name__ == 'printing_callback'

@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_listener_callback_not_none(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
    with patch('src.broker.queue.get_settings', s):
        from src.listener import Listener

        l = Listener.on(event_name='payment.payments.pay.all', callback=lambda x: print(x))
        assert l.callback is not None
        assert l.callback.__name__ == '<lambda>'
