from typing import Callable
import json
import functools
import asyncio

from event_people.utils import adjust_name_event
from event_people.broker.rabbit import Rabbit
from event_people.event import Event

class Listener:

    @staticmethod
    def on(callback: Callable, *event_name):
        return Listener(callback,*event_name)

    def __init__(self,callback: Callable = None, *event_name) -> None:
        self.callback = callback if callback else self.callback_event

        with Rabbit() as r:
            r.consume(self.callback,*event_name)

    def callback_event(self, ch, method, properties, body) -> Event:
        print(" [x] %r:%r" % (method.routing_key, body))
        json_message = json.loads(body)
        header = json_message['header']
        name = header['resource'] + '.' + header['origin'] +  '.'  + header['action'] + '.' + header['destiny']
        self.result = Event(appName=header['app'], name=name ,body=json_message['body'])
        ch.basic_ack(delivery_tag= method.delivery_tag)
        return self.result
