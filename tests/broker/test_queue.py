import pytest
from mock import patch, MagicMock
import pika

from pika.spec import Basic


class TestQueue:

    @staticmethod
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
        conn_path = f"{setup['basedir']}.broker.rabbit_broker.pika.BlockingConnection"
        with patch(conn_path, spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            q = Queue(channel)
            assert q

    def test_subscribe_queue_ok(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        conn_path = f"{setup['basedir']}.broker.rabbit_broker.pika.BlockingConnection"
        with patch(conn_path, spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Queue.subscribe(channel, 'resource.custom.receive.all', True,
                            TestQueue.callback)

    def test_subscribe_queue_name_less_four_parts(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        conn_path = f"{setup['basedir']}.broker.rabbit_broker.pika.BlockingConnection"
        with pytest.raises(ValueError):
            with patch(conn_path, spec=pika.BlockingConnection):
                rabbit = RabbitBroker()
                channel = rabbit.get_connection()
                Queue.subscribe(channel, 'resource.custom', False,
                                TestQueue.callback)

    def test_subscribe_with_fourth_queue_name_different_than_all(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue
        conn_path = f"{setup['basedir']}.broker.rabbit_broker.pika.BlockingConnection"
        with patch(conn_path, spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Queue.subscribe(channel, 'resource.custom.recieve.action', False,
                            TestQueue.callback)

    def test_main_queue_declared_without_dead_letter_argument(self, setup):
        """The main queue must be declared argument-free (no x-dead-letter-exchange),
        so upgrades over legacy queues never PRECONDITION_FAIL. The DLQ is a plain
        queue and there is no DLX fanout exchange or binding."""
        from event_people import Queue

        channel = MagicMock()
        q = Queue(channel)
        q._define_queue('resource.custom.pay.all', retry_params={})

        # The main queue declare must carry no x-dead-letter-exchange argument.
        main_queue = 'service_name-resource.custom.pay.all'
        declare_calls = {
            c.args[0]: c.kwargs for c in channel.queue_declare.call_args_list
        }
        assert main_queue in declare_calls
        assert 'arguments' not in declare_calls[main_queue], \
            "main queue must be declared without arguments"

        # The DLQ must be a plain durable queue (no DLX argument/binding).
        assert 'service_name_dlq' in declare_calls
        assert 'arguments' not in declare_calls['service_name_dlq']

        # No DLX fanout exchange must be declared.
        channel.exchange_declare.assert_not_called()

        # The retry queue keeps its dead-letter routing back to the main queue.
        retry_queue = f'{main_queue}_retry'
        assert retry_queue in declare_calls
        retry_args = declare_calls[retry_queue]['arguments']
        assert retry_args['x-dead-letter-exchange'] == ''
        assert retry_args['x-dead-letter-routing-key'] == main_queue

    def test_callback_subscribe_sucessffuly(self, setup):
        from event_people import RabbitBroker
        from event_people import Queue

        conn_path = f"{setup['basedir']}.broker.rabbit_broker.pika.BlockingConnection"
        with patch(conn_path, spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            queue_instance = Queue(channel)
            delivery_tag = Basic.Deliver('consumer_tag_')
            delivery_tag.routing_key = 'resource.custom.pay.all'
            body = {'amount': 350, 'name': 'George'}
            properties = pika.BasicProperties(headers={})
            queue_name = 'service_name-resource.custom.pay.all'
            retry_params = {'max_retries': 3, 'initial_delay': 1000,
                            'delay_strategy': 'exponential',
                            'dlq_name': 'service_name_dlq'}
            queue_instance._callback(
                channel=channel, delivery_info=delivery_tag,
                properties=properties, payload=body,
                args=[False, TestQueue.callback, None, queue_name, retry_params])
