import pika
from event_people.broker.rabbit.retry_manager import RetryManager


class RabbitContext:
    """ Queue wrapper for python user"""
    def __init__(self, channel, delivery_info, properties=None, queue_name=None,
                 max_retries=3, delay_strategy='exponential', initial_delay=1000,
                 retry_count=0, body=None):
        self.channel = channel
        self.delivery_info = delivery_info
        self.properties = properties
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.delay_strategy = delay_strategy
        self.initial_delay = initial_delay
        self.retry_count = retry_count
        self._retry_manager = RetryManager(max_retries, delay_strategy, initial_delay)
        self.dlq_name = None
        self._body = body if body is not None else b''

    @property
    def is_last_retry(self):
        return self.retry_count >= self.max_retries - 1

    def success(self):
        self.channel.basic_ack(self.delivery_info.delivery_tag)

    def fail(self):
        if self._retry_manager.should_retry(self.retry_count):
            delay = self._retry_manager.get_next_delay(self.retry_count)
            retry_queue_name = f'{self.queue_name}_retry'
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=retry_queue_name,
                    body=self._get_body(),
                    properties=pika.BasicProperties(
                        expiration=str(delay),
                        headers={'x-event-people-retries': int(self.retry_count + 1)},
                        delivery_mode=2,
                    ),
                )
                try:
                    self.channel.basic_ack(self.delivery_info.delivery_tag)
                except Exception:
                    # Publish already succeeded; swallow ack errors to avoid masking
                    # the successful retry enqueue. The original message may be
                    # redelivered once more but that is safer than losing the retry.
                    pass
            except Exception:
                self.channel.basic_nack(self.delivery_info.delivery_tag, requeue=False)
        else:
            self.channel.basic_nack(self.delivery_info.delivery_tag, requeue=False)

    def reject(self):
        self.channel.basic_nack(self.delivery_info.delivery_tag, requeue=False)

    def _get_body(self):
        return self._body


# Backward-compatibility alias
Context = RabbitContext
