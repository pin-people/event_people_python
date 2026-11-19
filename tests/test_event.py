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
        event = Event(name='resource.custom.receive', body=None)
        assert event.has_body() is False

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
    def test_json_payload_with_null_true_false_is_parsed(self, setup):
        """Inbound payloads are JSON: null, true and false must be read."""
        from event_people import Event
        body = b'{"id": 42, "deleted_at": null, "active": true, "archived": false}'

        event = Event(name='resource.custom.receive', body=body)

        assert event.body == {'id': 42, 'deleted_at': None, 'active': True, 'archived': False}

    def test_json_envelope_is_unwrapped_to_its_body(self, setup):
        """A payload built by Event.payload() round-trips to the same body."""
        from event_people import Event
        sent = Event(name='resource.custom.receive', body={'id': 42, 'deleted_at': None})

        received = Event(name='resource.custom.receive', body=sent.payload().encode('utf-8'))

        assert received.body == {'id': 42, 'deleted_at': None}

    def test_json_payload_given_as_text_is_parsed(self, setup):
        from event_people import Event

        event = Event(name='resource.custom.receive', body='{"amount": 35, "paid": true}')

        assert event.body == {'amount': 35, 'paid': True}

    def test_python_literal_payload_is_still_accepted(self, setup):
        """Payloads written as a Python literal by older emitters keep working."""
        from event_people import Event

        event = Event(name='resource.custom.receive', body=b"{'amount': 35, 'paid': True}")

        assert event.body == {'amount': 35, 'paid': True}

    def test_unreadable_payload_raises(self, setup):
        import pytest
        from event_people import Event

        with pytest.raises((ValueError, SyntaxError)):
            Event(name='resource.custom.receive', body=b'not a payload {')
