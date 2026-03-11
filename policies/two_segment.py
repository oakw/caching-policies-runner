from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict, OrderedDict
import math
import random


@dataclass
class TwoSegmentPolicy:
    """Two-segment eviction policy (probation + protected).

    - Probation: LRU (recency-based)
    - Protected: LFU (frequency-based)

    Items enter probation on insert.
    Promotion to protected happens only after the *second hit* (i.e., first hit while
    residing in probation).

    Eviction preference:
      1) Evict from probation first (LRU)
      2) If probation empty, evict from protected (LFU)

    Since this handles two segments, it is implemented using policy interface but does not extend it.
    """

    _victim_sample_proportion: float = 1.0
    protected_fraction: float = 0.5

    def __post_init__(self):
        if not (0.0 < float(self.protected_fraction) < 1.0):
            raise ValueError("protected_fraction must be in (0,1)")

        self._probation: OrderedDict[int, None] = OrderedDict()
        self._freq: dict[int, OrderedDict[int, None]] = defaultdict(OrderedDict)
        self._key_freq: dict[int, int] = {}
        self._min_freq: int = 1
        self._access_count: dict[int, int] = {}
        self._max_protected: int = 1

    def set_victim_sample_proportion(self, victim_sample_proportion: float) -> None:
        vsp = float(victim_sample_proportion)
        if not (0.0 < vsp <= 1.0):
            raise ValueError("victim_sample_proportion must be in (0, 1]")
        self._victim_sample_proportion = vsp

    def _recompute_limit(self) -> None:
        total = len(self._probation) + len(self._key_freq)
        self._max_protected = max(1, int(total * float(self.protected_fraction)))

    def on_insert(self, key: int, timestamp: int | None = None):
        self.on_evict(key)
        self._probation[key] = None
        self._access_count[key] = 0
        self._recompute_limit()

    def on_access(self, key: int, timestamp: int | None = None, size: int = 0, latency: float = 0.0):
        if key in self._probation:
            self._probation.move_to_end(key)
        elif key in self._key_freq:
            self._increase_freq(key)
        else:
            return

        self._access_count[key] = self._access_count.get(key, 0) + 1
        if key in self._probation and self._access_count[key] >= 2:
            self._promote(key)

    def on_evict(self, key: int):
        self._probation.pop(key, None)

        f = self._key_freq.pop(key, None)
        if f is not None:
            bucket = self._freq.get(f)
            if bucket is not None:
                bucket.pop(key, None)
                if not bucket:
                    self._freq.pop(f, None)
                    if self._min_freq == f:
                        self._min_freq = min(self._freq, default=1)

        self._access_count.pop(key, None)
        self._recompute_limit()

    def _sample(self, keys: list[int]) -> list[int]:
        if self._victim_sample_proportion >= 1.0 or len(keys) <= 1:
            return keys
        k = max(1, int(math.ceil(len(keys) * self._victim_sample_proportion)))
        return random.sample(keys, k)

    def select_victims(self, key_pool: set[int] | None = None, timestamp=None):
        if key_pool is None or not key_pool:
            raise ValueError("select_victims needs a non-empty key_pool")

        # prefer probation (LRU)
        candidates = [k for k in self._probation.keys() if k in key_pool]
        if candidates:
            sample = set(self._sample(candidates))
            for k in self._probation.keys():
                if k in sample:
                    return [k]
            raise RuntimeError("probation sample non-empty but no victim found")

        # else protected (LFU)
        prot_candidates = [k for k in self._key_freq.keys() if k in key_pool]
        if prot_candidates:
            sample = self._sample(prot_candidates)
            missing = [k for k in sample if k not in self._key_freq]
            if missing:
                raise RuntimeError(f"protected sample contains keys missing frequency: {missing[:5]}")
            victim = min(sample, key=lambda k: self._key_freq[k])
            return [victim]

        raise RuntimeError(
            "TwoSegmentPolicy state out of sync: no probation/protected key is in key_pool"
        )

    def _promote(self, key: int) -> None:
        if key not in self._probation:
            return
        self._probation.pop(key, None)

        f = 1
        self._key_freq[key] = f
        self._freq[f][key] = None
        self._min_freq = 1
        self._recompute_limit()
        self._ensure_protected_limit()

    def _increase_freq(self, key: int) -> None:
        f = self._key_freq[key]
        bucket = self._freq[f]
        bucket.pop(key, None)

        if not bucket:
            self._freq.pop(f, None)
            if self._min_freq == f:
                self._min_freq = min(self._freq, default=f + 1)

        f += 1
        self._key_freq[key] = f
        self._freq[f][key] = None

    def _ensure_protected_limit(self) -> None:
        # demote LFU victims until protected segment fits the limit.
        while len(self._key_freq) > self._max_protected and self._freq:
            victim = next(iter(self._freq[self._min_freq]))
            self._freq[self._min_freq].pop(victim, None)
            if not self._freq[self._min_freq]:
                self._freq.pop(self._min_freq, None)
                self._min_freq = min(self._freq, default=1)

            self._key_freq.pop(victim, None)
            self._probation[victim] = None
