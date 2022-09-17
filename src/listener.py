from email import header
from typing import Callable
import json

from src.utils import adjust_name_event
from src.broker.rabbit import Rabbit
from src.event import Event

class Listener:

    @staticmethod
    def on(event_name: str, callback: Callable= None):
        return Listener(event_name, callback)

    def __init__(self, event_name, callback: Callable = None) -> None:
        self.event_name = adjust_name_event(event_name)
        self.callback = callback if callback else self.callback_event
        self.result = None

        with Rabbit() as r:
            r.consume(self.event_name, callback=self.callback)

    def callback_event(self, ch, method, properties, body) -> Event:
        print(" [x] %r:%r" % (method.routing_key, body))
        json_message = json.loads(body)
        header = json_message['header']
        name = header['resource'] + '.' + header['origin'] +  '.'  + header['action'] + '.' + header['destiny']
        self.result = Event(appName=header['app'], name=name ,body=json_message['body'])


    def get_result(self):
        return self.result
