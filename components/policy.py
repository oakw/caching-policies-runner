import math
import random
from itertools import islice

class Policy:
    _victim_sample_proportion = 1.0

    def __init__(self, features, utility_model, ranker):
        self.features = features
        self.utility_model = utility_model
        self.ranker = ranker

    def set_victim_sample_proportion(self, victim_sample_proportion: float) -> None:
        vsp = float(victim_sample_proportion)
        if not (0.0 < vsp <= 1.0):
            raise ValueError("victim_sample_proportion must be in (0, 1]")
        self._victim_sample_proportion = vsp

    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        for f in self.features:
            f.on_access(key, timestamp, size=size, latency=latency)
        if hasattr(self.ranker, "on_access"):
            self.ranker.on_access(key, timestamp, size=size, latency=latency)

    def on_insert(self, key, timestamp):
        if hasattr(self.ranker, "on_insert"):
            self.ranker.on_insert(key, timestamp)

    def on_evict(self, key):
        if hasattr(self.ranker, "on_evict"):
            self.ranker.on_evict(key)

    def select_victims(self, key_pool: set, timestamp=None):
        if len(key_pool) == 0:
            return []

        if len(key_pool) == 1:
            return [next(iter(key_pool))]

        pool_size = len(key_pool)

        if self._victim_sample_proportion >= 1.0:
            candidates = key_pool
        else:
            sample_size = max(1, int(math.ceil(pool_size * self._victim_sample_proportion)))
            candidates = set(islice(random.sample(tuple(key_pool), sample_size), sample_size))

        utilities = {
            key: self.utility_model.compute(key, self.features, timestamp=timestamp) for key in candidates
        }

        return [self.ranker.select(utilities)]
