import signal
import sys

from event_people.config import Config
from event_people.listeners.listener_manager import ListenerManager

class Daemon:
    POLL_INTERVAL_SECONDS = 1

    @classmethod
    def start(cls):
        cls.bind_signals()

        broker = Config.get_broker()
        broker.get_connection()

        ListenerManager.bind_all_listeners()

        try:
            cls._consume(broker)
        except KeyboardInterrupt: #pragma: no cover
            broker.close_connection()#pragma: no cover

    @classmethod
    def _consume(cls, broker):
        """Serve every channel of the broker connection until it closes.

        Each listener consumes on its own channel, so the loop has to run on
        the connection: start_consuming() on a single channel only dispatches
        the consumers registered on that channel.
        """
        while broker.connection is not None and broker.connection.is_open:
            broker.connection.process_data_events(time_limit=cls.POLL_INTERVAL_SECONDS)

    @classmethod
    def stop(cls):
        """Close broker connection and terminate the process."""
        broker = Config.broker
        try:
            if broker is not None:
                broker.close_connection()
        finally:
            sys.exit(0)

    @classmethod
    def bind_signals(cls):
        """Trap SIGTERM and SIGINT for graceful shutdown."""
        signal.signal(signal.SIGTERM, lambda signum, frame: cls.stop())
        signal.signal(signal.SIGINT, lambda signum, frame: cls.stop())
