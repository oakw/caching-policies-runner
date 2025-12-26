class State:
    def __init__(self, storage=None):
        self.storage = storage

        self.hit_count = 0
        self.miss_count = 0
        self.access_count = 0
        self.last_timestamp = 0

    @property
    def capacity(self):
        return getattr(self.storage, "capacity", 0)

    @property
    def current_size(self):
        if hasattr(self.storage, "data"):
            return len(self.storage.data)
        return 0

    def on_access(self, key: int, timestamp: int, hit: bool):
        self.access_count += 1
        self.last_timestamp = timestamp
        if hit:
            self.hit_count += 1
        else:
            self.miss_count += 1

    def attach_to(self, cache):
        """Attach the state to a Cache to read storage-derived values."""
        self.storage = cache.storage
        return self

    def to_dict(self):
        return {
            "capacity": self.capacity,
            "current_size": self.current_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "access_count": self.access_count,
            "last_timestamp": self.last_timestamp,
        }