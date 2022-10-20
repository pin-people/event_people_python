import pytest
import os

BASE_DIR: str = 'event_people'

@pytest.fixture(scope='function')
def setup():
    os.environ['RABBIT_URL'] = 'amqp://guest:guest@localhost:5672'
    os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'service_name'
    os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
    os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'event_people'

    yield {'basedir': BASE_DIR}

    os.unsetenv('RABBIT_URL')
    os.unsetenv('RABBIT_EVENT_PEOPLE_APP_NAME')
    os.unsetenv('RABBIT_EVENT_PEOPLE_VHOST')
    os.unsetenv('RABBIT_EVENT_PEOPLE_TOPIC_NAME')

@pytest.fixture(scope='function')
def load_listener_test(setup):
    from event_people import BaseListener

    class TestListener(BaseListener):

        def __init__(self, context):
            self.context = context

        def pay(self, event):
            print(f"Paid {event.body['amount']} for {event.body['name']} ~> {event.name}")


        def receive(self, event):
            if event.body['amount'] > 500:
                print(f"Received {event.body['amount']} from {event.body['name']} ~> {event.name}")
            else:
                print('[consumer] Got SKIPPED message')

    return TestListener, setup

