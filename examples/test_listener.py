import os
import sys

os.environ['RABBIT_URL'] = 'amqp://guest:guest@localhost:5672'
os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'service_name'
os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'event_people'

sys.path.insert(0, 'event_people')

from listener import Listener
##from event_people import Listener

def callback(event, context):
  print(event.name)
  print(event.header)
  print(event.body)
  context.success()

Listener.on('resource.origin.action', callback)


