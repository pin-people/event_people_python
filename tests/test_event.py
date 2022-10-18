import ast
import pytest
import json

class TestEvent:

    def test_load_event_type_is_dict(self, setup):
        from event import Event

        event_name = 'resource.custom.receive'
        body = b"{'amount': 35, 'name': 'Peter' }"

        event = Event(name=event_name, body=body)

        assert event.name == f'{event_name}.all'
        assert ast.literal_eval(body.decode('utf-8')) == event.body

    def test_load_event_with_invalid_name(self, setup):
        from event import Event

        event_name = 'resource.custom'
        body = b"{'amount': 35, 'name': 'Peter' }"

        with pytest.raises(ValueError):
            event = Event(name=event_name, body=body)

    def test_get_pyload(self, setup):
        from event import Event
        event_name = 'resource.custom.receive'
        body = b"{'amount': 35, 'name': 'Peter' }"

        event = Event(name=event_name, body=body)

        resp = json.loads(event.payload())

        assert resp['header'] == 'service_name.resource.custom.receive.all.1.0'