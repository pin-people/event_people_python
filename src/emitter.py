from src.broker.rabbit import Rabbit

class Emitter:

    @staticmethod
    def trigger(events):
       Emitter(events)

    def __init__(self, events) -> None:

        with Rabbit() as r:
            r.producer(events)