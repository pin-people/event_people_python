from config import Config
from broker.rabbit.topic import Topic

class Emitter:
    @classmethod
    def trigger(cls, *events):
        cls().itrigger(events)
    
    def itrigger(self, events):
        broker = Config.get_broker()
        channel = broker.get_connection()

        for event in events:
            broker.produce(events)

        try:
            channel.start_consuming()
        finally:
            channel.stop_consuming()

        return events
