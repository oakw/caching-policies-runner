class Storage:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = dict()
        self.latencies = dict()
        self._used_capacity = 0

    def contains(self, key):
        return key in self.data

    def insert(self, key, size, latency=0.0):
        self.data[key] = size
        self.latencies[key] = latency
        self._used_capacity += size

    def evict(self, key):
        self._used_capacity -= self.data[key]
        del self.data[key]
        del self.latencies[key]

    def used_capacity(self):
        return self._used_capacity

    def is_full(self, next_insert_size = 0):
        return (self.used_capacity() + next_insert_size) >= self.capacity

    def keys(self):
        return set(self.data.keys())
