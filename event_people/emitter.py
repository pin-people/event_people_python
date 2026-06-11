from event_people.config import Config

class Emitter:
    @classmethod
    def trigger(cls, *events):
        cls().itrigger(events)

    def itrigger(self, events):
        broker = Config.get_broker()
        broker.get_connection()

        broker.produce(events)

        return events
