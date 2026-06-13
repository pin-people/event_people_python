import pytest
import mock


class TestBaseListener:
    """Tests for BaseListener — including v1.2.0 class-level retry attributes."""

    def test_base_listener_default_retry_attrs_are_none(self, setup):
        """Class-level retry attrs default to None (defer to Config)."""
        from event_people import BaseListener
        assert BaseListener.max_attempts is None
        assert BaseListener.initial_delay is None
        assert BaseListener.delay_strategy is None
        assert BaseListener.dlq_name is None

    def test_resolve_retry_params_uses_config_defaults(self, setup):
        """When no class attrs set, _resolve_retry_params falls back to Config."""
        from event_people import BaseListener
        from event_people.config import Config

        params = BaseListener._resolve_retry_params()
        global_cfg = Config.get_retry_config()
        assert params['max_retries'] == global_cfg['max_attempts']
        assert params['initial_delay'] == global_cfg['initial_delay']
        assert params['delay_strategy'] == global_cfg['delay_strategy']
        assert params['dlq_name'] == global_cfg['dlq_name']

    def test_subclass_overrides_max_attempts(self, setup):
        """Listener subclass with max_attempts overrides Config default."""
        from event_people import BaseListener

        class MyListener(BaseListener):
            max_attempts = 7

        params = MyListener._resolve_retry_params()
        assert params['max_retries'] == 7

    def test_subclass_overrides_initial_delay(self, setup):
        from event_people import BaseListener

        class MyListener(BaseListener):
            initial_delay = 500

        params = MyListener._resolve_retry_params()
        assert params['initial_delay'] == 500

    def test_subclass_overrides_delay_strategy(self, setup):
        from event_people import BaseListener

        class MyListener(BaseListener):
            delay_strategy = 'fixed'

        params = MyListener._resolve_retry_params()
        assert params['delay_strategy'] == 'fixed'

    def test_subclass_overrides_dlq_name(self, setup):
        from event_people import BaseListener

        class MyListener(BaseListener):
            dlq_name = 'my_custom_dlq'

        params = MyListener._resolve_retry_params()
        assert params['dlq_name'] == 'my_custom_dlq'

    def test_subclass_partial_override(self, setup):
        """Only set attributes override Config; unset attrs fall back to Config."""
        from event_people import BaseListener
        from event_people.config import Config

        class MyListener(BaseListener):
            max_attempts = 10
            # initial_delay, delay_strategy, dlq_name not set

        params = MyListener._resolve_retry_params()
        global_cfg = Config.get_retry_config()
        assert params['max_retries'] == 10
        assert params['initial_delay'] == global_cfg['initial_delay']
        assert params['delay_strategy'] == global_cfg['delay_strategy']
        assert params['dlq_name'] == global_cfg['dlq_name']

    def test_callback_injects_context_as_instance_attr(self, setup):
        """BaseListener.callback must set self.context before calling handler."""
        from event_people import BaseListener, Event

        received = {}

        class MyListener(BaseListener):
            def handle(self, event):
                received['context'] = self.context
                received['event'] = event

        event = Event('resource.custom.receive.all', {'key': 'val'})
        ctx = mock.MagicMock()
        MyListener.callback('handle', event, ctx)

        assert received['context'] is ctx
        assert received['event'] is event

    def test_success_delegates_to_context(self, setup):
        from event_people import BaseListener

        ctx = mock.MagicMock()
        listener = BaseListener(ctx)
        listener.success()
        ctx.success.assert_called_once()

    def test_fail_delegates_to_context(self, setup):
        from event_people import BaseListener

        ctx = mock.MagicMock()
        listener = BaseListener(ctx)
        listener.fail()
        ctx.fail.assert_called_once()

    def test_reject_delegates_to_context(self, setup):
        from event_people import BaseListener

        ctx = mock.MagicMock()
        listener = BaseListener(ctx)
        listener.reject()
        ctx.reject.assert_called_once()

    def test_fixed_event_name_three_parts(self, setup):
        from event_people import BaseListener
        result = BaseListener.fixed_event_name('resource.custom.pay', 'all')
        assert result == 'resource.custom.pay.all'

    def test_fixed_event_name_four_parts(self, setup):
        from event_people import BaseListener
        result = BaseListener.fixed_event_name('resource.custom.pay.all', 'service_name')
        assert result == 'resource.custom.pay.service_name'
