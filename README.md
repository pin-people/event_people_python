# EventPeople

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/pin-people/event_people_python/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/pin-people/event_people_python/tree/main)

EventPeople is a tool to simplify the communication of event based services. It is an based on the [EventBus](https://github.com/EmpregoLigado/event_bus_rb) gem.

The main idea is to provide a tool that can emit or consume events based on its names, the event name has 4 words (`resource.origin.action.destination`) which defines some important info about what kind of event it is, where it comes from and who is eligible to consume it:

- **resource:** Defines which resource this event is related like a `user`, a `product`, `company` or anything that you want;
- **origin:** Defines the name of the system which emitted the event;
- **action:** What action is made on the resource like `create`, `delete`, `update`, etc. PS: *It is recommended to use the Simple Present tense for actions*;
- **destination (Optional):** This word is optional and if not provided EventPeople will add a `.all` to the end of the event name. It defines which service should consume the event being emitted, so if it is defined and there is a service whith the given name only this service will receive it. It is very helpful when you need to re-emit some events. Also if it is `.all` all services will receive it.

As of today EventPeople uses RabbitMQ as its datasource, but there are plans to add support for other Brokers in the future.

## Installation

Add this line to your project's `requirements.txt` file:

```text
event_people>=0.0.3
```

And then execute

```bash
python -m pip install -r requirements.txt
```

Or install it with:

```bash
python -m pip install event_people
```

And set env vars:
```bash
export RABBIT_URL='amqp://guest:guest@localhost:5672'
export RABBIT_EVENT_PEOPLE_APP_NAME='service_name'
export RABBIT_EVENT_PEOPLE_VHOST='event_people'
export RABBIT_EVENT_PEOPLE_TOPIC_NAME='event_people'
```

> **Note:** `RABBIT_EVENT_PEOPLE_MAX_RETRIES` and `RABBIT_EVENT_PEOPLE_RETRY_TTL_MS`
> were removed in v1.2.0. Retry settings are now configured via `Config.configure()`
> or per-listener class attributes — see the [Retry and DLQ](#retry-and-dead-letter-queue-dlq) section.

## Usage

### Events

The main component of `EventPeople` is the `Event` class which wraps all the logic of an event and whenever you receive or want to send an event you will use it.

It has 2 attributes `name` and `payload`:

- **name:** The name must follow our conventions, being it 3 (`resource.origin.action`) or 4 words (`resource.origin.action.destination`);
- **payload:** It is the body of the massage, it should be a Hash object for simplicity and flexibility.

```python
from event_people import Event
from event_people import Emitter

name = 'user.users.create'
body = { id: 42, name: 'John Doe', age: 35 }

event = Event(name, body)

```

There are 3 main interfaces to use `EventPeople` on your project:

- Calling `event_people.Emitter.trigger(event)` inside your project;
- Calling `event_people.Listener.on(event_name)` inside your project;
- Or extending `event_people.ListenersBase` and use it as a daemon.

### Using the Emitter
You can emit events on your project passing an `event_people.event.Event` instance to the `event_people.emitter.trigger` method. Doing this other services that are subscribed to these events will receive it.

```python
from event_people import Event
from event_people import Emitter

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

Given you want to consume a single event inside your project you can use the `event_people.Listener.on` method. It consumes a single event, given there are events available to be consumed with the given name pattern.

```python
from event_people import Listener
from event_people import Event


def callback_method(event, context):
    print("")
    print("  - Received the %r message from %r:", event.name, event.origin)
    print("     Message: %r", event.body)
    print("")

    context.success()


event_name = 'resource.origin.action.all'

Listener.on(event_name, callback_method)
```
[See more details](https://github.com/pin-people/event_people_python/blob/master/examples/listener.rb)

You can also receive all available messages using a loop:

```python
from event_people import Listener
from event_people import Event

has_events = true

def callback_method(event, context):
    has_events = true
    print("")
    print("  - Received the %r message from %r:", event.name, event.origin)
    print("     Message: %r", event.body)
    print("")

    context.success()


event_name = 'resource.origin.action.all'


while(has_events):
    has_events = false
    Listener.on(event_name, callback_method)
```

#### Multiple events routing

If your project needs to handle lots of events you can extend `eventPeople.ListenersBase` class to bind how many events you need to instance methods, so whenever an event is received the method will be called automatically.

```python
from event_people import ListenersBase
from event_people import Event

class CustomEventListener(Base):
    self.bind('resource.custom.pay', self.pay)
    self.bind('resource.custom.receive', self.receive)
    self.bind('resource.custom.private.service', self.private_channel)

    def pay(event):
        print("Paid %r for %r ~> %r", event.body['amount'], event.body['name'], event.name)

        self.success()

    def receive(event):
        if (event.body.amount > 500):
          print("Received %r from %r ~> %r", event.body['amount'], event.body['name'], event.name)
      else:
          print("[consumer] Got SKIPPED message")
          return self.reject()

          self.success();

  def private_channel(event):
    print("[consumer] Got a private message: \"%r\" ~> %r", event.body['message'], event.name)

    self.success();
```
[See more details](https://github.com/pin-people/event_people_python/blob/master/examples/daemon.rb)

#### Creating a Daemon

If you have the need to create a deamon to consume messages on background you can use the `eventPeople.Daemon.start` method to do so with ease. Just remember to define or import all the event bindings before starting the daemon.

```python
from event_people import Daemon
from event_people import BaseListener

class CustomEventListener(BaseListener):
    def pay(self, event):
        print(f"Paid {event.body['amount']} for {event.body['name']} ~> {event.name}")

        self.success()

    def receive(self, event):
        if event.body['amount'] > 500:
            print(f"Received {event.body['amount']} from {event.body['name']} ~> {event.name}")
        else:
            print('[consumer] Got SKIPPED message')

            return self.reject()

        self.success()

    def private_channel(self, event):
        print(f"[consumer] Got a private message: \"{event.body['message']}\" ~> {event.name}")

        self.success()

    def ignore_me(self, event):
        print(f"This should never be called...")
        print(f"Spying on other systems: \"{event.body['message']}\" ~> {event.name}")

        self.success()

CustomEventListener.bind_event('resource.*.pay', 'pay')
CustomEventListener.bind_event('resource.custom.receive', 'receive')
CustomEventListener.bind_event('resource.custom.private.service_name', 'private_channel')
CustomEventListener.bind_event('resource.custom.ignored.other_service', 'ignore_me')
CustomEventListener.bind_event('resource.custom.pay.all', 'receive')

print('****************** Daemon Ready ******************');

Daemon.start()
```
[See more details](https://github.com/pin-people/event_people_python/blob/master/examples/daemon.rb)

## Retry and Dead Letter Queue (DLQ)

### Configuration

Retry behaviour is configured in code — the old env vars
`RABBIT_EVENT_PEOPLE_MAX_RETRIES` and `RABBIT_EVENT_PEOPLE_RETRY_TTL_MS` were
removed in v1.2.0.

**Global defaults via `Config.configure()`** (optional — hardcoded defaults apply when not called):

```python
from event_people import Config

Config.configure({
    'max_attempts': 5,       # default: 3
    'initial_delay': 2000,   # base delay in ms, default: 1000
    'delay_strategy': 'exponential',  # 'exponential' or 'fixed', default: 'exponential'
    'dlq_name': 'my_dlq',   # default: '{appName}_dlq'
})
```

**Per-listener overrides** via class attributes (override Config defaults for that specific listener):

```python
from event_people import BaseListener

class OrderListener(BaseListener):
    max_attempts = 5
    initial_delay = 2000
    delay_strategy = 'exponential'

    def handle(self, event):
        try:
            process(event)
            self.success()
        except Exception:
            if self.context.is_last_retry:
                print("Final attempt failed, sending to DLQ")
            self.fail()

OrderListener.bind_event('order.service.created', 'handle')
```

### How it works

Dead-lettering is **application-level**: the main queue is declared without any
dead-letter argument, and the library **publishes** failed messages directly to a
plain `{appName}_dlq` queue (via the default exchange) and acks. There is no broker
dead-letter-exchange.

On `context.fail()`:
- If retries remain → message is published to `{queue}_retry` with backoff delay, then acked
- If retries exhausted → published to `{appName}_dlq` then acked (falls back to `nack(requeue=False)` if no DLQ is configured or the publish fails)
- If publish to retry queue fails (broker down) → `nack(requeue=False)` (never requeued to avoid infinite loops)

On `context.reject()` → published directly to `{appName}_dlq` then acked, no retries (falls back to `nack(requeue=False)` if no DLQ is configured or the publish fails)

**Delay strategies:**
- `exponential` (default): `min(initialDelay × 5^retryCount, 600000)` ms
- `fixed`: constant `initialDelay` ms

### Queue topology (auto-created on subscribe)

| Queue | Name | Purpose |
|---|---|---|
| Main queue | `{appName}-{routingKey}` | Declared argument-free (no dead-letter-exchange) |
| DLQ | `{appName}_dlq` | Plain durable queue; the library publishes failed messages to it |
| Retry queue | `{queue_name}_retry` | Holds messages until backoff delay expires, then routes back to the main queue |

### Migration from the broker-DLX version (not drop-in)

Versions ≤ 0.1.x declared the main queue **with** an immutable
`x-dead-letter-exchange = {appName}_dlx` argument (spec v1.1.0) plus a `{appName}_dlx`
fanout exchange and a bound `{appName}_dlq`. Upgrading to the application-level design
(this version) declares the main queue argument-free, which is **inequivalent** to the
existing queue — the first redeclare raises `PRECONDITION_FAILED`.

Upgrading is therefore **not drop-in**. Per environment, once:

1. Stop the consumer.
2. Delete the argument-bearing main queue(s). The `{appName}_dlx` fanout exchange and
   the broker-bound binding may also be removed; the plain `{appName}_dlq` queue can
   be kept.
3. Start the new consumer — it redeclares the main queue argument-free.

After this one-time cleanup all future upgrades are drop-in. See the platform
`COMPATIBILITY.md` (spec v1.1.0 → v1.1.1) for the full contract.

### Usage with `Listener.on`

```python
from event_people import Listener, Event

def handle_event(event: Event, context):
    print(f"Attempt {event.retry_count + 1} of {context.max_retries}")

    if event.body.get("invalid"):
        context.reject()   # → DLQ immediately, no retries
        return

    try:
        process(event)
        context.success()
    except Exception:
        if context.is_last_retry:
            print("Final attempt failed, sending to DLQ")
        context.fail()     # → retry queue (or DLQ if exhausted)

Listener.on("order.service.created", handle_event)
```

## Development

After checking out the repo, run `bin/setup` to install dependencies. Then, run `bin/test` to run the tests.

To install this package onto your local machine, run `python -m pip install -e .`.

## Contributing

- Fork it
- Create your feature branch (`git checkout -b my-new-feature`)
- Commit your changes (`git commit -am 'Add some feature'`)
- Push to the branch (`git push origin my-new-feature`)
- Create new Pull Request

## License

The package is available as open source under the terms of the [LGPL 3.0 License](https://www.gnu.org/licenses/lgpl-3.0.en.html).
