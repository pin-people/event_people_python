from config import Config
from .listener_manager import ListenerManager

class BaseListener:
    def __init__(self, context):
        self._context = context

    @classmethod
    def bind_event(cls, event_name, callback):
        if len(event_name.split('.')) == 3:
            app_name = Config.APP_NAME
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
                event_name=event_name
            )

    @classmethod
    def fixed_event_name(cls, event_name, postfix):
        routing_key = event_name
        splited = event_name.split('.')

        if len(splited) == 3:
            routing_key = f'{event_name}.{postfix}'

        return routing_key

    def callback(self, event, callback):
        callback(event, self._context)

    def success(self):
        self._context.success()

    def fail(self):
        self._context.fail()

    def reject(self):
        self._context.reject()
