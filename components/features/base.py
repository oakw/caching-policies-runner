from abc import ABC, abstractmethod

class Feature(ABC):
    @abstractmethod
    def on_access(self, key, timestamp):
        pass

    @abstractmethod
    def value(self, key):
        pass

    @abstractmethod
    def sorted_keys(self):
        # Each feature can implement its own (efficient) way of returning sorted keys
        pass