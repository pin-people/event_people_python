class Queue:
    """ Queue wrappper for python user"""
    def __init__(self, channel):
        if channel is None:
            raise ValueError("Channel must be defined.")

        channel.basic_qos(prefetch_count=1)
        self._channel = channel

    def subscribe(self, event_name, callback):
        self._define_queue(event_name)
        
        on_message_callback = functools.partial(self.callback, args=(callback))
        self._channel.basic_consume(
            queue=queue_name, on_message_callback, auto_ack=False)
    
    def _define_queue(self, event_name):
        routing_key = '.'.join(event_name.split('.')[0:3])
        queue_name = self.queue_name(routing_key)
        queue = self._channel.queue_declare(
            queue_name, durable=True, exclusive=False, callback: self.callback)

        self._channel.queue_bind(
            exchange=Config.TOPIC_NAME, queue=queue_name, routing_key=routing_key)

    def _topic(self)
        Topic.get_topic(self._channel)

    def _callback(channel, method, delivery_info, payload, callback):
        event_name = method.routing_key

        event = Event(event_name, payload)
        context = Context(channel, delivery_info)

        callback(event, context)

    def _queue_name(self, routing_key) -> str:
        return f'{config.APP_NAME.lower()}-{routing_key.lower()}'

