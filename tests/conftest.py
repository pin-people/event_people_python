import pytest
from mock import patch
from decouple import Config, RepositoryEnv
from io import StringIO
import os
import pika
from event_people.config import Settings

ENVFILE = '''

RABBIT_URL = amqp://guest:guest@localhost:5672
RABBIT_EVENT_PEOPLE_APP_NAME = service_name
RABBIT_EVENT_PEOPLE_VHOST = event_people
RABBIT_EVENT_PEOPLE_TOPIC_NAME = event_people


'''


@pytest.fixture(scope='module')
def config():
    with patch('decouple.open', return_value=StringIO(ENVFILE), create=True):
        return Config(RepositoryEnv('.env'))

@pytest.fixture(scope='module')
def settings(config):
    with patch('event_people.config.config',config) as c:
        s = Settings()
        return s

@pytest.fixture(scope='module')
def mock_connection():
    os.environ["RABBIT_URL"] = "amqp://guest:guest@localhost:5672"
    os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'EventPeopleExampleApp'
    os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
    os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'topic1'

    with patch('event_people.broker.rabbit.pika.BlockingConnection', spec=pika.BlockingConnection) as mocked_connection:
        mocked_connection.return_value.channel.return_value.basic_publish.return_value = False
        mocked_connection.return_value.channel.return_value.exchange_declare.return_value = True
        return mock_connection
