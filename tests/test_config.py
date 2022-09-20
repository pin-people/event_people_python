"""_This test config module from lib_
"""


from event_people.config import Settings
import pytest
from mock import patch
import pytest

def test_env_exists(config):
    with patch('event_people.config.config',config) as c:
        s = Settings()
        assert config('RABBIT_URL') == s.EVENT_PEOPLE_RABBIT_URL
        assert config('RABBIT_EVENT_PEOPLE_APP_NAME') == s.EVENT_PEOPLE_APP_NAME
        assert config('RABBIT_EVENT_PEOPLE_VHOST') == s.EVENT_PEOPLE_VHOST
        assert config('RABBIT_EVENT_PEOPLE_TOPIC_NAME') == s.EVENT_PEOPLE_TOPIC_NAME

def test_env_not_exists(config):
    with pytest.raises(AttributeError):
        with patch('event_people.config.config',config) as c:
            s = Settings()
            assert s.EVENT_URL
