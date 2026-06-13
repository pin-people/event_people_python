import signal
import sys
from unittest.mock import patch, MagicMock
import pika

class TestDeamon:

    def test_start_deamon(self, setup):
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            from event_people import Daemon
            Daemon.start()

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

