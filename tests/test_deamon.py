import signal
import sys
from unittest.mock import patch, MagicMock

class TestDeamon:

    @staticmethod
    def _broker_serving(cycles):
        """Broker double whose connection stays open for `cycles` polls."""
        broker = MagicMock()
        polls = []

        def process_data_events(time_limit=None):
            polls.append(time_limit)
            if len(polls) >= cycles:
                broker.connection.is_open = False

        broker.connection.is_open = True
        broker.connection.process_data_events.side_effect = process_data_events

        return broker, polls

    def test_start_serves_the_connection_until_it_closes(self, setup):
        """Daemon.start must pump the connection, not a single channel."""
        from event_people import Daemon
        from event_people.config import Config

        broker, polls = self._broker_serving(cycles=3)
        original_broker = Config.broker
        try:
            Config.broker = broker

            with patch('signal.signal'), \
                 patch('event_people.daemon.ListenerManager.bind_all_listeners') as bind:
                Daemon.start()
        finally:
            Config.broker = original_broker

        bind.assert_called_once()
        assert polls == [Daemon.POLL_INTERVAL_SECONDS] * 3
        broker.get_connection.return_value.start_consuming.assert_not_called()

    def test_start_opens_the_connection_before_binding_listeners(self, setup):
        from event_people import Daemon
        from event_people.config import Config

        broker, _ = self._broker_serving(cycles=1)
        calls = []
        broker.get_connection.side_effect = lambda: calls.append('connect')
        original_broker = Config.broker
        try:
            Config.broker = broker

            with patch('signal.signal'), \
                 patch('event_people.daemon.ListenerManager.bind_all_listeners',
                       side_effect=lambda: calls.append('bind')):
                Daemon.start()
        finally:
            Config.broker = original_broker

        assert calls == ['connect', 'bind']

    def test_start_returns_when_the_connection_is_already_closed(self, setup):
        from event_people import Daemon
        from event_people.config import Config

        broker = MagicMock()
        broker.connection.is_open = False
        original_broker = Config.broker
        try:
            Config.broker = broker

            with patch('signal.signal'), \
                 patch('event_people.daemon.ListenerManager.bind_all_listeners'):
                Daemon.start()
        finally:
            Config.broker = original_broker

        broker.connection.process_data_events.assert_not_called()

    def test_bind_signals_registers_sigterm_and_sigint(self, setup):
        """Daemon.bind_signals must register handlers for SIGTERM and SIGINT."""
        from event_people import Daemon

        registered = {}
        original_signal = signal.signal

        def capturing_signal(sig, handler):
            registered[sig] = handler

        with patch('signal.signal', side_effect=capturing_signal):
            Daemon.bind_signals()

        assert signal.SIGTERM in registered, "SIGTERM handler not registered"
        assert signal.SIGINT in registered, "SIGINT handler not registered"

    def test_stop_closes_broker_and_exits(self, setup):
        """Daemon.stop must close the broker connection and call sys.exit(0)."""
        from event_people import Daemon
        from event_people.config import Config

        mock_broker = MagicMock()
        original_broker = Config.broker
        try:
            Config.broker = mock_broker

            with patch('sys.exit') as mock_exit:
                Daemon.stop()

            mock_broker.close_connection.assert_called_once()
            mock_exit.assert_called_once_with(0)
        finally:
            Config.broker = original_broker

    def test_stop_with_no_broker_still_exits(self, setup):
        """Daemon.stop must call sys.exit(0) even when no broker is set."""
        from event_people import Daemon
        from event_people.config import Config

        original_broker = Config.broker
        try:
            Config.broker = None

            with patch('sys.exit') as mock_exit:
                Daemon.stop()

            mock_exit.assert_called_once_with(0)
        finally:
            Config.broker = original_broker

