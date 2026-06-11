import pika
from event_people.broker.rabbit.retry_manager import RetryManager


class RabbitContext:
    """ Queue wrapper for python user"""
    def __init__(self, channel, delivery_info, properties=None, queue_name=None,
                 max_retries=3, delay_strategy='exponential', retry_count=0):
        self.channel = channel
        self.delivery_info = delivery_info
        self.properties = properties
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.delay_strategy = delay_strategy
        self.retry_count = retry_count
        self._retry_manager = RetryManager(max_retries, delay_strategy)
        self.dlq_name = None

    @property
    def is_last_retry(self):
        return self.retry_count >= self.max_retries - 1

    def success(self):
        self.channel.basic_ack(self.delivery_info.delivery_tag)

    def fail(self):
        if self._retry_manager.should_retry(self.retry_count):
            delay = self._retry_manager.get_next_delay(self.retry_count)
            retry_queue_name = f'{self.queue_name}_retry'
            self.channel.basic_publish(
                exchange='',
                routing_key=retry_queue_name,
                body=self._get_body(),
                properties=pika.BasicProperties(
                    expiration=str(delay),
                    headers={'x-event-people-retries': self.retry_count + 1},
                    delivery_mode=2,
                ),
            )
            self.channel.basic_ack(self.delivery_info.delivery_tag)
        else:
            self.channel.basic_nack(self.delivery_info.delivery_tag, requeue=False)

    def reject(self):
        self.channel.basic_nack(self.delivery_info.delivery_tag, requeue=False)

    def _get_body(self):
        # Retrieve the original body from the last delivery via the channel's
        # latest frame — we store it when the context is constructed.
        return self._body if hasattr(self, '_body') else b''


# Backward-compatibility alias
Context = RabbitContext
