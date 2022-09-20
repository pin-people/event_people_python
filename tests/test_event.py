import pytest
import json
import os

from pydantic.error_wrappers import ValidationError
from event_people.event import Header, Event, Body

class TestEvent:

   @pytest.fixture()
   def setUp(self):
        print("setup")
        os.environ["RABBIT_URL"] = "amqp://guest:guest@localhost:5672"
        os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'EventPeopleExampleApp'
        os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
        os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'topic1'

        yield "resource"
        print("teardown")


   def test_event_with_no_header(self):
      with pytest.raises(ValidationError):
         Header(app='event_people')

   def test_header_with_all_params(self):
      Header(app='event_app', resource='resource', origin='origin', action='action', destiny='destiny')

   def test_event_with_wrong_pattern_name_param(self):
      with pytest.raises(ValueError):
         e = Event(name='teste.teste', body={'response': 'id'})

   def test_event_with_correct_pattern_name_param(self):
      e = Event(name="resource.origin.action.destiny", body={'response': 'id'})

   def test_event_name_with_no_destiny(self):
      e = Event(name="resource.origin.action", body={'response': 'id'})
      assert e.header.destiny == 'all'

   def test_event_with_no_body(self):
      with pytest.raises(ValueError):
         e = Event(name="resource.origin.action", body=None)

   def test_event_with_correct_body_type(self):
      body = Body(message={'key': 'value'})
      assert isinstance(body.message, dict)

   def test_event_with_diferent_body_type(self):
      with pytest.raises(ValueError):
         body = Body(message=244)

   def test_event_get_json_payload(self):
      e = Event(name="resource.origin.action", body={'response': 384})
      assert e.payload() == '{"header": {"app": "event_people_app", "resource": "resource", "origin": "origin", "action": "action", "destiny": "all", "schema_version": 1.0}, "body": {"message": {"response": 384}}}'
      assert json.loads(e.payload())

   def test_event_return_payload_with_four_part_name(self):
      e = Event(name='resource.core.register.textanalysis', body={'response': 123})
      assert e.header.resource == 'resource'
      assert e.header.origin == 'core'
      assert e.header.action == 'register'
      assert e.header.destiny == 'textanalysis'

   def test_event_get_schema_version_from_body(self):
      e = Event("resource.core.register.textanalysis", {"schema_version": 1.2})
      assert e.header.schema_version == 1.2
