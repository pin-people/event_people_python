from mock import patch
import pika

class TestRabbitBroker:

    def callback(event, context):
        print(event.name)
        print(event.header)
        print(event.body)
        context.success()

    def test_get_connection_ok(self, setup):
        from event_people import RabbitBroker

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            assert channel

    def test_get_connection_with_open_status(self,setup):
        from event_people import RabbitBroker

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection) as mocked_connection:
            mocked_connection.is_closed = False
            rabbit = RabbitBroker()
            rabbit.connection = mocked_connection
            channel = rabbit.get_connection()
            assert channel

    def test_consume_event(self, setup):
        from event_people import RabbitBroker
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            rabbit.consume('resource.custom.recieve.action', TestRabbitBroker.callback, False)

    def test_produce_list_events(self, setup):
        from event_people import RabbitBroker
        from event_people import Event
        events = []
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            event_name = 'resource.custom.receive'
            body = { 'amount': 350, 'name': 'George' }

            events.append(Event(event_name, body))

            event_name = 'resource.custom.receive'
            body = { 'amount': 550, 'name': 'James' }

            events.append(Event(event_name, body))

            event_name = 'resource.custom.private.service'
            body = { 'message': 'Secret' }

            events.append(Event(event_name, body))

            event_name = 'resource.origin.action'
            body = { 'bo': 'dy' }
            schema_version = 4.2

            events.append(Event(event_name, body, schema_version))

            rabbit.produce(events)

    def test_produce_unique_event(self, setup):
        from event_people import RabbitBroker
        from event_people import Event
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()

            event_name = 'resource.origin.action'
            body = { 'bo': 'dy' }
            schema_version = 4.2

            event = Event(event_name, body, schema_version)

            rabbit.produce(event)