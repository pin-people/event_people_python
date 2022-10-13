from config import Config
from listeners.listener_manager import ListenerManager

class Daemon:
    @classmethod
    def start(cls):
        channel = Config.get_broker().get_connection()

        ListenerManager.bind_all_listeners()

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
