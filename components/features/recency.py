from .base import Feature

class RecencyFeature(Feature):
    def __init__(self):
        self.last_access = {}

    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        self.last_access[key] = timestamp

    def value(self, key):
        return self.last_access.get(key, float("inf"))
