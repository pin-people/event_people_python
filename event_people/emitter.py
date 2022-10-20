from event_people.config import Config

class Emitter:
    @classmethod
    def trigger(cls, *events):
        cls().itrigger(events)

    def itrigger(self, events):
        broker = Config.get_broker()
        channel = broker.get_connection()

        broker.produce(events)

        try:
            channel.start_consuming()
        finally:
            channel.stop_consuming()

        return events
