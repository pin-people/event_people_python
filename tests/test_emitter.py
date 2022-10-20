
import pika
from mock import patch

class TestEmitter:

    def test_with_one_event(self, setup):
        from event_people import Emitter
        from event_people import Event
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            body = { 'amount': 350, 'name': 'George' }
            event = Event(name='resource.custom.pay', body=body)
            Emitter.trigger(event)

    def test_with_more_than_one_event(self, setup):
        from event_people import Emitter
        from event_people import Event
        events = []
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            body = { 'amount': 350, 'name': 'George' }
            event1 = Event(name='resource.custom.pay', body=body)
            events.append(event1)

            body = { 'amount': 700, 'name': 'Barnie' }
            event2 = Event(name='resource.custom.pay.all', body=body)
            events.append(event2)
            Emitter.trigger(events)
