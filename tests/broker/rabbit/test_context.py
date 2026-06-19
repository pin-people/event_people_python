import mock
from pika.spec import Basic
import pika


class TestContext:

    @mock.patch('pika.BlockingConnection')
    def test_context_sucess_message(self, connection, setup):
        from event_people import Context
        delivery_tag = Basic.Deliver('consumer_tag_')
        context = Context(connection, delivery_tag)
        context.success()

    @mock.patch('pika.BlockingConnection')
    def test_context_reject_message(self, connection, setup):
        from event_people.broker.rabbit.context import Context
        delivery_tag = Basic.Deliver('consumer_tag_')
        context = Context(connection, delivery_tag)
        context.reject()

    @mock.patch('pika.BlockingConnection')
    def test_context_fail_message(self, connection, setup):
        from event_people.broker.rabbit.context import Context
        delivery_tag = Basic.Deliver('consumer_tag_')
        context = Context(connection, delivery_tag)
        context.fail()

    # --- v1.2.0 ---

    @mock.patch('pika.BlockingConnection')
    def test_context_accepts_initial_delay(self, connection, setup):
        """RabbitContext must accept initial_delay param (v1.2.0)."""
        from event_people.broker.rabbit.context import RabbitContext
        delivery_tag = Basic.Deliver('consumer_tag_')
        ctx = RabbitContext(connection, delivery_tag, initial_delay=2000)
        assert ctx.initial_delay == 2000

    @mock.patch('pika.BlockingConnection')
    def test_context_default_initial_delay(self, connection, setup):
        """RabbitContext default initial_delay is 1000 ms."""
        from event_people.broker.rabbit.context import RabbitContext
        delivery_tag = Basic.Deliver('consumer_tag_')
        ctx = RabbitContext(connection, delivery_tag)
        assert ctx.initial_delay == 1000

    def test_is_last_retry_true_when_at_max(self, setup):
        """is_last_retry == True when retry_count >= max_retries - 1."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        delivery_tag = Basic.Deliver('consumer_tag_')
        ctx = RabbitContext(channel, delivery_tag, max_retries=3, retry_count=2)
        assert ctx.is_last_retry is True

    def test_is_last_retry_false_when_under_max(self, setup):
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        delivery_tag = Basic.Deliver('consumer_tag_')
        ctx = RabbitContext(channel, delivery_tag, max_retries=3, retry_count=0)
        assert ctx.is_last_retry is False

    def test_fail_publishes_with_initial_delay_expiration(self, setup):
        """fail() should publish with expiration = initial_delay * (5^retry_count)."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        delivery_tag = Basic.Deliver('consumer_tag_')
        delivery_tag.delivery_tag = 1

        ctx = RabbitContext(
            channel, delivery_tag,
            queue_name='test_queue',
            max_retries=3,
            initial_delay=2000,
            delay_strategy='exponential',
            retry_count=0,
            body=b'{}',
        )
        ctx.fail()

        # Should publish to retry queue with expiration = 2000 * 5^0 = 2000
        channel.basic_publish.assert_called_once()
        _, kwargs = channel.basic_publish.call_args
        assert kwargs['properties'].expiration == '2000'

    def test_fail_fixed_delay_uses_initial_delay(self, setup):
        """fail() with fixed strategy should use initial_delay as the constant delay."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        delivery_tag = Basic.Deliver('consumer_tag_')
        delivery_tag.delivery_tag = 1

        ctx = RabbitContext(
            channel, delivery_tag,
            queue_name='test_queue',
            max_retries=3,
            initial_delay=500,
            delay_strategy='fixed',
            retry_count=0,
            body=b'{}',
        )
        ctx.fail()

        channel.basic_publish.assert_called_once()
        _, kwargs = channel.basic_publish.call_args
        assert kwargs['properties'].expiration == '500'

    def test_fail_exhausted_retries_no_dlq_nacks_without_requeue(self, setup):
        """fail() exhausted with no DLQ configured must nack(requeue=False)."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        delivery_tag = Basic.Deliver('consumer_tag_')
        delivery_tag.delivery_tag = 99

        ctx = RabbitContext(
            channel, delivery_tag,
            max_retries=3,
            retry_count=3,  # exhausted
            body=b'{}',
        )
        # dlq_name defaults to None → no app-level DLQ target
        ctx.fail()

        channel.basic_nack.assert_called_once_with(99, requeue=False)
        channel.basic_publish.assert_not_called()

    def test_fail_exhausted_retries_publishes_to_dlq_and_acks(self, setup):
        """fail() exhausted with a DLQ configured publishes to the DLQ then acks."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        delivery_tag = Basic.Deliver('consumer_tag_')
        delivery_tag.delivery_tag = 7

        ctx = RabbitContext(
            channel, delivery_tag,
            max_retries=3,
            retry_count=3,  # exhausted
            body=b'{"x":1}',
        )
        ctx.dlq_name = 'service_name_dlq'
        ctx.fail()

        channel.basic_publish.assert_called_once()
        _, kwargs = channel.basic_publish.call_args
        assert kwargs['exchange'] == ''
        assert kwargs['routing_key'] == 'service_name_dlq'
        assert kwargs['body'] == b'{"x":1}'
        channel.basic_ack.assert_called_once_with(7)
        channel.basic_nack.assert_not_called()

    def test_reject_publishes_to_dlq_and_acks(self, setup):
        """reject() publishes the message to the app-level DLQ then acks."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        delivery_tag = Basic.Deliver('consumer_tag_')
        delivery_tag.delivery_tag = 11

        ctx = RabbitContext(channel, delivery_tag, retry_count=0, body=b'{}')
        ctx.dlq_name = 'service_name_dlq'
        ctx.reject()

        channel.basic_publish.assert_called_once()
        _, kwargs = channel.basic_publish.call_args
        assert kwargs['exchange'] == ''
        assert kwargs['routing_key'] == 'service_name_dlq'
        channel.basic_ack.assert_called_once_with(11)
        channel.basic_nack.assert_not_called()

    def test_reject_no_dlq_nacks_without_requeue(self, setup):
        """reject() with no DLQ configured falls back to nack(requeue=False)."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        delivery_tag = Basic.Deliver('consumer_tag_')
        delivery_tag.delivery_tag = 5

        ctx = RabbitContext(channel, delivery_tag, body=b'{}')
        ctx.reject()

        channel.basic_nack.assert_called_once_with(5, requeue=False)
        channel.basic_publish.assert_not_called()

    def test_reject_dlq_publish_failure_nacks_without_requeue(self, setup):
        """reject() with a DLQ but a failing publish must nack(requeue=False)."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        channel.basic_publish.side_effect = Exception("broker down")
        delivery_tag = Basic.Deliver('consumer_tag_')
        delivery_tag.delivery_tag = 8

        ctx = RabbitContext(channel, delivery_tag, body=b'{}')
        ctx.dlq_name = 'service_name_dlq'
        ctx.reject()

        channel.basic_nack.assert_called_once_with(8, requeue=False)

    def test_fail_publish_error_nacks_without_requeue(self, setup):
        """When publish fails, must nack(requeue=False) — not requeue=True (SOPHIA-1G)."""
        from event_people.broker.rabbit.context import RabbitContext
        channel = mock.MagicMock()
        channel.basic_publish.side_effect = Exception("broker down")
        delivery_tag = Basic.Deliver('consumer_tag_')
        delivery_tag.delivery_tag = 42

        ctx = RabbitContext(
            channel, delivery_tag,
            queue_name='test_queue',
            max_retries=3,
            retry_count=0,
            body=b'{}',
        )
        ctx.fail()

        channel.basic_nack.assert_called_once_with(42, requeue=False)
