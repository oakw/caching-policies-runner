from .base import Feature

class RecencyFeature(Feature):
    def __init__(self):
        self.last_access = {}
        self._sorted_last_accesses: list[tuple[int, int]] = []

    def on_access(self, key, timestamp):
        if key in self.last_access:
            self._sorted_last_accesses.remove((key, self.last_access[key]))

        self.last_access[key] = timestamp
        self._sorted_last_accesses.append((key, timestamp))

    def value(self, key):
        return self.last_access.get(key, float("inf"))

    # First - least recently used
    def sorted_keys(self):
        yield from (key for key, _ in self._sorted_last_accesses)