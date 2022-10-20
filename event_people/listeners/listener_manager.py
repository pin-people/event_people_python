from event_people.config import Config

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
            broker.consume(listener.event_name, listener.listener_class.callback, final_method_name=listener.callback)


class ListenerConfiguration:
    def __init__(self, listener_class, callback, event_name):
        self.listener_class = listener_class
        self.callback = callback
        self.event_name = event_name
