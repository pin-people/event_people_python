from mock import patch
import pika

class TestEmitter:

    def test_with_one_event(self):
        from emitter import Emitter
        from event import Event
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            body = { 'amount': 350, 'name': 'George' }
            event = Event(name='resource.custom.pay', body=body)
            Emitter.trigger(event)

    def test_with_more_than_one_event(self):
        from emitter import Emitter
        from event import Event
        events = []
        with patch('broker.rabbit_broker.pika.BlockingConnection', spec=pika.BlockingConnection):
            body = { 'amount': 350, 'name': 'George' }
            event1 = Event(name='resource.custom.pay', body=body)
            events.append(event1)

            body = { 'amount': 700, 'name': 'Barnie' }
            event2 = Event(name='resource.custom.pay.all', body=body)
            events.append(event2)
            Emitter.trigger(events)
