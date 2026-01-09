from abc import ABC, abstractmethod

class Feature(ABC):
    @abstractmethod
    def on_access(self, key, timestamp):
        pass

    @abstractmethod
    def value(self, key):
        pass
