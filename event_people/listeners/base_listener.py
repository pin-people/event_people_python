from event_people.config import Config
from event_people.listeners.listener_manager import ListenerManager

class BaseListener:
    def __init__(self, context):
        self._context = context

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
    def callback(cls, event, context, final_method_name):
        instance = cls(context)
        method = getattr(instance, final_method_name)

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
