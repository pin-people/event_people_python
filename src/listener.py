from typing import Callable
from src.utils import adjust_name_event
from src.broker.rabbit import Rabbit

class Listener:

    @staticmethod
    def on(event_name: str, callback: Callable= None):
        return Listener(event_name, callback)

    def __init__(self, event_name, callback: Callable = None) -> None:
        self.event_name = adjust_name_event(event_name)
        self.callback = callback if callback else self.printing_callback

        with Rabbit() as r:
            r.consume(self.event_name, callback=self.callback)

    def printing_callback(self, ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))
