from event_people.config import Config
from event_people.listeners.listener_manager import ListenerManager

class BaseListener:
    """Base class for user-defined listener classes.

    Class-level retry attributes (all optional — fall back to Config defaults):
      max_attempts   — maximum retry attempts for this listener
      initial_delay  — base retry delay in ms for this listener
      delay_strategy — 'exponential' or 'fixed'
      dlq_name       — DLQ name for this listener

    Example::

        class OrderListener(BaseListener):
            max_attempts = 5
            initial_delay = 2000
            delay_strategy = 'exponential'

            def handle(self, event):
                process(event)
                self.success()

        OrderListener.bind_event('order.service.created', 'handle')
    """

    # Class-level retry overrides — subclasses may declare these.
    # Value of None means "use Config default".
    max_attempts = None
    initial_delay = None
    delay_strategy = None
    dlq_name = None

    def __init__(self, context):
        self.context = context
        # Keep backward-compatible private alias
        self._context = context

    @classmethod
    def _resolve_retry_params(cls):
        """Resolve retry config: listener class attributes > Config defaults."""
        global_config = Config.get_retry_config()
        return {
            'max_retries': cls.max_attempts if cls.max_attempts is not None else global_config['max_attempts'],
            'initial_delay': cls.initial_delay if cls.initial_delay is not None else global_config['initial_delay'],
            'delay_strategy': cls.delay_strategy if cls.delay_strategy is not None else global_config['delay_strategy'],
            'dlq_name': cls.dlq_name if cls.dlq_name is not None else global_config['dlq_name'],
        }

    @classmethod
    def bind_event(cls, event_name, callback):
        app_name = Config.APP_NAME
        if len(event_name.split('.')) <= 3:
            ListenerManager.add_listener(
                listener_class=cls,
                callback=callback,
                event_name=cls.fixed_event_name(event_name, 'all')
            )
            ListenerManager.add_listener(
                listener_class=cls,
                callback=callback,
                event_name=cls.fixed_event_name(event_name, app_name)
            )
        else:
            ListenerManager.add_listener(
                listener_class=cls,
                callback=callback,
                event_name=cls.fixed_event_name(event_name, app_name)
            )

    @classmethod
    def callback(cls, function, event, context=None):
        """Wrap broker delivery into Event + Context and dispatch to user method.

        Signature: ``callback(function, event, context)``
          - function: name of the handler method to call on this listener instance
          - event:    Event instance built from the broker delivery
          - context:  RabbitContext instance (injected by Queue._callback). Also
                      set as ``self.context`` on the listener instance before dispatch.

        Retry config is resolved from: listener class attributes > Config defaults.
        """
        instance = cls(context)
        method = getattr(instance, function)
        method(event)

    @classmethod
    def fixed_event_name(cls, event_name, postfix):
        routing_key = event_name
        splitted = event_name.split('.')

        if len(splitted) <= 3:
            routing_key = f'{event_name}.{postfix}'
        elif len(splitted) == 4:
            base_name = '.'.join(splitted[0:3])
            routing_key = f'{base_name}.{postfix}'

        return routing_key

    def success(self):
        self._context.success()

    def fail(self):
        self._context.fail()

    def reject(self):
        self._context.reject()
