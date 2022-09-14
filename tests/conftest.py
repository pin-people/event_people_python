import pytest
from mock import patch
import pytest
from decouple import Config, RepositoryEnv
from io import StringIO

from src.config import Settings

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
    with patch('src.config.config',config) as c:
        s = Settings()
        return s
