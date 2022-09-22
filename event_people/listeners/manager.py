from event_people.listener import Listener

class Manager:

    def __init__(self) -> None:
        self.listeners = []

    def bind_all_listeners(self):
        for config in self.listeners:
           l =  Listener.on(config)

    def register_listener_configuration(self, configuration):
        self.listeners.append(configuration)