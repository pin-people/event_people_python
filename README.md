# EventPeople


EventPeople is a tool to simplify the communication of services based on events. It is an extension of the [Pika](https://github.com/pika/pika) library.

The main idea is to provide a tool that can emit or consume events based on its names, the event name has 4 words (`resource.origin.action.destiny`) which defines some important info about what kind of event it is, where it comes from and who is eligible to consume it:

- **resource:** Defines which resource this event is related like a `user`, a `product`, `company` or anything that you want;
- **origin:** Defines the name of the system which emitted the event;
- **action:** What action is made on the resource like `create`, `delete`, `update`, etc. PS: *It is recommended to use the Semple Present tense for actions*;
- **destiny (Optional):** This word is optional and if not provided EventPeople will add a `.all` to the end of the event name. It defines which service should consume the event being emitted, so if it is defined and there is a service whith the given name only this service will receive it. It is very helpful when you need to re-emit some events. Also if it is `.all` all services will receive it.

As of today EventPeople uses RabbitMQ as its datasource, but there are plans to add support for other Brokers in the future.

## Installation

for instalattion execute the follow command

```python
  pip install event_people
```


And set env vars:
```python
ENV['RABBIT_URL'] = 'amqp://guest:guest@localhost:5672'
ENV['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'service_name'
ENV['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
ENV['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'event_people'
````

## Usage

### Events

The main component of `EventPeople` is the `Event` class which wraps all the logic of an event and whenever you receive or want to send an event you will use it.

It has 2 attributes `name` and `payload`:

- **name:** The name must follow our conventions, being it 3 (`resource.origin.action`) or 4 words (`resource.origin.action.destiny`);
- **payload:** It is the body of the massage, it should be a Hash object for simplicity and flexibility.

```python
from event_people.event import Event
from event_people.emmiter import Emitter

body = {'text': 'meu chefe é legal'}
e1 = Event(name='resource.origin.action', body=body, appName='EventPeopleExampleApp')

Emitter.trigger(e1)

```

There are 3 main interfaces to use `EventPeople` on your project:

- Calling `event_people.emmiter.Emitter.trigger(event)` inside your project;
- Calling `event_people.listener.Listener.on(event_name)` inside your project;
- Or extending `event_people.broker.base` and use it as a daemon.

### Using the Emitter
You can emit events on your project passing an `event_people.event.Event` instance to the `event_people.emitter.trigger` method. Doing this other services that are subscribed to these events will receive it.

```python
from event_people.event import Event
from event_people.emmiter import Emitter

event_name = 'receipt.payments.pay.users'
body = { amount: 350.76 }
event = Event(event_name, body)

Emitter.trigger(event)

```
[See more details](https://github.com/pin-people/event_people_python/blob/master/examples/emitter.rb)

### Listeners

You can subscribe to events based on patterns for the event names you want to consume or you can use the full name of the event to consume single events.

We follow the RabbitMQ pattern matching model, so given each word of the event name is separated by a dot (`.`), you can use the following symbols:

- `* (star):` to match exactly one word. Example `resource.*.*.all`;
- `# (hash):` to match zero or more words. Example `resource.#.all`.

Other important aspect of event consumming is the result of the processing we provide 3 methods so you can inform the Broker what to do with the event next:

- `success!:` should be called when the event was processed successfuly and the can be discarded;
- `fail!:` should be called when an error ocurred processing the event and the message should be requeued;
- `reject!:` should be called whenever a message should be discarded without being processed.

Given you want to consume a single event inside your project you can use the `EventPeople::Listener.on` method. It consumes a single event, given there are events available to be consumed with the given name pattern.

```python
from event_people.listener import Listener
from event_people.event import Event

os.environ["RABBIT_URL"] = "amqp://guest:guest@localhost:5672"
os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'EventPeopleExampleApp'
os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'topic1'


def callback_test(ch, method, properties, body) -> Event:
        print(" [x] %r:%r" % (method.routing_key, body))
        json_message = json.loads(body)
        header = json_message['header']
        name = header['resource'] + '.' + header['origin'] +  '.'  + header['action'] + '.' + header['destiny']
        result = Event(appName=header['app'], name=name ,body=json_message['body'])
        ch.basic_ack(delivery_tag= method.delivery_tag)


l = Listener.on(callback_test, 'resource.origin.action.all')
```

You can also receive listen (consume) messagem from more than one queues

```python
from event_people.listener import Listener
from event_people.event import Event

os.environ["RABBIT_URL"] = "amqp://guest:guest@localhost:5672"
os.environ['RABBIT_EVENT_PEOPLE_APP_NAME'] = 'EventPeopleExampleApp'
os.environ['RABBIT_EVENT_PEOPLE_VHOST'] = 'event_people'
os.environ['RABBIT_EVENT_PEOPLE_TOPIC_NAME'] = 'topic1'

result = None
def callback_test(ch, method, properties, body) -> Event:
        print(" [x] %r:%r" % (method.routing_key, body))
        json_message = json.loads(body)
        header = json_message['header']
        name = header['resource'] + '.' + header['origin'] +  '.'  + header['action'] + '.' + header['destiny']
        result = Event(appName=header['app'], name=name ,body=json_message['body'])
        ch.basic_ack(delivery_tag= method.delivery_tag)


Listener.on(callback_test,'resource.origin.action.all', 'resource.origin1.action2.all')

```
[See more details](https://github.com/pin-people/event_people_python/blob/master/examples/listener_multiple_events)


## Development

After checking out the repo, run `bin/setup` to install dependencies. Then, run `bundle exec rspec` to run the tests. You can also run `bin/console` for an interactive prompt that will allow you to experiment.

To install this gem onto your local machine, run `bundle exec rake install`.

## Contributing

- Fork it
- Create your feature branch (`git checkout -b my-new-feature`)
- Commit your changes (`git commit -am 'Add some feature'`)
- Push to the branch (`git push origin my-new-feature`)
- Create new Pull Request

## License

The gem is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
