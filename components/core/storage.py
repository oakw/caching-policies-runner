class Storage:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = set()

    def contains(self, key):
        return key in self.data

    def insert(self, key):
        self.data.add(key)

    def evict(self, key):
        self.data.remove(key)

    def is_full(self):
        return len(self.data) >= self.capacity

    def keys(self):
        return list(self.data)
