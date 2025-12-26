from abc import ABC, abstractmethod

class Window(ABC):
    @abstractmethod
    def update(self, event):
        pass

    @abstractmethod
    def project(self, raw_features):
        pass
