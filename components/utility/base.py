from abc import ABC, abstractmethod

class UtilityModel(ABC):
    @abstractmethod
    def compute(self, key, features, predictions=None):
        pass
