from .base import Feature

class RecencyFeature(Feature):
    def __init__(self):
        self.last_access = {}

    def on_access(self, key, timestamp):
        self.last_access[key] = timestamp

    def value(self, key):
        return self.last_access.get(key, float("inf"))
