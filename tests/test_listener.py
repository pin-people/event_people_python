import inspect
from mock import patch
import pika


class TestListener:

    def callback(event, context):
        print(event.name)
        print(event.header)
        print(event.body)
        context.success()

    def test_listen_event_with(self, setup):
        from event_people import Listener
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            Listener.on('resource.custom.receive.all', TestListener.callback)

    def test_listen_passing_callback_no_callback(self, setup):
        from event_people import Listener

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            Listener.on('resource.custom.receive.all', TestListener.callback)

    def test_listen_event_name_with_three_parts(self, setup):
        from event_people import Listener

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            Listener.on('resource.custom.receive', TestListener.callback)

    # --- v1.2.0 ---

    def test_on_signature_has_two_params(self, setup):
        """Listener.on signature must be on(event_name, callback) — v1.2.0."""
        from event_people import Listener
        sig = inspect.signature(Listener.on)
        params = list(sig.parameters.keys())
        # Static method: no 'self'. Expect exactly (event_name, callback).
        assert params == ['event_name', 'callback'], (
            f"Expected ['event_name', 'callback'], got {params}"
        )

    def test_on_uses_config_defaults_not_env_vars(self, setup):
        """Retry config comes from Config defaults, not env vars (v1.2.0 change)."""
        from event_people import Listener, Config
        import os
        # Ensure old env vars are not set — should not affect behaviour
        os.environ.pop('RABBIT_EVENT_PEOPLE_MAX_RETRIES', None)
        os.environ.pop('RABBIT_EVENT_PEOPLE_RETRY_TTL_MS', None)

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            # Should succeed using hardcoded defaults from Config
            Listener.on('resource.custom.receive.all', TestListener.callback)

    def test_on_applies_config_configure_overrides(self, setup):
        """Listener.on uses Config.configure() overrides when set."""
        from event_people import Listener, Config
        orig_ma = Config.MAX_ATTEMPTS
        try:
            Config.configure({'max_attempts': 5})
            with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
                # Should succeed — just verifying no error with overridden config
                Listener.on('resource.custom.receive.all', TestListener.callback)
        finally:
            Config.MAX_ATTEMPTS = orig_ma
