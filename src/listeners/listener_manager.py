from config import Config
from broker.rabbit.topic import Topic

class ListenerManager:
    _listeners = []

    @classmethod
    def add_listener(cls, listener_class, callback, event_name):
        configuration = ListenerConfiguration(listener_class, callback, event_name)
        cls._listeners.append(configuration)

    @classmethod
    def bind_all_listeners(cls):
        broker = Config.get_broker()

        for listener in cls._listeners:
            broker.consume(listener.event_name, cls.callback)

    @classmethod
    def callback(cls, event, context):
        listener = next(lst for lst in cls._listeners if lst.event_name == event.name)

        instance = listener.listener_class(context)
        method = getattr(instance, listener.callback)

        method(event)


class ListenerConfiguration:
    def __init__(self, listener_class, callback, event_name):
        self.listener_class = listener_class
        self.callback = callback
        self.event_name = event_name
