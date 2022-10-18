import pytest
import os
import sys

@pytest.fixture(scope='function')
def setup():
    os.environ['RABBIT_URL'] = 'amqp://guest:guest@localhost:5672'
    os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'service_name'
    os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
    os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'event_people'
    sys.path.insert(0, 'src')
    yield

    os.unsetenv('RABBIT_URL')
    os.unsetenv('RABBIT_EVENT_PEOPLE_APP_NAME')
    os.unsetenv('RABBIT_EVENT_PEOPLE_VHOST')
    os.unsetenv('RABBIT_EVENT_PEOPLE_TOPIC_NAME')
