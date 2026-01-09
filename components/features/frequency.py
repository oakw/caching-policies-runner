from .base import Feature

class FrequencyFeature(Feature):
    def __init__(self):
        self.counts = {}

    def on_access(self, key, timestamp):
        self.counts[key] = self.counts.get(key, 0) + 1

    def value(self, key):
        return self.counts.get(key, 0)
