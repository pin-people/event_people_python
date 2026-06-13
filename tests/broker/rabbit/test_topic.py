import json
import pika
import pytest
from mock import patch, call


class TestTopic:

    def test_get_topic_with_channel(self, setup):
        from event_people import RabbitBroker
        from event_people import Topic

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Topic.get_topic(channel=channel)

    def test_get_topic_whithout_channel(self, setup):
        from event_people import Topic

        with pytest.raises(ValueError):
            Topic.get_topic(channel=None)

    def test_produce_topic_with_channel(self, setup):
        from event_people import RabbitBroker
        from event_people import Event
        from event_people import Topic

        body = { 'amount': 350, 'name': 'George' }
        event = Event(name='resource.custom.pay', body=body)
        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()
            Topic.produce(channel=channel, event=event)

    def test_produce_topic_without_channel(self, setup):
        from event_people import Event
        from event_people import Topic
        with pytest.raises(ValueError):
            body = { 'amount': 350, 'name': 'George' }
            event = Event(name='resource.custom.pay', body=body)
            Topic.produce(channel=None, event=event)

    def test_produce_uses_camelcase_header_keys(self, setup):
        """BUG-PY-001: Topic.produce must publish camelCase JSON keys, not snake_case.

        Spec requires headers JSON keys to be camelCase (appName, schemaVersion).
        Previously event.header.__dict__ emitted snake_case (app_name, schema_version).
        """
        from event_people import RabbitBroker, Event, Topic

        body = {'amount': 10}
        event = Event(name='resource.custom.pay', body=body)

        published_bodies = []

        with patch('{0}.broker.rabbit_broker.pika.BlockingConnection'.format(setup['basedir']), spec=pika.BlockingConnection):
            rabbit = RabbitBroker()
            channel = rabbit.get_connection()

            # Capture the body argument passed to basic_publish
            original_publish = channel.basic_publish
            def capturing_publish(**kwargs):
                published_bodies.append(kwargs.get('body', b''))
            channel.basic_publish = capturing_publish

            Topic.produce(channel=channel, event=event)

        assert len(published_bodies) == 1, "basic_publish should have been called once"
        payload = json.loads(published_bodies[0].decode('utf-8'))
        headers = payload['headers']

        # camelCase keys must be present
        assert 'appName' in headers, f"'appName' missing from headers: {list(headers.keys())}"
        assert 'schemaVersion' in headers, f"'schemaVersion' missing from headers: {list(headers.keys())}"

        # snake_case keys must NOT be present (this was the bug)
        assert 'app_name' not in headers, "'app_name' (snake_case) must not appear in headers"
        assert 'schema_version' not in headers, "'schema_version' (snake_case) must not appear in headers"

        # Values should be correct
        assert headers['appName'] == 'service_name'
        assert headers['schemaVersion'] == 1.0
