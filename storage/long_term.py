"""Long-term memory using SQLite or PostgreSQL."""


class DatabaseMemory:
    def __init__(self, url="sqlite:///memory.db"):
        self.url = url
        # TODO: initialize database connection

    def fetch(self, query, *params):
        # TODO: query database
        pass

    def store(self, data):
        # TODO: persist data
        pass
