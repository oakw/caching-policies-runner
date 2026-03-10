from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from .base import AdmissionPolicy
from components.features.frequency import FrequencyFeature


TinyLFUByteLatencyMode = Literal[
    "freq_times_size_times_latency",
    "freq_times_latency_over_size",
]


@dataclass
class TinyLFUByteLatencyAdmission(AdmissionPolicy):
    """
    Similar to TinyLFU but with latency-byte-awareness in the scoring and no windowed main cache.

    Maintains a sliding-window frequency estimator using `FrequencyFeature.recent_count`.

    On every request record the access.

    On miss, admit an object only if its score is higher than the score of the
    would-be victim (the victim chosen by the eviction policy).

    Latency-aware modes:
      - "freq_times_size_times_latency": freq * size * latency
      - "freq_times_latency_over_size": (freq * latency) / size

    Comparison type stays the same: admit iff incoming_score > victim_score.
    """

    window_size: int = 100_000
    mode: TinyLFUByteLatencyMode = "freq_times_size_times_latency"
    default_latency: float = 1.0
    latency_floor: float = 1e-9

    def __post_init__(self):
        self.window_size = int(self.window_size)
        if self.window_size <= 0:
            raise ValueError("window_size must be > 0")
        self._freq = FrequencyFeature()

        self.default_latency = float(self.default_latency)
        if self.default_latency <= 0:
            self.default_latency = 1.0

        self._last_access: tuple[int, int, int, float] | None = None  # (key, timestamp, size, latency)
        self._last_victim: tuple[int, int, float] | None = None  # (victim_key, victim_size, victim_latency)

    def on_access(self, key: int, timestamp: int, size: int, hit: bool, latency: float) -> None:
        self._freq.on_access(key, timestamp)

        if not hit:
            if latency <= 0:
                latency = float(self.default_latency)

            self._last_access = (int(key), int(timestamp), int(size), float(latency))
        else:
            self._last_access = None

        # Victim info is set by Cache before calling accept.

    def set_victim(self, victim_key: int, victim_size: int, victim_latency: float) -> None:
        """Called by Cache right before accept() when a miss requires eviction."""
        if victim_latency <= 0:
            victim_latency = float(self.default_latency)

        self._last_victim = (int(victim_key), int(victim_size), float(victim_latency))

    def accept(self, key: int, timestamp: int, size: int, latency: float = 0.0) -> bool:
        if self._last_victim is None:
            return True

        victim_key, victim_size, victim_latency = self._last_victim

        size = max(1, int(size))
        victim_size = max(1, int(victim_size))

        incoming_latency = max(float(self.latency_floor), float(latency))
        victim_latency = max(float(self.latency_floor), float(victim_latency))

        incoming_freq = self._freq.recent_count(int(key), int(timestamp), self.window_size)
        victim_freq = self._freq.recent_count(int(victim_key), int(timestamp), self.window_size)

        if self.mode == "freq_times_size_times_latency":
            incoming_score = float(incoming_freq) * float(size) * float(incoming_latency)
            victim_score = float(victim_freq) * float(victim_size) * float(victim_latency)

        elif self.mode == "freq_times_latency_over_size":
            incoming_score = (float(incoming_freq) * float(incoming_latency)) / float(size)
            victim_score = (float(victim_freq) * float(victim_latency)) / float(victim_size)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

        self._last_victim = None
        self._last_access = None

        return incoming_score > victim_score
