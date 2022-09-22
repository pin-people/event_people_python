class Base:

    def __init__(self,channel, delivery_info) -> None:
        self.channel = channel
        self.delivery_info = delivery_info

    def sucess(self):
        self.channel.basic_ack(delivery_tag= 1)

    def fail(self):
        self.channel.basic_ack(delivery_tag=1)

    def reject(self):
        self.channel.basic_ack(delivery_tag=1)