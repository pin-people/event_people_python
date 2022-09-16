from mock import patch
import pika
import pytest
from src.config import Settings


@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_queue_name_with_parameter(mocked_connection, config):

    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
        with patch('src.broker.queue.get_settings', s):
            from src.broker.queue import Queue
            q = Queue(mocked_connection.channel)

            assert q.queue_name('test_name') == f'{s.EVENT_PEOPLE_APP_NAME}-test_name'

@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_queue_with_many_binding_keys_subscribe(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
        with patch('src.broker.queue.get_settings', s):
            from src.broker.queue import Queue
            q = Queue(mocked_connection.channel)
            q.subscribe('resource.origin.action')

@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_queue_with_no_binding_keys_subscribe(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with pytest.raises(TypeError):

        with patch('src.config.config',config) as c:
            s = Settings()
            with patch('src.broker.queue.get_settings', s):
                from src.broker.queue import Queue
                q = Queue(mocked_connection.channel)
                q.subscribe()


@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_queue_with_start_consume(mocked_connection, config):
    mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
    mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True

    with patch('src.config.config',config) as c:
        s = Settings()
        with patch('src.broker.queue.get_settings', s):
            from src.broker.queue import Queue
            q = Queue(mocked_connection.channel)
            q.subscribe('resource.origin.action')
            q.start('resource.origin.action', None)
