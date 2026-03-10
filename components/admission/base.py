from abc import ABC, abstractmethod


class AdmissionPolicy(ABC):
    @abstractmethod
    def on_access(self, key: int, timestamp: int, size: int, hit: bool, latency: float = 0) -> None:
        """Observe every request, regardless of hit/miss."""

    @abstractmethod
    def accept(self, key: int, timestamp: int, size: int, latency: float = 0.0) -> bool:
        """Return True if the object should be admitted into the cache on this miss."""
