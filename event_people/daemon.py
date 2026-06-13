import signal
import sys

from event_people.config import Config
from event_people.listeners.listener_manager import ListenerManager

class Daemon:
    @classmethod
    def start(cls):
        cls.bind_signals()

        channel = Config.get_broker().get_connection()

        ListenerManager.bind_all_listeners()

        try:
            channel.start_consuming()
        except KeyboardInterrupt: #pragma: no cover
            channel.stop_consuming()##pragma: no cover

    @classmethod
    def stop(cls):
        """Close broker connection and terminate the process."""
        broker = Config.broker
        if broker is not None:
            broker.close_connection()
        sys.exit(0)

    @classmethod
    def bind_signals(cls):
        """Trap SIGTERM and SIGINT for graceful shutdown."""
        signal.signal(signal.SIGTERM, lambda signum, frame: cls.stop())
        signal.signal(signal.SIGINT, lambda signum, frame: cls.stop())
