from abc import ABC, abstractmethod

class Adapter(ABC):
    @abstractmethod
    def observe(self, outcome):
        pass

    @abstractmethod
    def update(self):
        pass
