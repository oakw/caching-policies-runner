class State:
    def __init__(self, storage=None):
        self.storage = storage

        self.hit_count = 0
        self.miss_count = 0
        self.access_count = 0
        self.last_timestamp = 0
        self.hit_object_size_sum = 0
        self.hit_response_time_sum = 0.0

    @property
    def capacity(self):
        return getattr(self.storage, "capacity", 0)

    @property
    def current_size(self):
        if hasattr(self.storage, "data"):
            return sum(self.storage.data.values())
        return 0

    def on_access(self, key: int, timestamp: int, hit: bool, object_size: int, response_time: float):
        self.access_count += 1
        self.last_timestamp = timestamp
        if hit:
            self.hit_count += 1
            self.hit_object_size_sum += object_size
            self.hit_response_time_sum += response_time
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
            "hit_object_size_sum": self.hit_object_size_sum,
            "hit_response_time_sum": self.hit_response_time_sum
        }

    def __repr__(self):
        return (f"State(capacity={self.capacity}, current_size={self.current_size}, "
                f"hit_count={self.hit_count}, miss_count={self.miss_count}, "
                f"access_count={self.access_count}, last_timestamp={self.last_timestamp}, "
                f"hit_object_size_sum={self.hit_object_size_sum}, "
                f"hit_response_time_sum={self.hit_response_time_sum})")