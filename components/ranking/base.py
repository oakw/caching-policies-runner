from abc import ABC, abstractmethod

class Ranker(ABC):
    @abstractmethod
    def select(self, utilities):
        pass
