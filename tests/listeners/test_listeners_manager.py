import pika
from mock import patch

class TestListenerManager:

    def test_add_with_one_listener(self, load_listener_test):
        from event_people import ListenerManager
        ListenerManager.add_listener(listener_class=load_listener_test, callback=None, event_name='resource.custom.pay')
        assert len(ListenerManager._listeners) == 1


    def test_add_listener_with_more(self, load_listener_test):
        from event_people import ListenerManager
        ListenerManager._listeners.clear()
        ListenerManager.add_listener(listener_class=load_listener_test, callback=None, event_name='resource.custom.pay')
        ListenerManager.add_listener(listener_class=load_listener_test, callback=None, event_name='resource.custom.service.all')
        assert len(ListenerManager._listeners) == 2

    def test_bind_all_listeners(self, load_listener_test):
        from event_people import ListenerManager
        ListenerManager._listeners.clear()
        listener_test, setup = load_listener_test
        ListenerManager.add_listener(listener_class=listener_test, callback=None, event_name='resource.custom.pay.service')
        ListenerManager.add_listener(listener_class=listener_test, callback=None, event_name='resource.custom.service.all')
        assert len(ListenerManager._listeners) == 2

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            ListenerManager.bind_all_listeners()