from abc import ABC, abstractmethod

class Ranker(ABC):
    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        pass

    def on_insert(self, key, timestamp):
        pass

    def on_evict(self, key):
        pass

    @abstractmethod
    def select(self, utilities):
        pass
