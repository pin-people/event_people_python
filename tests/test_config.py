"""_This test config module from lib_
"""


from src.config import Settings
import pytest
from mock import patch
import pytest
from decouple import Config, RepositoryEnv
from io import StringIO



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

def test_env_exists(config):
    with patch('src.config.config',config) as c:
        s = Settings()
        assert config('RABBIT_URL') == s.EVENT_PEOPLE_RABBIT_URL
        assert config('RABBIT_EVENT_PEOPLE_APP_NAME') == s.EVENT_PEOPLE_APP_NAME
        assert config('RABBIT_EVENT_PEOPLE_VHOST') == s.EVENT_PEOPLE_VHOST
        assert config('RABBIT_EVENT_PEOPLE_TOPIC_NAME') == s.EVENT_PEOPLE_TOPIC_NAME

def test_env_not_exists(config):
    with pytest.raises(AttributeError):
        with patch('src.config.config',config) as c:
            s = Settings()
            assert s.EVENT_URL
