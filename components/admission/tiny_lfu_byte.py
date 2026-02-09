from __future__ import annotations

from dataclasses import dataclass

from .base import AdmissionPolicy
from components.features.frequency import FrequencyFeature


@dataclass
class TinyLFUByteAdmission(AdmissionPolicy):
    """
    Admission policy for byte caches. Similar to TinyLFU but with byte-awareness in the scoring and no windowed main cache.

    Maintains a sliding-window frequency estimator using `FrequencyFeature.recent_count`.

    On every request record the access.

    On miss, admit an object only if its score is higher than the score of the
    would-be victim (the victim chosen by the eviction policy).
    """

    window_size: int = 100_000

    def __post_init__(self):
        self.window_size = int(self.window_size)
        if self.window_size <= 0:
            raise ValueError("window_size must be > 0")
        self._freq = FrequencyFeature()

        # Stashed context for comparing incoming vs victim
        self._last_access: tuple[int, int, int] | None = None  # (key, timestamp, size)
        self._last_victim: tuple[int, int] | None = None  # (victim_key, victim_size)

    def on_access(self, key: int, timestamp: int, size: int, hit: bool) -> None:
        self._freq.on_access(key, timestamp)

        # For the subsequent accept() call on miss, remember the candidate.
        if not hit:
            self._last_access = (int(key), int(timestamp), int(size))
        else:
            self._last_access = None

        # Victim info is set by Cache before calling accept.

    def set_victim(self, victim_key: int, victim_size: int) -> None:
        """Called by Cache right before accept() when a miss requires eviction."""
        self._last_victim = (int(victim_key), int(victim_size))

    def accept(self, key: int, timestamp: int, size: int) -> bool:
        if self._last_victim is None:
            return True

        victim_key, victim_size = self._last_victim

        size = max(1, int(size))
        victim_size = max(1, int(victim_size))

        incoming_freq = self._freq.recent_count(int(key), int(timestamp), self.window_size)
        victim_freq = self._freq.recent_count(int(victim_key), int(timestamp), self.window_size)

        incoming_score = float(incoming_freq) / float(size)
        victim_score = float(victim_freq) / float(victim_size)

        self._last_victim = None
        self._last_access = None

        return incoming_score > victim_score
