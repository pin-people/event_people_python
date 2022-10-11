from typing import Callable
from src.utils import adjust_name_event

class Listener:

    @staticmethod
    def on(event_name, callback = None):
        broker_callback = callback if callback else Listener.basic_callback
        Config.get_broker().consume(event_name, callback)

  
    @staticmethod
    def printing_callback(self, ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))
