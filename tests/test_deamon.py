from mock import patch
import pika

class TestDeamon:

    def test_start_deamon(self, setup):
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            from event_people import Daemon
            Daemon.start()

