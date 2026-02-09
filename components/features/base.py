from abc import ABC, abstractmethod

class Feature(ABC):
    @abstractmethod
    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        pass

    @abstractmethod
    def value(self, key):
        pass
