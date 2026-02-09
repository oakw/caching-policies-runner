from __future__ import annotations

from .base import Feature


class LatencyFeature(Feature):
    """Tracks latency (response time) per key.

    Stores the last observed latency for the object.
    """

    def __init__(self, default_latency: float = 1.0):
        self.default_latency = float(default_latency) if default_latency > 0 else 1.0
        self.last_latency: dict[int, float] = {}

    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        try:
            latency = float(latency)
        except Exception:
            latency = self.default_latency

        if latency <= 0:
            latency = self.default_latency

        self.last_latency[int(key)] = latency

    def value(self, key):
        return float(self.last_latency.get(int(key), self.default_latency))
