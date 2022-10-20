import mock
from pika.spec import Basic

class TestContext:

    @mock.patch('pika.BlockingConnection')
    def test_context_sucess_message(self, connection, setup):
        from event_people import Context
        delivery_tag = Basic.Deliver('consumer_tag_')
        context = Context(connection, delivery_tag)
        context.success()

    @mock.patch('pika.BlockingConnection')
    def test_context_reject_message(self, connection, setup):
        from event_people.broker.rabbit.context import Context
        delivery_tag = Basic.Deliver('consumer_tag_')
        context = Context(connection, delivery_tag)
        context.reject()

    @mock.patch('pika.BlockingConnection')
    def test_context_fail_message(self, connection, setup):
        from event_people.broker.rabbit.context import Context
        delivery_tag = Basic.Deliver('consumer_tag_')
        context = Context(connection, delivery_tag)
        context.fail()
