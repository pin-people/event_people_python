from src.config import get_settings
from src.utils import adjust_name_event

config = get_settings()

class Queue:
    """ Queue wrappper for python user"""
    def __init__(self, channel):
        if channel is None:
            raise ValueError("Channel can't be None")

        self.channel = channel
        self.channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    def subscribe(self, *binding_key):

        for binding in binding_key:
            routing_key = adjust_name_event(binding)
            name_queue = self.queue_name(routing_key)
            self.channel.queue_declare(name_queue, exclusive=True)

            self.channel.queue_bind(
                exchange='topic_logs', queue=name_queue, routing_key=routing_key)

    def start(self, event_name):
        print(' [*] Waiting for logs. To exit press CTRL+C')
        queue_name = self.queue_name(event_name)
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()


    def callback(ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))


    def queue_name(self, routing_key) -> str:
        return f'{config.EVENT_PEOPLE_APP_NAME}-{routing_key}'

