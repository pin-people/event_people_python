class Base:
    connection = None
    consumers = []

    def get_consumers(self):
        return self.consumers

    def get_connection(self):
        raise NotImplementedError('Must be implemented')

    @classmethod
    def consume(cls, event_name, callback):
        if(cls.consumers[event_name]):
            return cls.consumers[event_name]

        cls.consumers[event_name] = cls().consume(event_name, callback)

    def consume(self, event_name, callback):
        raise NotImplementedError('Must be implemented')

    @classmethod
    def produce(cls, events):
        cls().produce(events)

    def produce(self, events):
        raise NotImplementedError('Must be implemented')

    def close_connection(cls):
        raise NotImplementedError('Must be implemented')
