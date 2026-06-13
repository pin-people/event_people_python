import inspect
import os
from functools import partial
from event_people.event import Event
from .context import RabbitContext


class Queue:
    TOPIC_NAME = os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME']
    APP_NAME = os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']

    """ Queue wrapper for python user"""
    def __init__(self, channel):
        if channel is None:
            raise ValueError("Channel must be defined.")

        channel.basic_qos(prefetch_count=1)
        self._channel = channel

    @classmethod
    def subscribe(cls, channel, event_name, continuous, callback,
                  final_method_name=None, retry_params=None):
        cls(channel).isubscribe(event_name, continuous, callback,
                                final_method_name, retry_params)

    def isubscribe(self, event_name, continuous, callback,
                   final_method_name=None, retry_params=None):
        retry_params = retry_params or {}
        queue_name = self._define_queue(event_name, retry_params)

        on_message_callback = partial(
            self._callback,
            args=(continuous, callback, final_method_name, queue_name, retry_params),
        )
        self._channel.basic_consume(
            queue=queue_name, on_message_callback=on_message_callback, auto_ack=False)

    def _define_queue(self, event_name, retry_params=None):
        retry_params = retry_params or {}
        routing_key = '.'.join(event_name.split('.')[0:4])
        queue_name = self._queue_name(routing_key)

        app_name = self.APP_NAME.lower()
        dlx_name = f'{app_name}_dlx'
        dlq_name = retry_params.get('dlq_name', f'{app_name}_dlq')

        # Declare the main queue with dead-letter-exchange pointing to DLX
        self._channel.queue_declare(
            queue_name,
            durable=True,
            exclusive=False,
            arguments={'x-dead-letter-exchange': dlx_name},
        )

        self._channel.queue_bind(
            exchange=self.TOPIC_NAME, queue=queue_name, routing_key=routing_key)

        # Declare DLX exchange (fanout, durable) — idempotent
        self._channel.exchange_declare(
            exchange=dlx_name,
            exchange_type='fanout',
            durable=True,
        )

        # Declare DLQ and bind to DLX — idempotent
        self._channel.queue_declare(dlq_name, durable=True, exclusive=False)
        self._channel.queue_bind(exchange=dlx_name, queue=dlq_name, routing_key='')

        # Declare retry queue — messages expire back to the main queue via DLX
        retry_queue_name = f'{queue_name}_retry'
        self._channel.queue_declare(
            retry_queue_name,
            durable=True,
            exclusive=False,
            arguments={
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': queue_name,
            },
        )

        return queue_name

    def _callback(self, channel, delivery_info, properties, payload, args):
        continuous, callback, final_method_name, queue_name, retry_params = args
        event_name = delivery_info.routing_key

        # Read retry count from AMQP header — pika may deliver the value as int,
        # float, or str depending on the AMQP type tag used by the publisher.
        retry_count = 0
        if properties and properties.headers:
            raw = properties.headers.get('x-event-people-retries', 0)
            try:
                retry_count = max(0, int(float(raw)))
            except (TypeError, ValueError):
                retry_count = 0

        event = Event(event_name, payload, retry_count=retry_count)

        max_retries = retry_params.get('max_retries', 3)
        delay_strategy = retry_params.get('delay_strategy', 'exponential')
        initial_delay = retry_params.get('initial_delay', 1000)

        context = RabbitContext(
            channel=channel,
            delivery_info=delivery_info,
            properties=properties,
            queue_name=queue_name,
            max_retries=max_retries,
            delay_strategy=delay_strategy,
            initial_delay=initial_delay,
            retry_count=retry_count,
            body=payload,
        )
        context.dlq_name = retry_params.get('dlq_name', f'{self.APP_NAME.lower()}_dlq')

        if final_method_name is not None:
            # Dispatch via BaseListener.callback(function, event, context) — v1.2.0
            callback(final_method_name, event, context)
        else:
            try:
                param_count = len(inspect.signature(callback).parameters)
            except (ValueError, TypeError):
                param_count = 2

            if param_count >= 3:
                callback(event, context, final_method_name)
            else:
                callback(event, context)

        if not continuous:
            channel.stop_consuming()

    def _queue_name(self, routing_key) -> str:
        broken_event_name = routing_key.split('.')
        if len(broken_event_name) < 3:
            raise ValueError("queue name must follow the pattern, resource.origin.action or resource.origin.action.destination")

        event_name = '.'.join(broken_event_name[0:4])

        if broken_event_name[3] != 'all':
            event_name = f"{'.'.join(broken_event_name[0:3])}.all"

        return f'{self.APP_NAME.lower()}-{event_name.lower()}'
