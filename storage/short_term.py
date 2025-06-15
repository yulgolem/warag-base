"""Short-term memory using Redis."""

class RedisMemory:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        # TODO: initialize Redis connection

    def get(self, key):
        # TODO: fetch value
        pass

    def set(self, key, value):
        # TODO: store value
        pass
