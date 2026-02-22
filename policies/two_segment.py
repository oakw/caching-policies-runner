from __future__ import annotations

from dataclasses import dataclass

from components.features.frequency import FrequencyFeature
from components.features.recency import RecencyFeature
from components.policy import Policy
from components.ranking.min_utility import MinUtilityRanker
from components.utility.simple import SimpleUtility
import math
import random
from itertools import islice


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

    Protected segment size is controlled by `protected_fraction` of total number of
    objects (not bytes), since `Storage` is byte-capacity based and not easily split.
    """

    _victim_sample_proportion: float = 1.0
    protected_fraction: float = 0.5

    def __post_init__(self):
        if not (0.0 < float(self.protected_fraction) < 1.0):
            raise ValueError("protected_fraction must be in (0, 1)")

        # Probation (LRU)
        self._prob_recency = RecencyFeature()
        self._prob_utility = SimpleUtility(self._prob_recency)
        self._prob_ranker = MinUtilityRanker()

        # Protected (LFU)
        self._prot_freq = FrequencyFeature()
        self._prot_utility = SimpleUtility(self._prot_freq)
        self._prot_ranker = MinUtilityRanker()

        # Segment membership
        self._probation: set[int] = set()
        self._protected: set[int] = set()

        # How many times a key has been accessed since last insert.
        # We only need to know when it reaches 2 (promotion gate).
        self._access_counts: dict[int, int] = {}

    def set_victim_sample_proportion(self, victim_sample_proportion: float) -> None:
        vsp = float(victim_sample_proportion)
        if not (0.0 < vsp <= 1.0):
            raise ValueError("victim_sample_proportion must be in (0, 1]")
        self._victim_sample_proportion = vsp

    def on_access(self, key: int, timestamp: int, size: int = 0, latency: float = 0.0):
        if key in self._probation:
            self._prob_recency.on_access(key, timestamp, size=size, latency=latency)
        if key in self._protected:
            self._prot_freq.on_access(key, timestamp, size=size, latency=latency)

        if key in self._probation or key in self._protected:
            self._access_counts[key] = self._access_counts.get(key, 0) + 1

            # Promote on second hit: inserted -> (miss) -> access_count==0 in cache,
            # first hit makes it 1, second hit makes it 2.
            if key in self._probation and self._access_counts[key] >= 2:
                self._promote_to_protected(key)

    def on_insert(self, key: int, timestamp: int):
        self._probation.add(key)
        self._protected.discard(key)

        self._access_counts[key] = 0
        self._prob_recency.on_access(key, timestamp)

    def on_evict(self, key: int):
        self._probation.discard(key)
        self._protected.discard(key)
        self._access_counts.pop(key, None)

    def select_victims(self, key_pool: set, timestamp=None):
        self._probation.intersection_update(key_pool)
        self._protected.intersection_update(key_pool)

        if self._victim_sample_proportion < 1.0:
            key_pool_size = max(1, int(math.ceil(len(key_pool) * self._victim_sample_proportion)))
            key_pool = set(islice(random.sample(tuple(key_pool), key_pool_size), key_pool_size))

        if self._probation:
            return [self._select_from_probation(timestamp)]

        if self._protected:
            return [self._select_from_protected(timestamp)]

        # if membership got out of sync, use LRU over key_pool
        # TODO: idk why this happens
        if not key_pool:
            return []
        tmp = Policy([self._prob_recency], self._prob_utility, self._prob_ranker)
        return tmp.select_victims(key_pool, timestamp=timestamp)

    def _select_from_probation(self, timestamp):
        utilities = {
            key: self._prob_utility.compute(key, [self._prob_recency], timestamp=timestamp)
            for key in self._probation
        }
        return self._prob_ranker.select(utilities)

    def _select_from_protected(self, timestamp):
        utilities = {
            key: self._prot_utility.compute(key, [self._prot_freq], timestamp=timestamp)
            for key in self._protected
        }
        return self._prot_ranker.select(utilities)

    def _promote_to_protected(self, key: int):
        if key not in self._probation:
            return
        self._probation.discard(key)
        self._protected.add(key)

        # Enforce protected segment size (object-count based).
        total = len(self._probation) + len(self._protected)
        if total <= 0:
            return

        max_protected = max(1, int(total * float(self.protected_fraction)))

        while len(self._protected) > max_protected:
            victim = self._select_from_protected(timestamp=None)
            # all is full, so demote to probation; do not reset access count
            self._protected.discard(victim)
            self._probation.add(victim)
