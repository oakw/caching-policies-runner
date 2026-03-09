from dataclasses import dataclass
from .base import UtilityModel

@dataclass
class FreqSizeLatencyUtility(UtilityModel):
    """Utility combining frequency, size, and latency.

    Variants:
      - "freq_times_size_times_latency": freq * size * latency
      - "freq_times_latency_over_size": (freq * latency) / size

    `freq_feature.value(key)` must return a frequency-like number.
    `latency_feature.value(key)` must return a latency > 0.

    Size is taken from storage if available; otherwise `size_floor`.
    """

    freq_feature: any
    latency_feature: any
    storage: any
    mode: str = "freq_times_size_times_latency"
    size_floor: int = 1
    latency_floor: float = 1e-9

    def compute(self, key, features, predictions=None, timestamp=None):
        freq = float(self.freq_feature.value(key))
        lat = float(self.latency_feature.value(key))
        if lat <= 0:
            lat = float(self.latency_floor)

        size = self.size_floor
        data = getattr(self.storage, "data", None)
        if isinstance(data, dict) and key in data:
            try:
                size = int(data[key])
            except Exception:
                size = self.size_floor
        if size <= 0:
            size = self.size_floor

        if self.mode == "freq_times_size_times_latency":
            return freq / (float(size) * float(lat))
        if self.mode == "freq_times_latency_over_size":
            return (freq * float(lat)) / float(size)

        raise ValueError(f"Unknown mode: {self.mode}")
