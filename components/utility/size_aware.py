from __future__ import annotations

from typing import Literal

from .base import UtilityModel


SizeUtilityMode = Literal["freq_over_size", "freq_times_size"]


class SizeAwareLFUUtility(UtilityModel):
    """Size-aware frequency-based utility."""

    def __init__(
        self,
        frequency_feature,
        storage,
        mode: SizeUtilityMode = "freq_over_size",
        size_floor: int = 1,
    ):
        self.frequency_feature = frequency_feature
        self.storage = storage
        self.mode = mode
        self.size_floor = max(1, int(size_floor))

    def compute(self, key, features, predictions=None, timestamp=None):
        freq = float(self.frequency_feature.value(key))

        size = self.size_floor
        data = getattr(self.storage, "data", None)
        if isinstance(data, dict) and key in data:
            try:
                size = int(data[key])
            except Exception:
                size = self.size_floor

        if size <= 0:
            size = self.size_floor

        # supports two modes
        if self.mode == "freq_over_size":
            return freq / float(size)
        if self.mode == "freq_times_size":
            return freq * float(size)

        raise ValueError(f"Unknown size utility mode: {self.mode}")
