import pytest
import pika
from src.broker.rabbit import Rabbit
from mock import patch

@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_rabbit_close_connection(mocked_connection):

    with Rabbit() as r:
        mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
        r.close()
        assert r

@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_rabbit_consume_queue(mocked_connection):

    with Rabbit() as r:
        mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
        r.consume('user.users.create.all')


@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_rabbit_consume_without_parameters(mocked_connection):
    with pytest.raises(TypeError):
        with Rabbit() as r:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            r.consume()

@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_rabbit_consume_many_events(mocked_connection):
    with pytest.raises(TypeError):
        with Rabbit() as r:
            mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
            r.consume('user.users.create.all', 'resource.custom.private.service')


@patch('src.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection)
def test_rabbit_emmit_event_sucessfully(mocked_connection):
    with Rabbit() as r:
        mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
        ##todo
