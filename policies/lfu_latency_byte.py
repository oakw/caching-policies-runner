from __future__ import annotations

from typing import Literal

from components.core.storage import Storage
from components.features.frequency import FrequencyFeature
from components.features.latency import LatencyFeature
from components.policy import Policy
from components.ranking.min_utility import MinUtilityRanker
from components.utility.freq_size_latency import FreqSizeLatencyUtility


LatencyByteMode = Literal[
    "freq_over_size_times_latency",
    "freq_times_latency_over_size",
]

def LFU_LatencyByte(
    storage: Storage,
    mode: LatencyByteMode = "freq_over_size_times_latency",
    default_latency: float = 1.0,
):
    """
    LFU eviction extended with latency + size-aware utility.
    """

    freq = FrequencyFeature()
    latency = LatencyFeature(default_latency=default_latency)

    utility = FreqSizeLatencyUtility(
        freq_feature=freq,
        latency_feature=latency,
        storage=storage,
        mode=mode,
    )
    ranker = MinUtilityRanker()

    return Policy([freq, latency], utility, ranker)
