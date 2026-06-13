import pytest
from mock import patch
import pika

from pika.spec import Basic


class TestQueue:

    def callback(event, context, final_method):
        print(event.name)
        print(event.header)
        print(event.body)
        print(final_method)
        context.success()


    def test_create_queue_without_channel(self, setup):
        from event_people import Queue
        with pytest.raises(ValueError):
            q = Queue(None)
            assert q

    def test_create_queue_with_channel_ok(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            q = Queue(channel)
            assert q


    def test_subscribe_queue_ok(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Queue.subscribe(channel, 'resource.custom.receive.all', True, TestQueue.callback)


    def test_subscribe_queue_name_less_four_parts(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        with pytest.raises(ValueError):
            with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
                rabbit = RabbitBroker()
                channel = rabbit.get_connection()
                Queue.subscribe(channel, 'resource.custom', False, TestQueue.callback)

    def test_subscribe_with_fourth_queue_name_different_than_all(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Queue.subscribe(channel, 'resource.custom.recieve.action', False, TestQueue.callback)

    def test_callback_subscribe_sucessffuly(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        import pika as _pika

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            queue_instance = Queue(channel)
            delivery_tag = Basic.Deliver('consumer_tag_')
            delivery_tag.routing_key = 'resource.custom.pay.all'
            body = { 'amount': 350, 'name': 'George' }
            properties = _pika.BasicProperties(headers={})
            queue_name = 'service_name-resource.custom.pay.all'
            retry_params = {'max_retries': 3, 'initial_delay': 1000, 'delay_strategy': 'exponential',
                            'dlq_name': 'service_name_dlq'}
            queue_instance._callback(channel=channel, delivery_info=delivery_tag,
                                     properties=properties, payload=body,
                                     args=[False, TestQueue.callback, None, queue_name, retry_params])
