class Storage:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = dict()

    def contains(self, key):
        return key in self.data

    def insert(self, key, size):
        self.data[key] = size

    def evict(self, key):
        del self.data[key]

    def is_full(self, next_insert_size = 0):
        return (sum(self.data.values()) + next_insert_size) >= self.capacity

    def keys(self):
        return list(self.data.keys())
