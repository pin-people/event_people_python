class Topic:
    """ Queue wrappper for python user"""
    EXCHANGE_TYPE = 'topic'

    def __init__(self, channel):
        if channel is None:
            raise ValueError("Channel must be defined.")

        self._channel = channel

    def get_topic(cls, channel):
        cls(channel).get_topic()

    def get_topic(self):
        self._channel.exchange_declare(
            Config.TOPIC_NAME, self.exchange_type=EXCHANGE_TYPE, passive=True, durable=True)

        return self

    def produce(cls, channel, event):
        cls(channel).produce(event)

    def produce(self, event):
        topic = self.get_topic()

        topic.basic_publish(Config.TOPIC_NAME, event.name, event.body)
