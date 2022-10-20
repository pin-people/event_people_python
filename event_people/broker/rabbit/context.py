class Context:
    """ Queue wrappper for python user"""
    def __init__(self, channel, delivery_info):
        self.channel = channel
        self.delivery_info = delivery_info

    def success(self):
        self.channel.basic_ack(self.delivery_info.delivery_tag)

    def fail(self):
        self.channel.basic_nack(self.delivery_info.delivery_tag, requeue=True)

    def reject(self):
        self.channel.basic_nack(self.delivery_info.delivery_tag, requeue=False)
