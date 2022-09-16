from mock import patch
from src.config import Settings

def test_queue_name_with_parameter(config):
    with patch('src.config.config',config) as c:
        s = Settings()
        with patch('src.broker.queue.get_settings', s):
            from src.broker.queue import Queue
            q = Queue()

            assert q.queue_name('test_name') == f'{s.EVENT_PEOPLE_APP_NAME}-test_name'


def test_queue_subscribe(settings):
    ...