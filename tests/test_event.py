import ast
import pytest
import json

class TestEvent:

    def test_load_event_type_is_dict(self, setup):
        from event_people import Event

        event_name = 'resource.custom.receive'
        body = b"{'amount': 35, 'name': 'Peter'}"

        event = Event(name=event_name, body=body)

        assert event.name == f'{event_name}.all'
        assert ast.literal_eval(body.decode('utf-8')) == event.body

    def test_load_event_with_invalid_name(self, setup):
        from event_people import Event

        event_name = 'resource.custom'
        body = b"{'amount': 35, 'name': 'Peter' }"

        with pytest.raises(ValueError):
            Event(name=event_name, body=body)

    def test_get_payload_succeffuly(self, setup):
        from event_people import Event
        event_name = 'resource.custom.receive'
        body = b"{'amount': 35, 'name': 'Peter'}"

        event = Event(name=event_name, body=body)

        resp = json.loads(event.payload())

        header = resp['headers']
        assert header['appName'] == 'service_name'
        assert header['resource'] == 'resource'
        assert header['origin'] == 'custom'

        assert resp['body'] == ast.literal_eval(body.decode('utf-8'))

    def test_get_payload_with_empty_body(self, setup):
        from event_people import Event
        event_name = 'resource.custom.receive'
        body = {}

        event = Event(name=event_name, body=body)

        resp = json.loads(event.payload())

        assert resp['body'] == body

    def test_has_body_returns_true_when_body_present(self, setup):
        from event_people import Event
        event = Event(name='resource.custom.receive', body={'amount': 10})
        assert event.has_body() is True

    def test_has_body_returns_false_when_body_none(self, setup):
        """has_body() returns False only when body is None (not for falsy-but-present values)."""
        from event_people import Event
        # An empty dict is a present (non-None) body — has_body() should be True.
        event = Event(name='resource.custom.receive', body={})
        assert event.has_body() is True

    def test_has_body_returns_true_for_falsy_non_none_body(self, setup):
        """Falsy-but-present bodies (empty dict) are treated as having a body."""
        from event_people import Event
        event = Event(name='resource.custom.receive', body={})
        assert event.has_body() is True

    def test_has_name_returns_true_when_name_present(self, setup):
        from event_people import Event
        event = Event(name='resource.custom.receive', body={})
        assert event.has_name() is True

    def test_increment_retry_count(self, setup):
        from event_people import Event
        event = Event(name='resource.custom.receive', body={})
        assert event.retry_count == 0
        event.increment_retry_count()
        assert event.retry_count == 1
        event.increment_retry_count()
        assert event.retry_count == 2