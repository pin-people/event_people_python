from mock import patch
import pika

class TestDeamon:

    def test_start_deamon(self):
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            from daemon import Daemon
            Daemon.start()

