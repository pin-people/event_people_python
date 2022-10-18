from mock import patch
import pika

class TestListener:

    def callback(event, context):
        print(event.name)
        print(event.header)
        print(event.body)
        context.success()

    def test_listen_event_with(self, setup):
        from listener import Listener
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            Listener.on('resource.custom.receive.all', TestListener.callback)

    def test_listen_passing_callback_no_callback(self, setup):
        from listener import Listener

        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            Listener.on('resource.custom.receive.all', TestListener.callback)

    def test_listen_event_name_with_three_parts(self, setup):
        from listener import Listener

        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            Listener.on('resource.custom.receive', TestListener.callback)
