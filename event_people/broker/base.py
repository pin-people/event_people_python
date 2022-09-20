class Base:

    def get_connection(self):
        raise NotImplementedError('Must be implemented')

    def consumers(self):
        raise NotImplementedError('Must be implemented')

    def producer(self):
        raise NotImplementedError('Must be implemented')

    def close_connection():
        raise NotImplementedError('Must be implemented')
