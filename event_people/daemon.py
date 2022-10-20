from event_people.config import Config
from event_people.listeners.listener_manager import ListenerManager

class Daemon:
    @classmethod
    def start(cls):
        channel = Config.get_broker().get_connection()

        ListenerManager.bind_all_listeners()

        try:
            channel.start_consuming()
        except KeyboardInterrupt: #pragma: no cover
            channel.stop_consuming()##pragma: no cover
